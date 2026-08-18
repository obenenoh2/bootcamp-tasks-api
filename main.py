from fastapi import FastAPI, Depends, HTTPException
from typing import List
import uvicorn
import logging

from database import get_db, init_db, create_task, get_task, get_tasks, update_task, delete_task
from models import TaskCreate, TaskUpdate, Task
from cache import cache
from metrics import metrics_endpoint, TASKS_CREATED, TASKS_ACTIVE, TASKS_COMPLETED
from logger import logging_middleware

# Set up logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Taskly API", version="1.0.0")

# Add middleware
app.middleware("http")(logging_middleware)

# Add metrics endpoint
app.add_route("/metrics", metrics_endpoint)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "tasks-api"}

# Create task
@app.post("/tasks", response_model=Task)
async def create_task_endpoint(task: TaskCreate, db=Depends(get_db)):
    db_task = create_task(db, task)
    TASKS_CREATED.inc()
    TASKS_ACTIVE.inc()
    return db_task

# List tasks
@app.get("/tasks", response_model=List[Task])
async def list_tasks_endpoint(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks

# Get single task (with caching)
@app.get("/tasks/{task_id}", response_model=Task)
async def get_task_endpoint(task_id: int, db=Depends(get_db)):
    try:
        cached_task = await cache.get(f"task:{task_id}")
        if cached_task:
            logger.info(f"Cache hit for task {task_id}")
            return cached_task
    except Exception as e:
        logger.warning(f"Cache error: {e}")
    
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "done": task.completed
        }
        await cache.set(f"task:{task_id}", task_dict)
        logger.info(f"Cached task {task_id}")
    except Exception as e:
        logger.warning(f"Cache set error: {e}")
    
    return task

# Update task
@app.patch("/tasks/{task_id}", response_model=Task)
async def update_task_endpoint(task_id: int, task_update: TaskUpdate, db=Depends(get_db)):
    task = update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        await cache.delete(f"task:{task_id}")
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")
    
    if task_update.done:
        TASKS_COMPLETED.inc()
        TASKS_ACTIVE.dec()
    
    return task

# Delete task
@app.delete("/tasks/{task_id}")
async def delete_task_endpoint(task_id: int, db=Depends(get_db)):
    success = delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        await cache.delete(f"task:{task_id}")
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")
    TASKS_ACTIVE.dec()
    
    return {"message": "Task deleted successfully"}

@app.get("/")
async def root():
    return {"message": "Welcome to Taskly API"}

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        await cache.connect()
        logger.info("Cache connected successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
