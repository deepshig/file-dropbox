import pika
import sys
from config import config
import service
import io
import utils
import requests

ser = service.service()

class RabbitMQManager:
    def __init__(self, rabbitmq_config):
        self.connection_url = self.__get_connection_url(rabbitmq_config)
        self.connection = self.__get_connection(self.connection_url)
        self.chan      = self.connection.channel()
        # self.chan.queue_declare(queue='hello', durable=True)
        self.queue_name = rabbitmq_config["queue_name"]
        self.__init_queue()

    def __get_connection_url(self, rabbitmq_config):
        return "amqp://{}:{}@{}:{}?connection_attempts=10&retry_delay=10".format(rabbitmq_config["user"],
                                                                                 rabbitmq_config["password"],
                                                                                 rabbitmq_config["host"],
                                                                                 rabbitmq_config["port"])

    def __get_connection(self, amqp_url):
        try:
            url_params = pika.URLParameters(amqp_url)
            connection = pika.BlockingConnection(url_params)
        except pika.exceptions as err:
            error_str = "Error while connecting to rabbitmq : " + str(err)
            sys.exit(error_str)
        else:
            return connection

    def receive_msg(self, ch, method, properties, body):
        msg = body.decode('utf-8')
        key = msg["file_cache_key"]
        file_contents = ser.redis_client.get(key)
        file = io.BytesIO(file_contents)
        try:
            serv.aws_client.upload_fileobj(file,config["aws"]["upload_file_bucket"], str(config["aws"]["upload_file_key"]+"/"+str(msg["file_name"])))
            logging.info("AWS S3 - Upload successful")
            headers, data = utils.create_fileUpload_request("uploaded_successfully",msg["file_name"])
            response = requests.put('http://localhost:3500/file/update/status', headers=headers, data=data)
        except Exception as e:
            logging.error("AWS S3- Upload fail")
            headers, data = utils.create_fileUpload_request("upload_failed", msg["file_name"])
            response = requests.put('http://localhost:3500/file/update/status', headers=headers, data=data)
            # sys.exit(error_str)
        ch.basic_ack(delivery_tag=method.delivery_tag)

