from src.file_uploader.redis_driver import RedisDriver
import pytest
from pytest_mock import mocker
import sys
sys.path.append('../')

from src.file_uploader.index_cache import IndexCache, STATUS_FILE_CACHED  # NOQA
from src.file_uploader.redis_driver import RedisDriver, ERROR_KEY_NOT_FOUND  # NOQA

test_redis_config = {"host": "127.0.0.1",
                     "port": 6379}


def teardown_redis(redis_conn):
    if redis_conn is not None:
        redis_conn.flushall()


def test_create(mocker):
    file_name = "file1"

    """
    success
    """
    cache = IndexCache(test_redis_config)
    result = cache.create(file_name)
    assert result["success"] == True

    key = "file_index:" + file_name
    result = cache.redis.get(key)
    assert result["success"] == True
    assert result["value"] == STATUS_FILE_CACHED

    teardown_redis(cache.redis.connection)

    """
    failure : redis fails
    """
    def mock_redis_set(obj, key, val):
        return {"success": False,
                "error": "some redis error"}

    mocker.patch.object(RedisDriver, 'set', new=mock_redis_set)

    cache = IndexCache(test_redis_config)
    result = cache.create(file_name)
    assert result["success"] == False
    assert result["error"] == "some redis error"


def test_update(mocker):
    file_name = "file1"
    index_key = "file_index:" + file_name
    new_status = "something"

    cache = IndexCache(test_redis_config)

    """
    success
    """
    result = cache.redis.set(index_key, "old_status")
    assert result["success"] == True

    result = cache.update(file_name, new_status)
    print(result)
    assert result["success"] == True

    result = cache.redis.get(index_key)
    assert result["success"] == True
    assert result["value"] == new_status

    teardown_redis(cache.redis.connection)

    """
    failure : key doesn't exist
    """
    result = cache.update(file_name, new_status)
    assert result["success"] == False
    assert result["error"] == ERROR_KEY_NOT_FOUND

    """
    failure : redis is not responsive while getting the key
    """
    def mock_redis_get(obj, key):
        return {"success": False,
                "error": "Redis not responding"}

    mocker.patch.object(RedisDriver, 'get', new=mock_redis_get)

    cache = IndexCache(test_redis_config)
    result = cache.update(file_name, new_status)
    assert result["success"] == False
    assert result["error"] == "Redis not responding"

    """
    failure : redis is not responsive while setting the key
    """
    def mock_redis_get(obj, key):
        return {"success": True}

    def mock_redis_set(obj, key, value):
        return {"success": False,
                "error": "Redis not responding"}

    mocker.patch.object(RedisDriver, 'get', new=mock_redis_get)
    mocker.patch.object(RedisDriver, 'set', new=mock_redis_set)

    cache = IndexCache(test_redis_config)
    result = cache.update(file_name, new_status)
    assert result["success"] == False
    assert result["error"] == "Redis not responding"
