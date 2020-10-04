from src.file_uploader import  redis

ERROR_FILE_NOT_FOUND = "File not found"
ERROR_EMPTY_FILE = "File is empty"

class FileCache:
    def __init__(self, redis_config):
        self.redis = redis.RedisDriver(redis_config)

    def __key(self, file_name):
        return "file:"+ file_name

    def store(self, file_name):
        file = None
        try:
            file = open(file_name, 'rb')
            file_contents = file.read()
        except FileNotFoundError:
            return {"success": False,
                    "error": ERROR_FILE_NOT_FOUND}
        finally:
            if file is not None:
                file.close()

        if file_contents is None or len(file_contents) == 0:
            return {"success": False,
                    "error":ERROR_EMPTY_FILE}

        file_key = self.__key(file_name)
        result = self.redis.set(file_key, file_contents)
        return result

