from models import models, redis_model

import consumer



from config import config

import boto3

class service():
    def __init__(self):
        self.mongo_client = self.getMongoDbModel()
        # self.rabbitmq_client = getRabbitMqModel()

        self.reddis_client  = self.getRedisModel()
        self.aws_client   = self.getAwsModel()
        return

    def getMongoDbModel(self):
       return models.model()

    # def getRabbitMqModel(self):
    #     return consumer.RabbitMQManager(config["rabbitmq_config"]["queue_name"])

    def getRedisModel(self):
        return redis_model.RedisDriver(config["index_cache_config"])

    def getAwsModel(self):
        return boto3.client('s3',aws_access_key_id=config["aws"]["access_key"],aws_secret_access_key = config["aws"]["secret_access_key"])

