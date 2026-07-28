from datetime import datetime
from typing import List
from sqlalchemy.future import select
from database import AsyncSessionLocal, Reminder

class ReminderService:
    @staticmethod
    async def create_reminder(user_id: int, title: str, remind_at: datetime, reminder_type: str = "Custom", recurrence: str = "once") -> Reminder:
        async with AsyncSessionLocal() as session:
            reminder = Reminder(user_id=user_id, title=title, remind_at=remind_at, reminder_type=reminder_type, recurrence=recurrence)
            session.add(reminder)
            await session.commit()
            await session.refresh(reminder)
            return reminder

    @staticmethod
    async def get_pending_reminders() -> List[Reminder]:
        async with AsyncSessionLocal() as session:
            now = datetime.utcnow()
            stmt = select(Reminder).where(Reminder.remind_at <= now, Reminder.is_sent == False)
            res = await session.execute(stmt)
            return list(res.scalars().all())

    @staticmethod
    async def mark_sent(reminder_id: int) -> None:
        async with AsyncSessionLocal() as session:
            stmt = select(Reminder).where(Reminder.id == reminder_id)
            res = await session.execute(stmt)
            reminder = res.scalar_one_or_none()
            if reminder:
                reminder.is_sent = True
                await session.commit()
