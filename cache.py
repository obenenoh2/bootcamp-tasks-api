import json
import os

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL_SECONDS = 30
TASKS_LIST_KEY = "tasks:list"
TASK_KEY_TMPL = "tasks:{task_id}"

client = redis.from_url(REDIS_URL, decode_responses=True)


def get_cached_tasks():
    raw = client.get(TASKS_LIST_KEY)
    return json.loads(raw) if raw else None


def set_cached_tasks(tasks):
    client.set(TASKS_LIST_KEY, json.dumps(tasks), ex=CACHE_TTL_SECONDS)


def get_cached_task(task_id: int):
    raw = client.get(TASK_KEY_TMPL.format(task_id=task_id))
    return json.loads(raw) if raw else None


def set_cached_task(task_id: int, task: dict):
    client.set(TASK_KEY_TMPL.format(task_id=task_id), json.dumps(task), ex=CACHE_TTL_SECONDS)


def invalidate_task_cache(task_id: int):
    client.delete(TASKS_LIST_KEY)
    client.delete(TASK_KEY_TMPL.format(task_id=task_id))
