from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

# Define Base here
Base = declarative_base()

# SQLAlchemy model
class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, default="medium")
    completed = Column(Boolean, default=False)

# Pydantic models for API
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    done: Optional[bool] = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    done: Optional[bool] = None

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    done: bool = False
    
    class Config:
        from_attributes = True
