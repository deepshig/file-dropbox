import pytest
import sys
sys.path.append('../')

from src.file_uploader.redis import RedisDriver, ERROR_KEY_NOT_FOUND  # NOQA

test_redis_config = {"host": "127.0.0.1",
                     "port": 6379}


def teardown_redis(redis_conn):
    if redis_conn is not None:
        redis_conn.flushall()


def test_connect():
    r = RedisDriver(test_redis_config)
    r.connection.set("hello", "world")
    assert r.connection.get("hello") == b'world'
    teardown_redis(r.connection)


def test_set():
    r = RedisDriver(test_redis_config)
    """
    success : set normal string value
    """
    result = r.set("test_key", "test_value")
    assert result["success"] == True

    assert r.connection.get("test_key") == b'test_value'

    """
    success : set non-string value
    """
    result = r.set("test_key2", {"k1": 1})
    print(result)
    assert result["success"] == True
    teardown_redis(r.connection)


def test_get():
    r = RedisDriver(test_redis_config)
    """
    failure : key doesn't exist
    """
    result = r.get("random_key")
    assert result["success"] == False
    assert result["error"] == ERROR_KEY_NOT_FOUND

    """
    success
    """
    r.connection.set("hello", "world")

    result = r.get("hello")
    assert result["success"] == True
    assert result["value"] == "world"
    teardown_redis(r.connection)
