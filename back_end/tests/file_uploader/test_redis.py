import pytest
import sys
sys.path.append('../')

from src.file_uploader.redis import RedisDriver  # NOQA

test_redis_config = {"host": "127.0.0.1",
                     "port": 6379}


def teardown_redis(redis_conn):
    if redis_conn is not None:
        redis_conn.flushall()


def test_connect():
    r = RedisDriver()
    r.connect(test_redis_config)
    r.connection.set("hello", "world")
    assert r.connection.get("hello") == b'world'
    teardown_redis(r.connection)
