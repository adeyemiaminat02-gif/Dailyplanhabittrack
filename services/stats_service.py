from sqlalchemy.future import select
from sqlalchemy import func
from database import AsyncSessionLocal, Task, Habit

class StatsService:
    @staticmethod
    async def get_user_stats(user_id: int) -> dict:
        async with AsyncSessionLocal() as session:
            total_tasks = await session.scalar(select(func.count(Task.id)).where(Task.user_id == user_id))
            completed_tasks = await session.scalar(select(func.count(Task.id)).where(Task.user_id == user_id, Task.is_completed == True))
            
            habits = (await session.execute(select(Habit).where(Habit.user_id == user_id))).scalars().all()
            total_habits = len(habits)
            longest_streak = max([h.longest_streak for h in habits], default=0)
            active_streaks = [h.current_streak for h in habits if h.current_streak > 0]
            
            completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

            return {
                "total_tasks": total_tasks or 0,
                "completed_tasks": completed_tasks or 0,
                "pending_tasks": (total_tasks or 0) - (completed_tasks or 0),
                "completion_rate": completion_rate,
                "total_habits": total_habits,
                "longest_streak": longest_streak,
                "avg_active_streak": round(sum(active_streaks) / len(active_streaks), 1) if active_streaks else 0
            }
