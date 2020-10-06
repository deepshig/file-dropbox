import uuid
import time
import json

STATUS_FILE_CACHED = "File stored in cache"
STATUS_FILE_UPLOADED = "File uplaoded successfully"


class FileUploader:
    def __init__(self, file_cache, queue_manager, index_cache):
        self.file_cache = file_cache
        self.queue_manager = queue_manager
        self.index_cache = index_cache

    def send_file_for_upload(self, file_path):
        file_name = str(uuid.uuid4())

        result = self.file_cache.store(file_path, file_name)
        if not result["success"]:
            result["error_msg"] = "Error while storing the file contents in cache : " + result["error"]
            return result

        file_cache_key = result["file_key"]

        result = self.__create_file_index_cache(file_name)
        if not result["success"]:
            result["error_msg"] = "Error while creating file index on the cache : " + result["error"]
            return result

        result = self.__publish_queue_event(file_name, file_cache_key)
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

        result = self.__update_file_index_cache(
            file_name, STATUS_FILE_UPLOADED)
        if not result["success"]:
            result["error_msg"] = "Error while updating file status in index cache  : " + \
                result["error"]
            return result

        return {"success": True}

    def __create_file_index_cache(self, file_name):
        index_key = self.__get_index_key(file_name)
        result = self.index_cache.set(index_key, STATUS_FILE_CACHED)
        return result

    def __update_file_index_cache(self, file_name, updated_status):
        index_key = self.__get_index_key(file_name)

        result = self.__check_if_index_key_exists(index_key)
        if not result["success"]:
            return result

        result = self.index_cache.set(index_key, updated_status)
        return result

    def __check_if_index_key_exists(self, file_name):
        return self.index_cache.get(file_name)

    def __get_index_key(self, file_name):
        return "file_index:" + file_name

    def __publish_queue_event(self, file_name, file_key):
        msg = {"id": str(uuid.uuid4()),
               "file_name": file_name,
               "file_cache_key": file_key,
               "event_timestamp": time.time()}

        msg_json = json.dumps(msg)
        return self.queue_manager.publish(msg_json)
