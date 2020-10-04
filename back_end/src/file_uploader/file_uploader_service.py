import uuid
import time
import json

STATUS_FILE_CACHED = "File stored in cache"

class FileUploader:
    def __init__(self, file_cache, queue_manager, index_cache):
        self.file_cache = file_cache
        self.queue_manager = queue_manager
        self.index_cache = index_cache

    def send_file_for_upload(self, file_path):
        file_name = str(uuid.uuid4())

        result = self.file_cache.store(file_name)
        if not result["success"]:
            result["error"] = "Error while storing the file contents in cache : " + result["error"]
            return result

        result = self.__create_file_index_cache(file_name)
        if not result["success"]:
            result["error"] = "Error while creating file index on the cache : " + result["error"]
            return result


        result = self.__publish_queue_event(file_name, result["index_key"])
        if not result["message_published"]:
            result["success"] = False
            return result

        return {"success": True,
                "file_name": file_name}

    def __create_file_index_cache(self, file_name):
        index_key = "file_index:" + file_name
        result = self.index_cache.set(index_key, STATUS_FILE_CACHED)
        result["index_key"] = index_key
        return result

    def __publish_queue_event(self, file_name, index_key):
        msg = {"id": str(uuid.uuid4()),
               "file_name": file_name,
               "index_cache_key": index_key,
               "event_timestamp": time.time()}

        msg_json = json.dumps(msg)
        return self.queue_manager.publish(msg_json)

