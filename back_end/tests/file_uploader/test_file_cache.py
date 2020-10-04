import pytest
import sys
import os
sys.path.append('../')

from src.file_uploader.file_cache import FileCache, ERROR_FILE_NOT_FOUND, ERROR_EMPTY_FILE  # NOQA
from src.file_uploader.redis import ERROR_KEY_NOT_FOUND # NOQA

test_redis_config = {"host": "127.0.0.1",
                     "port": 6379}


def teardown_redis(redis_conn):
    if redis_conn is not None:
        redis_conn.flushall()

def test_store():
    cache = FileCache(test_redis_config)
    """
    failure : file does not exist
    """
    file_name = "random_file.txt"
    file_path = "some/path/"+file_name

    result = cache.store(file_path, file_name)
    assert result["success"] == False
    assert result["error"] == ERROR_FILE_NOT_FOUND

    key = "file:random_file.txt"
    fetched_file = cache.redis.get(key)
    assert fetched_file["success"] == False
    assert fetched_file["error"] == ERROR_KEY_NOT_FOUND

    """
    failure : file is empty
    """
    file_name = "test_file.txt"
    file_path = "./"+file_name
    file = open(file_path, "w")
    file.close()

    result = cache.store(file_path, file_name)
    assert result["success"] == False
    assert result["error"] == ERROR_EMPTY_FILE

    key = "file:test_file.txt"
    fetched_file = cache.redis.get(key)
    assert fetched_file["success"] == False
    assert fetched_file["error"] == ERROR_KEY_NOT_FOUND

    """
    success
    """
    file_name = "test_file.txt"
    file_path = "./"+file_name

    file = open(file_path, "w+")
    file_content = "Hello World"
    file.write(file_content)
    file.close()

    result = cache.store(file_path, file_name)
    assert result["success"] == True

    key = "file:test_file.txt"
    fetched_file = cache.redis.get(key)
    assert fetched_file["success"] == True
    assert fetched_file["value"] == str(file_content.encode('utf-8'))

    teardown_redis(cache.redis.connection)
    os.remove(file_name)


