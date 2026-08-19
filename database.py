from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, TaskModel, TaskCreate, TaskUpdate
from typing import List, Optional
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tasks:tasks@db:5432/tasks")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database - create tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_task(db, task: TaskCreate) -> TaskModel:
    """Create a new task"""
    db_task = TaskModel(
        title=task.title,
        description=task.description,
        priority=task.priority,
        completed=task.done if hasattr(task, 'done') else False
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db, task_id: int) -> Optional[TaskModel]:
    """Get a task by ID"""
    return db.query(TaskModel).filter(TaskModel.id == task_id).first()

def get_tasks(db, skip: int = 0, limit: int = 100) -> List[TaskModel]:
    """Get all tasks with pagination"""
    return db.query(TaskModel).offset(skip).limit(limit).all()

def update_task(db, task_id: int, task_update: TaskUpdate) -> Optional[TaskModel]:
    """Update a task"""
    task = get_task(db, task_id)
    if not task:
        return None
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.done is not None:
        task.completed = task_update.done
    db.commit()
    db.refresh(task)
    return task

def delete_task(db, task_id: int) -> bool:
    """Delete a task"""
    task = get_task(db, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True
