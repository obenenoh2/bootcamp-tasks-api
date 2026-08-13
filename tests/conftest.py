import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

import fakeredis
import pytest

import cache
import database
import main  # noqa: F401  (registers TaskModel with Base.metadata)


@pytest.fixture(autouse=True)
def isolated_state():
    cache.client = fakeredis.FakeStrictRedis(decode_responses=True)
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    yield
