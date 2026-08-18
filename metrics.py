from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response, Request
import time

# Define metrics
REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
TASKS_CREATED = Counter('tasks_created_total', 'Total number of tasks created')
TASKS_ACTIVE = Gauge('tasks_active_total', 'Number of active (not completed) tasks')
TASKS_COMPLETED = Counter('tasks_completed_total', 'Total number of tasks marked completed')

async def metrics_endpoint(request: Request):
    """Expose metrics for Prometheus scraping"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

def track_metrics(method):
    """Decorator to track endpoint metrics"""
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            response = await method(*args, **kwargs)
            status = getattr(response, 'status_code', 200)
            REQUESTS.labels(
                method=method.__name__,
                endpoint='/tasks',
                status=status
            ).inc()
            return response
        except Exception as e:
            REQUESTS.labels(
                method=method.__name__,
                endpoint='/tasks',
                status=500
            ).inc()
            raise e
        finally:
            LATENCY.labels(
                method=method.__name__,
                endpoint='/tasks'
            ).observe(time.time() - start)
    return wrapper
