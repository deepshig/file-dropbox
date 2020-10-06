import uuid
import time
import json
from src.file_uploader import index_cache
# import index_cache


class FileUploader:
    def __init__(self, file_cache, queue_manager, index_cache):
        self.file_cache = file_cache
        self.queue_manager = queue_manager
        self.index_cache = index_cache

    def send_file_for_upload(self, file_path, user_id, user_name):
        file_name = str(uuid.uuid4())

        result = self.file_cache.store(file_path, file_name)
        if not result["success"]:
            result["error_msg"] = "Error while storing the file contents in cache : " + result["error"]
            return result

        file_cache_key = result["file_key"]

        result = self.index_cache.create(file_name)
        if not result["success"]:
            result["error_msg"] = "Error while creating file index on the cache : " + result["error"]
            return result

        result = self.__publish_queue_event(
            file_name, file_cache_key, user_id, user_name)
        if not result["message_published"]:
            result["success"] = False
            result["error_msg"] = result["error"]
            return result

        return {"success": True,
                "file_name": file_name}

    def delete_uploaded_file(self, file_name):
        result = self.file_cache.delete(file_name)
        if not result["success"]:
            result["error_msg"] = "Error while deleting the file from cache : " + \
                result["error"]
            return result

        result = self.index_cache.update(
            file_name, index_cache.STATUS_FILE_UPLOADED)
        if not result["success"]:
            result["error_msg"] = "Error while updating file status in index cache  : " + \
                result["error"]
            return result

        return {"success": True}

    def __publish_queue_event(self, file_name, file_key, user_id, user_name):
        msg = {"id": str(uuid.uuid4()),
               "file_name": file_name,
               "file_cache_key": file_key,
               "user_id": user_id,
               "user_name": user_name,
               "event_timestamp": time.time()}

        msg_json = json.dumps(msg)
        return self.queue_manager.publish(msg_json)
