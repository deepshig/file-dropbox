import redis
import sys


class RedisDriver:
    def __init__(self):
        self.connection = None

    def connect(self, redis_config):
        try:
            self.connection = redis.Redis(host=redis_config["host"],
                                          port=redis_config["port"])
        except Exception as err:
            error_str = "Error while connecting to redis : " + str(err)
            sys.exit(error_str)
