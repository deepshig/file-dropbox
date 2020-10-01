import pika
import sys


class RabbitMQManager:
    def __init__(self, rabbitmq_config):
        self.connection_url = self.__get_connection_url(rabbitmq_config)
        self.connection = self.__get_connection(self.connection_url)
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

    def __init_queue(self):
        try:
            chan = self.connection.channel()
            chan.queue_declare(queue=self.queue_name, durable=True)
        except pika.exceptions as err:
            error_str = "Error while creating queue : " + str(err)
            sys.exit(error_str)
        else:
            return

    def shutdown_queue(self):
        chan = self.connection.channel()
        chan.close()
        self.connection.close()
        return

    def publish(self, message_body):
        try:
            chan = self.connection.channel()
            chan.basic_publish(exchange='', routing_key=self.queue_name,
                               body=message_body, properties=pika.BasicProperties(delivery_mode=2))
        except pika.exceptions as err:
            err_str = "Error while publishing message to queue=" + \
                self.queue_name + " : " + str(err)
            return {"message_published": False,
                    "error": err_str}
        else:
            return {"message_published": True}
        finally:
            if chan is not None:
                chan.close()
