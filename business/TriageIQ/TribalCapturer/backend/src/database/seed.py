"""
Seed script to populate the database with test data for development.
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .connection import AsyncSessionLocal, engine, Base
from ..models.user import User, UserRole
from ..services.auth_service import hash_password


async def seed_users(db: AsyncSession):
    """Create test users if they don't already exist."""

    # Check if users already exist
    result = await db.execute(select(User))
    existing_users = result.scalars().all()

    if existing_users:
        print(f"Database already has {len(existing_users)} user(s). Skipping seed.")
        return

    # Create test users
    test_users = [
        User(
            username="ma1@tribaliq.com",
            password_hash=hash_password("TestPassword123!"),
            full_name="Sarah Johnson",
            role="MA"  # Use string literal to match database enum
        ),
        User(
            username="ma2@tribaliq.com",
            password_hash=hash_password("TestPassword123!"),
            full_name="Michael Chen",
            role="MA"  # Use string literal to match database enum
        ),
        User(
            username="creator1@tribaliq.com",
            password_hash=hash_password("TestPassword123!"),
            full_name="Emma Rodriguez",
            role="Creator"  # Use string literal to match database enum
        ),
        User(
            username="creator2@tribaliq.com",
            password_hash=hash_password("TestPassword123!"),
            full_name="David Kim",
            role="Creator"  # Use string literal to match database enum
        ),
    ]

    for user in test_users:
        db.add(user)

    await db.commit()
    print(f"✅ Created {len(test_users)} test users:")
    for user in test_users:
        print(f"   - {user.username} ({user.role}): {user.full_name}")


async def main():
    """Main seed function."""
    print("🌱 Starting database seed...")

    # Create tables (if not already created by migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed data
    async with AsyncSessionLocal() as db:
        await seed_users(db)

    print("✅ Database seed completed!")
    print("\n📝 Test Credentials:")
    print("   MA Users:")
    print("   - ma1@tribaliq.com / TestPassword123!")
    print("   - ma2@tribaliq.com / TestPassword123!")
    print("   Creator Users:")
    print("   - creator1@tribaliq.com / TestPassword123!")
    print("   - creator2@tribaliq.com / TestPassword123!")


if __name__ == "__main__":
    asyncio.run(main())
