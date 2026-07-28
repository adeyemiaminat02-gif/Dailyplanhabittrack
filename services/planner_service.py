from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy import update
from database import AsyncSessionLocal, Task, PriorityEnum

class PlannerService:
    @staticmethod
    async def create_task(user_id: int, title: str, category: str = "Personal", priority: str = "Medium", deadline: Optional[datetime] = None) -> Task:
        async with AsyncSessionLocal() as session:
            priority_val = PriorityEnum(priority.capitalize()) if priority.capitalize() in PriorityEnum.__members__ else PriorityEnum.MEDIUM
            task = Task(user_id=user_id, title=title, category=category, priority=priority_val, deadline=deadline)
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    @staticmethod
    async def get_user_tasks(user_id: int, filter_type: str = "today") -> List[Task]:
        async with AsyncSessionLocal() as session:
            now = datetime.utcnow()
            stmt = select(Task).where(Task.user_id == user_id, Task.is_archived == False)
            
            if filter_type == "today":
                stmt = stmt.where(Task.deadline >= now.replace(hour=0, minute=0, second=0), Task.deadline <= now.replace(hour=23, minute=59, second=59))
            elif filter_type == "tomorrow":
                tomorrow = now + timedelta(days=1)
                stmt = stmt.where(Task.deadline >= tomorrow.replace(hour=0, minute=0, second=0), Task.deadline <= tomorrow.replace(hour=23, minute=59, second=59))
            elif filter_type == "upcoming":
                stmt = stmt.where(Task.deadline > now)
            
            result = await session.execute(stmt)
            return list(result.scalars().all())

    @staticmethod
    async def complete_task(task_id: int, user_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            res = await session.execute(stmt)
            task = res.scalar_one_or_none()
            if task:
                task.is_completed = True
                task.is_archived = True
                await session.commit()
                return True
            return False

    @staticmethod
    async def search_tasks(user_id: int, keyword: str) -> List[Task]:
        async with AsyncSessionLocal() as session:
            stmt = select(Task).where(Task.user_id == user_id, Task.title.ilike(f"%{keyword}%"))
            res = await session.execute(stmt)
            return list(res.scalars().all())
