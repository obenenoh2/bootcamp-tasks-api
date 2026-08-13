# Tasks API

A minimal FastAPI task tracker backed by Postgres, with a Redis read-through cache.

## Quick Start

**Use Python 3.10–3.12.** The pinned `pydantic==2.7.0` / `pydantic-core==2.18.1` has no
prebuilt wheel for Python 3.13+, so pip will try to compile it from source and fail. If
`python3 -V` shows 3.13 or newer, install 3.12 separately (e.g. `brew install python@3.12`)
and use that to create the venv below.

The app needs a Postgres database and a Redis instance to run. The easiest way to get both
locally is Docker:

```bash
docker compose up -d db redis
```

Then run the API itself:

```bash
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

By default the app connects to `postgresql+psycopg2://tasks:tasks@localhost:5432/tasks` and
`redis://localhost:6379/0` — override with the `DATABASE_URL` / `REDIS_URL` env vars if your
setup differs.

Open http://localhost:8000/docs for the interactive API docs.

## With Docker

```bash
docker compose up
```

This starts the API together with its Postgres and Redis containers, wired together with the
right env vars and healthchecks.

## Using the Swagger UI

FastAPI serves interactive API docs (Swagger UI) at `/docs` whenever the app is running.

1. Start the app (`uvicorn main:app --reload` or `docker compose up`).
2. Open http://localhost:8000/docs in a browser.
3. Expand an endpoint, e.g. `POST /tasks`, and click **Try it out**.
4. Edit the example request body, e.g.:
   ```json
   {
     "title": "Write the report",
     "description": "Due Friday",
     "priority": "medium"
   }
   ```
5. Click **Execute** to send the request and see the live response below, including the
   assigned `id`.
6. Use the `id` from that response to try `GET /tasks/{task_id}`, `PATCH /tasks/{task_id}`, or
   `DELETE /tasks/{task_id}` the same way.
7. `GET /tasks` lists everything currently stored; `GET /health` is a quick liveness check.

A raw OpenAPI schema is also available at `/openapi.json` if you want to feed it into another
tool (Postman, codegen, etc).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The test suite runs against an in-memory SQLite database and a fake Redis client, so it needs
neither Docker nor a real Postgres/Redis instance.

## Task-priority model

`model/train.py` trains a trivial TF-IDF + logistic regression classifier that predicts a
task's `priority` (low/medium/high) from its title + description, and logs it to MLflow. It's
the starter kit for the MLFlowOps project option. Unlike the app itself, this part of the repo
uses its own venv (see below) to keep the ML dependencies (`mlflow`, `pandas`, `scikit-learn`)
out of the API's runtime image.

Training reads directly from the app's Postgres `tasks` table — any task with a `priority` set
(via the API or the seed script below) becomes a training row. There's no separate dataset file
to keep in sync with the app.

`model/generate_data.py` seeds the database with synthetic, labeled tasks so there's something
to train on before real usage data accumulates:

```bash
DATABASE_URL=postgresql+psycopg2://tasks:tasks@localhost:5432/tasks python model/generate_data.py
```

**Use Python 3.10–3.12.** `mlflow` pulls in `pyarrow`, which has no prebuilt wheel for very new
Python versions (3.13+) on several platforms — pip will try to build it from source and fail
with a `cmake` error unless you have the full C++ build toolchain installed. If `python3 -V`
shows 3.13 or newer, install 3.12 separately (e.g. `brew install python@3.12`) and use that to
create the venv below.

```bash
python3.12 -m venv .venv-model
source .venv-model/bin/activate   # Windows: .venv-model\Scripts\activate
pip install -r model/requirements.txt
MLFLOW_TRACKING_URI=http://localhost:5000 python model/train.py
```
