"""
API routes for authentication operations.
"""
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from jose import JWTError, jwt

from ...config import settings
from ...database import get_db
from ...models.user import User, UserRole
from ...models.facility import Facility
from ...models.specialty import Specialty
from sqlalchemy.orm import selectinload
from ...api.dependencies import get_current_user
from ...api.schemas.user import UserLogin, UserCreate, UserInfo, LoginResponse
from ...services.auth_service import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token
)

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login"
)
async def login(
    credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and set HTTPOnly cookies.

    **Authentication Flow**: User provides username/password, receives access token in HTTPOnly cookie.

    Args:
        credentials: User login credentials (username/email and password)
        response: FastAPI response object to set cookies
        db: Database session

    Returns:
        LoginResponse: User information and success message

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    await db.commit()

    # Generate tokens
    access_token = create_access_token(user.id, user.username, user.role)
    refresh_token = create_refresh_token(user.id)

    # Set HTTPOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=15 * 60  # 15 minutes
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )

    return LoginResponse(
        user=UserInfo.model_validate(user),
        message="Login successful"
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout"
)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """
    Logout user by clearing HTTPOnly cookies.

    Args:
        response: FastAPI response object to clear cookies
        current_user: Authenticated user

    Returns:
        dict: Success message
    """
    # Clear cookies by setting max_age to 0
    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")

    return {"message": "Logout successful"}


@router.get(
    "/me",
    response_model=UserInfo,
    summary="Get current user information"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the currently authenticated user.

    Args:
        current_user: Authenticated user from dependency

    Returns:
        UserInfo: Current user information
    """
    return UserInfo.model_validate(current_user)


@router.post(
    "/register",
    response_model=UserInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    **Note**: In production, this endpoint should be restricted or require admin approval.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        UserInfo: Created user information

    Raises:
        HTTPException: 400 if username already exists
    """
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create new user
    user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserInfo.model_validate(user)


@router.get(
    "/sso",
    summary="SSO handshake from Synaptix",
)
async def sso_from_synaptix(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Accept a 60-second JWT minted by Synaptix's
    /api/v1/auth/sso/tribal-token endpoint, auto-provision the matching
    TribalCapturer user (by email == username), issue our own session
    cookies, and 302-redirect to SSO_LANDING_PATH.

    Token contract (HS256, signed with SYNAPTIX_SHARED_SECRET):
        iss = "synaptix"
        aud = "tribalcapturer"
        purpose = "sso-exchange"
        email, role, name (display name)

    Single use is enforced by the 60s exp window — replays past that
    point fail signature OR exp validation.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SYNAPTIX_SHARED_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience="tribalcapturer",
            issuer=settings.SYNAPTIX_ISSUER,
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"SSO token invalid: {e}",
        )

    if payload.get("purpose") != "sso-exchange":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token purpose",
        )

    email = (payload.get("email") or "").lower().strip()
    if not email:
        raise HTTPException(status_code=400, detail="Token missing email")

    display_name = payload.get("name") or email
    src_role = (payload.get("role") or "ma").lower()
    # Map Synaptix roles → TribalCapturer roles. Creator/admin both elevate
    # to Creator on this side; everything else is MA.
    tc_role = UserRole.CREATOR if src_role in ("creator", "admin") else UserRole.MA

    # Find or auto-provision the user by username (we use email as username
    # so identity is shared across the two systems). Eager-load assigned_*
    # so we can check whether to backfill facility/specialty access below.
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.assigned_facilities),
            selectinload(User.assigned_specialties),
        )
        .where(User.username == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            username=email,
            # Random hash — never used for login; SSO is the only path in.
            password_hash=hash_password(secrets.token_urlsafe(32)),
            full_name=display_name,
            role=tc_role,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user, attribute_names=["assigned_facilities", "assigned_specialties"])

    # Backfill RBAC: SSO-provisioned users initially have no facility or
    # specialty assignments, which blocks them from creating knowledge
    # entries. Until we wire per-user mapping from Synaptix, give them
    # everything — same scope as a Creator. Wrapped in try/except so any
    # ORM hiccup here does NOT prevent SSO from issuing the session
    # cookies and redirecting; the user just sees the assignment warning
    # in TribalCapturer until the backfill runs cleanly.
    try:
        if not user.assigned_facilities:
            all_facilities = (await db.execute(select(Facility))).scalars().all()
            user.assigned_facilities = list(all_facilities)
        if not user.assigned_specialties:
            all_specialties = (await db.execute(select(Specialty))).scalars().all()
            user.assigned_specialties = list(all_specialties)
    except Exception as e:
        import logging as _l
        _l.warning(f"SSO backfill of facility/specialty assignments failed for {email}: {e}")

    user.last_login = datetime.utcnow()
    try:
        await db.commit()
    except Exception as e:
        import logging as _l
        _l.warning(f"SSO commit failed for {email}: {e}")
        await db.rollback()

    # Issue TribalCapturer's own session, then redirect to home.
    access_token = create_access_token(user.id, user.username, user.role)
    refresh_token = create_refresh_token(user.id)

    redirect = RedirectResponse(url=settings.SSO_LANDING_PATH, status_code=302)
    redirect.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    redirect.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return redirect
