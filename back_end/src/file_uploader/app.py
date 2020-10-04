from flask import Flask
from flask_restful import Resource, Api, output_json, reqparse
from flask_cors import CORS
from werkzeug import datastructures, utils
import os
from src.file_uploader import file_uploader_service
from src.file_uploader import file_cache
from src.file_uploader import redis_driver
from src.file_uploader import rabbitmq
# import file_uploader_service
# import file_cache
# import redis_driver
# import rabbitmq

ERROR_FILE_NOT_PROVIDED = "File not provided"
FILE_TEMP_UPLOAD_PATH = "tmp/"

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
    index_cacher = redis_driver.RedisDriver(index_cache_config)
    file_cacher = file_cache.FileCache(file_cache_config)
    queue_manager = rabbitmq.RabbitMQManager(rabbitmq_config)

    svc = file_uploader_service.FileUploader(
        file_cacher, queue_manager, index_cacher)
    return svc


class Ping(Resource):
    def get(self):
        return output_json({"ping": "pong"}, 200)


class UploadFile(Resource):
    def __init__(self, svc):
        self.svc = svc

    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument(
            'file', type=datastructures.FileStorage, location='files')

        args = parse.parse_args()
        data_file = args['file']

        if data_file is None or data_file.filename == '':
            return output_json({"msg": ERROR_FILE_NOT_PROVIDED}, 400)

        file_name = utils.secure_filename(data_file.filename)
        file_path = FILE_TEMP_UPLOAD_PATH+file_name
        data_file.save(file_path)

        result = self.svc.send_file_for_upload(file_path)
        if result["success"]:
            resp = output_json(
                {"msg": file_uploader_service.STATUS_FILE_CACHED}, 201)

        elif result["error"] == file_cache.ERROR_EMPTY_FILE or result["error"] == file_cache.ERROR_FILE_NOT_FOUND:
            resp = output_json({"msg": result["error_msg"]}, 400)

        else:
            resp = output_json({"msg": result["error_msg"]}, 500)

        os.remove(file_path)
        return resp


svc = init(index_cache_config, file_cache_config, rabbitmq_config)

api.add_resource(Ping, '/ping')
api.add_resource(UploadFile, '/file/upload',
                 resource_class_kwargs={"svc": svc})

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False,
            passthrough_errors=True, host='0.0.0.0', port=3000)
