import pika
import sys
from config import config

class RabbitMQManager:
    def __init__(self, rabbitmq_config):
        self.connection_url = self.__get_connection_url(rabbitmq_config)
        self.connection = self.__get_connection(self.connection_url)
        self.chan      = self.connection.channel()
        # self.chan.queue_declare(queue='hello', durable=True)
        self.queue_name = rabbitmq_config["queue_name"]
        self.__init_queue()

    def __get_connection_url(self, rabbitmq_config):
        return "amqp://{}:{}@{}:{}?connection_attempts=10&retry_delay=10".format(config["rabbitmq_config"]["user"],
                                                                                 config["rabbitmq_config"]["password"],
                                                                                 config["rabbitmq_config"]["host"],
                                                                                 config["rabbitmq_config"]["port"])

    def __get_connection(self, amqp_url):
        try:
            url_params = pika.URLParameters(amqp_url)
            connection = pika.BlockingConnection(url_params)
        except pika.exceptions as err:
            error_str = "Error while connecting to rabbitmq : " + str(err)
            sys.exit(error_str)
        else:
            return connection


    def receive_msg(self, aws_client,message_body):
        msg = body.decode('utf-8')

        try:
            aws_client.upload_fileobj(file, upload_file_bucket, str(upload_file_key))
            logging.info("AWS S3 - Upload successful")
        except Exception as e:
            logging.error("AWS S3- Upload fail")
