<<<<<<< HEAD
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import cache
from database import Base, engine, get_db
from models import TaskModel

app = FastAPI(title="Tasks API", description="Bootcamp demo app — Week 1/2/8")

Base.metadata.create_all(bind=engine)
=======
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os

app = FastAPI(title="Tasks API", description="Bootcamp demo app — Week 1/2/8")

# In-memory store for simplicity (Week 2 labs add a real database)
tasks: dict[int, dict] = {}
next_id = 1
>>>>>>> 983f97f (Initial tasks-api — FastAPI bootcamp demo app)


class Task(BaseModel):
    title: str
    description: Optional[str] = None
    done: bool = False
<<<<<<< HEAD
    priority: Optional[str] = None  # "low" | "medium" | "high" — set manually or by the priority-classifier model
=======
>>>>>>> 983f97f (Initial tasks-api — FastAPI bootcamp demo app)


class TaskOut(Task):
    id: int

<<<<<<< HEAD
    model_config = {"from_attributes": True}

=======
>>>>>>> 983f97f (Initial tasks-api — FastAPI bootcamp demo app)

@app.get("/health")
def health():
    return {"status": "ok", "service": "tasks-api"}


@app.get("/tasks", response_model=List[TaskOut])
<<<<<<< HEAD
def list_tasks(db: Session = Depends(get_db)):
    cached = cache.get_cached_tasks()
    if cached is not None:
        return cached
    result = [TaskOut.model_validate(t).model_dump() for t in db.query(TaskModel).order_by(TaskModel.id).all()]
    cache.set_cached_tasks(result)
    return result


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(task: Task, db: Session = Depends(get_db)):
    db_task = TaskModel(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    cache.invalidate_task_cache(db_task.id)
    return db_task


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    cached = cache.get_cached_task(task_id)
    if cached is not None:
        return cached
    db_task = db.get(TaskModel, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    result = TaskOut.model_validate(db_task).model_dump()
    cache.set_cached_task(task_id, result)
    return result


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: Task, db: Session = Depends(get_db)):
    db_task = db.get(TaskModel, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in task.model_dump().items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    cache.invalidate_task_cache(task_id)
    return db_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.get(TaskModel, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    cache.invalidate_task_cache(task_id)
=======
def list_tasks():
    return [{"id": k, **v} for k, v in tasks.items()]


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(task: Task):
    global next_id
    tasks[next_id] = task.model_dump()
    result = {"id": next_id, **tasks[next_id]}
    next_id += 1
    return result


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task_id, **tasks[task_id]}


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: Task):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[task_id] = task.model_dump()
    return {"id": task_id, **tasks[task_id]}


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
>>>>>>> 983f97f (Initial tasks-api — FastAPI bootcamp demo app)
