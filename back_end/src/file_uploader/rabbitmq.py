import pika
import sys


class RabbitMQManager:
    def __init__(self, amqp_url, queue_name):
        self.connection = self.__get_connection(amqp_url)
        self.queue_name = queue_name
        self.__init_queue()

    def __get_connection(self, amqp_url):
        try:
            url_params = pika.URLParameters(amqp_url)
            connection = pika.BlockingConnection(url_params)
            return connection
        except pika.exceptions as err:
            error_str = "Error while connecting to rabbitmq : " + str(err)
            sys.exit(error_str)

    def __init_queue(self):
        try:
            chan = self.connection.channel()
            chan.queue_declare(queue=self.queue_name, durable=True)
            return
        except pika.exceptions as err:
            error_str = "Error while creating queue : " + str(err)
            sys.exit(error_str)

    def shutdown_queue(self):
        chan = self.connection.channel()
        chan.close()
        self.connection.close()
        return
