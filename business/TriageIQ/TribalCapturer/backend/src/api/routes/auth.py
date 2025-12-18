"""
API routes for authentication operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ...database import get_db
from ...models.user import User
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
