"""
FastAPI dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..database import get_db
from ..services.auth_service import decode_token
from ..models import User
from ..api.schemas.user import TokenData
from sqlalchemy import select


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from the access token cookie.

    Args:
        access_token: JWT access token from HTTPOnly cookie
        db: Database session

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: 401 if not authenticated or token invalid
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token_data = decode_token(access_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    return user


def require_role(*allowed_roles):
    """
    Factory function to create a role-based authorization dependency.

    Args:
        *allowed_roles: Variable number of UserRole values that are allowed

    Returns:
        Callable: Dependency function that checks user role

    Usage:
        @app.get("/endpoint", dependencies=[Depends(require_role(UserRole.CREATOR))])
        Or:
        current_user: User = Depends(require_role(UserRole.MA, UserRole.CREATOR))
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
