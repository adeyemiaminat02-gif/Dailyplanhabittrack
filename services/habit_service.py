from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.future import select
from database import AsyncSessionLocal, Habit, HabitLog, HabitFrequencyEnum

class HabitService:
    @staticmethod
    async def create_habit(user_id: int, name: str, frequency: str = "Daily") -> Habit:
        async with AsyncSessionLocal() as session:
            freq_enum = HabitFrequencyEnum(frequency.capitalize()) if frequency.capitalize() in HabitFrequencyEnum.__members__ else HabitFrequencyEnum.DAILY
            habit = Habit(user_id=user_id, name=name, frequency=freq_enum)
            session.add(habit)
            await session.commit()
            await session.refresh(habit)
            return habit

    @staticmethod
    async def get_user_habits(user_id: int) -> List[Habit]:
        async with AsyncSessionLocal() as session:
            stmt = select(Habit).where(Habit.user_id == user_id)
            res = await session.execute(stmt)
            return list(res.scalars().all())

    @staticmethod
    async def mark_habit_complete(habit_id: int, user_id: int) -> Optional[Habit]:
        async with AsyncSessionLocal() as session:
            stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
            res = await session.execute(stmt)
            habit = res.scalar_one_or_none()
            if habit:
                now = datetime.utcnow()
                habit.last_completed_at = now
                habit.current_streak += 1
                if habit.current_streak > habit.longest_streak:
                    habit.longest_streak = habit.current_streak
                
                log = HabitLog(habit_id=habit.id, action="completed", logged_date=now)
                session.add(log)
                await session.commit()
                await session.refresh(habit)
                return habit
            return None

    @staticmethod
    async def toggle_pause_habit(habit_id: int, user_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
            res = await session.execute(stmt)
            habit = res.scalar_one_or_none()
            if habit:
                habit.is_paused = not habit.is_paused
                await session.commit()
                return habit.is_paused
            return False
