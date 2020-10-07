import pika
import sys
import json
import service
import utils
import logging
import requests
import io
from config import config

logging.basicConfig(filename=config["logging"]["file_path"], filemode="a+", format='%(asctime)s %(levelname)s-%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

serv = service.service()


class RabbitMQManager:
    def __init__(self):
        self.connection_url = self.__get_connection_url()
        self.connection = self.__get_connection(self.connection_url)
        self.chan = self.connection.channel()
        self.queue_name = config["rabbitmq_config"]["queue_name"]
        self.chan.queue_declare(queue=self.queue_name, durable=True)

    def __get_connection_url(self):
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

    def receive_msg(self, ch, method, properties, body):
        msg_json = body.decode('utf-8')
        msg = json.loads(msg_json)
        # print(msg)
        key = msg["file_cache_key"]
        file_contents = serv.redis_client.get(key)
        # print(file_contents)
        file = io.BytesIO(bytes(file_contents["value"]))
        try:
            serv.aws_client.upload_fileobj(file, config["aws"]["upload_file_bucket"], str(
                config["aws"]["upload_file_key"]+"/"+str(msg["file_name"])))
            logging.info("AWS S3 - Upload successful")
            # print(msg["file_name"])
            url = '%s/%s/%s' % (serv.aws_client.meta.endpoint_url,
                                config["aws"]["upload_file_bucket"],  str(
                config["aws"]["upload_file_key"]+"/"+str(msg["file_name"])))
            req_obj = utils.create_mongoDb_insert_obj(msg)
            req_obj["url"] = url
            inserted_id = serv.mongo_client.create(req_obj)
            logging.info("File Uploaded Successfully")
            headers, data = utils.create_fileUpload_request(
                "uploaded_successfully", msg["file_name"])
            response = requests.put(
                'http://localhost:3500/file/update/status', headers=headers, data=data)
            if response:
                logging.info("Consumer Task Completed")
            else:
                logging.error("Consumer Task Failed")
        except Exception as e:
            logging.error("AWS S3- Upload fail")
            headers, data = utils.create_fileUpload_request(
                "upload_failed", msg["file_name"])
            response = requests.put(
                'http://localhost:3500/file/update/status', headers=headers, data=data)
            # print(response.body)
            # sys.exit(error_str)
        ch.basic_ack(delivery_tag=method.delivery_tag)
