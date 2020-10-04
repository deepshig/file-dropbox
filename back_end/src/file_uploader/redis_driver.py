import redis
from redis import RedisError
import sys

ERROR_KEY_NOT_FOUND = "Key not found in redis"


class RedisDriver:
    def __init__(self, redis_config):
        self.__connect(redis_config)

    def __connect(self, redis_config):
        try:
            self.connection = redis.StrictRedis(host=redis_config["host"],
                                                port=redis_config["port"],
                                                encoding="utf-8",
                                                decode_responses=True)
        except RedisError as err:
            error_str = "Error while connecting to redis : " + str(err)
            sys.exit(error_str)

    def set(self, key, value):
        key_str = str(key)
        val_str = str(value)
        try:
            self.connection.set(key_str, val_str)
            return {"success": True}
        except RedisError as err:
            error_str = "Error while connecting to redis : " + str(err)
            return {"success": False,
                    "error": error_str}

    def get(self, key):
        key_str = str(key)
        try:
            value = self.connection.get(key_str)
        except RedisError as err:
            error_str = "Error while retrieving value from redis : " + str(err)
            return {"success": False,
                    "error": error_str}

        if value is not None:
            return {"success": True,
                    "value": value}
        else:
            return {"success": False,
                    "error": ERROR_KEY_NOT_FOUND}
