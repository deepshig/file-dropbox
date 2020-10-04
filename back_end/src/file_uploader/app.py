from flask import Flask
from flask_restful import Resource, Api, output_json, reqparse
from flask_cors import CORS
from src.file_uploader import file_uploader_service
from src.file_uploader import file_cache
from src.file_uploader import redis
from src.file_uploader import rabbitmq

app = Flask(__name__)
CORS(app, supports_credentials=True)

api = Api(app)
CORS(app, supports_credentials=True)

index_cache_config = {"host": "127.0.0.1",
                     "port": 6379}

file_cache_config = {"host": "127.0.0.1",
                     "port": 6379}

rabbitmq_config = {"user": "guest",
                   "password": "guest",
                   "host": "127.0.0.1",
                   "port": "5672",
                   "queue_name": "file_uploads_queue"}

def init(index_cache_config, file_cache_config, rabbitmq_config):
    index_cacher = redis.RedisDriver(index_cache_config)
    file_cacher = file_cache.FileCache(file_cache_config)
    queue_manager = rabbitmq.RabbitMQManager(rabbitmq_config)

    svc = file_uploader_service.FileUploader(file_cacher, queue_manager, index_cacher)
    return svc

class Ping(Resource):
    def get(self):
        return output_json({"ping": "pong"}, 200)

svc = init(index_cache_config, file_cache_config, rabbitmq_config)

api.add_resource(Ping, '/ping')

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False,
            passthrough_errors=True, host='0.0.0.0', port=3000)


