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
