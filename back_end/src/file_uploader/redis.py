import redis
from redis import RedisError
import sys


class RedisDriver:
    def __init__(self, redis_config):
        self.__connect(redis_config)

    def __connect(self, redis_config):
        try:
            self.connection = redis.Redis(host=redis_config["host"],
                                          port=redis_config["port"])
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
