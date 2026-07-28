from typing import Optional
from sqlalchemy.future import select
from database import AsyncSessionLocal, User

class DatabaseService:
    @staticmethod
    async def get_or_create_user(telegram_id: int, username: Optional[str] = None, first_name: Optional[str] = None) -> User:
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(telegram_id=telegram_id, username=username, first_name=first_name)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user

    @staticmethod
    async def update_user_setting(telegram_id: int, key: str, value) -> None:
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user and hasattr(user, key):
                setattr(user, key, value)
                await session.commit()
