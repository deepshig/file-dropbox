import pytest
from pytest_mock import mocker
import sys
sys.path.append('../')

from src.file_uploader.file_uploader_service import FileUploader  # NOQA
from src.file_uploader.file_cache import FileCache  # NOQA
from src.file_uploader.index_cache import IndexCache  # NOQA
from src.file_uploader.redis_driver import RedisDriver  # NOQA
from src.file_uploader.rabbitmq import RabbitMQManager  # NOQA

test_redis_config = {"host": "127.0.0.1",
                     "port": 6379}

test_rabbitmq_config = {"user": "guest",
                        "password": "guest",
                        "host": "127.0.0.1",
                        "port": "5672",
                        "queue_name": "test"}


def test_send_file_for_upload(mocker):
    user_id = "user:1"
    user_name = "test_user"
    """
    failure : error while storing file in cache
    """
    def mock_file_cache_store(obj, file_path, file_name):
        return {"success": False,
                "error": "some_error"}

    mocker.patch.object(FileCache, 'store', new=mock_file_cache_store)

    file_cache = FileCache(test_redis_config)
    svc = FileUploader(file_cache, None, None)

    result = svc.send_file_for_upload("/random/file/path", user_id, user_name)
    assert result["success"] == False
    assert result["error_msg"] == "Error while storing the file contents in cache : some_error"

    """
    failure : error while creating file index cache entry
    """
    def mock_file_cache_store(obj, file_path, file_name):
        return {"success": True,
                "file_key": "file:file_name"}

    def mock_index_cache_create(obj, file_name):
        return {"success": False,
                "error": "some_error_in_indexing"}

    mocker.patch.object(FileCache, 'store', new=mock_file_cache_store)
    mocker.patch.object(IndexCache, 'create', new=mock_index_cache_create)

    file_cache = FileCache(test_redis_config)
    index_cache = IndexCache(test_redis_config)
    svc = FileUploader(file_cache, None, index_cache)

    result = svc.send_file_for_upload("/random/file/path", user_id, user_name)
    assert result["success"] == False
    assert result["error_msg"] == "Error while creating file index on the cache : some_error_in_indexing"

    """
    failure : error while publishing event to rabbitmq
    """
    def mock_file_cache_store(obj, file_path, file_name):
        return {"success": True,
                "file_key": "file:file_name"}

    def mock_index_cache_create(obj, file_name):
        return {"success": True}

    def mock_publish(obj, msg_body):
        return {"message_published": False,
                "error": "something failing"}

    mocker.patch.object(FileCache, 'store', new=mock_file_cache_store)
    mocker.patch.object(IndexCache, 'create', new=mock_index_cache_create)
    mocker.patch.object(RabbitMQManager, 'publish', new=mock_publish)

    file_cache = FileCache(test_redis_config)
    index_cache = IndexCache(test_redis_config)
    queue_manager = RabbitMQManager(test_rabbitmq_config)
    svc = FileUploader(file_cache, queue_manager, index_cache)

    result = svc.send_file_for_upload("/random/file/path", user_id, user_name)
    assert result["success"] == False
    assert result["error_msg"] == "something failing"

    """
    success
    """
    def mock_file_cache_store(obj, file_path, file_name):
        return {"success": True,
                "file_key": "file:file_name"}

    def mock_index_cache_create(obj, file_name):
        return {"success": True}

    def mock_publish(obj, msg_body):
        return {"message_published": True}

    mocker.patch.object(FileCache, 'store', new=mock_file_cache_store)
    mocker.patch.object(IndexCache, 'create', new=mock_index_cache_create)
    mocker.patch.object(RabbitMQManager, 'publish', new=mock_publish)

    file_cache = FileCache(test_redis_config)
    index_cache = IndexCache(test_redis_config)
    queue_manager = RabbitMQManager(test_rabbitmq_config)
    svc = FileUploader(file_cache, queue_manager, index_cache)

    result = svc.send_file_for_upload("/random/file/path", user_id, user_name)
    assert result["success"] == True


def test_delete_uploaded_file(mocker):
    """
    failure : error in deleting file from cache
    """
    def mock_file_cache_delete(obj, file_name):
        return {"success": False,
                "error": "some_error"}

    mocker.patch.object(FileCache, 'delete', new=mock_file_cache_delete)

    file_cache = FileCache(test_redis_config)
    svc = FileUploader(file_cache, None, None)

    result = svc.delete_uploaded_file("file1")
    assert result["success"] == False
    assert result["error_msg"] == "Error while deleting the file from cache : some_error"

    """
    failure : key not found in index cache
    """
    def mock_file_cache_delete(obj, file_name):
        return {"success": True,
                "file_key": "file:file_name"}

    def mock_redis_get(obj, key):
        return {"success": False,
                "error": "key not found"}

    mocker.patch.object(FileCache, 'delete', new=mock_file_cache_delete)
    mocker.patch.object(RedisDriver, 'get', new=mock_redis_get)

    file_cache = FileCache(test_redis_config)
    index_cache = IndexCache(test_redis_config)
    svc = FileUploader(file_cache, None, index_cache)

    result = svc.delete_uploaded_file("file1")
    assert result["success"] == False
    assert result["error_msg"] == "Error while updating file status in index cache  : key not found"

    """
    failure : error in updating file index cache
    """
    def mock_file_cache_delete(obj, file_name):
        return {"success": True,
                "file_key": "file:file_name"}

    def mock_index_cache_update(obj, file_name, status):
        return {"success": False,
                "error": "some_error_in_redis"}

    mocker.patch.object(FileCache, 'delete', new=mock_file_cache_delete)
    mocker.patch.object(IndexCache, 'update', new=mock_index_cache_update)

    file_cache = FileCache(test_redis_config)
    index_cache = IndexCache(test_redis_config)
    svc = FileUploader(file_cache, None, index_cache)

    result = svc.delete_uploaded_file("file1")
    assert result["success"] == False
    assert result["error_msg"] == "Error while updating file status in index cache  : some_error_in_redis"

    """
    success
    """
    def mock_file_cache_store(obj, file_path, file_name):
        return {"success": True,
                "file_key": "file:file_name"}

    def mock_index_cache_update(obj, file_name, status):
        return {"success": True}

    mocker.patch.object(FileCache, 'store', new=mock_file_cache_store)
    mocker.patch.object(IndexCache, 'update', new=mock_index_cache_update)

    file_cache = FileCache(test_redis_config)
    index_cache = IndexCache(test_redis_config)
    svc = FileUploader(file_cache, None, index_cache)

    result = svc.delete_uploaded_file("file1")
    assert result["success"] == True
