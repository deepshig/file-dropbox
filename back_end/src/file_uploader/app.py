from flask import Flask
from flask_restful import Resource, Api, output_json, reqparse
from flask_cors import CORS
from werkzeug import datastructures, utils
import os
# from src.file_uploader import file_uploader_service
# from src.file_uploader import file_cache
# from src.file_uploader import redis_driver
# from src.file_uploader import rabbitmq
import file_uploader_service
import file_cache
import redis_driver
import rabbitmq
import pathlib

ERROR_FILE_NOT_PROVIDED = "File not provided"
ERROR_FILE_STATUS_NOT_PROVIDED = "File status not provided"
ERROR_FILE_NAME_NOT_PROVIDED = "File name not provided"
ERROR_INVALID_FILE_STATUS = "File status is invalid"
ERROR_INVALID_FILE_NAME = "File name is invalid"
ERROR_INTERNAL_SERVER = "Internal Server Error"

accepted_file_status = ["uploaded_successfully", "upload_failed"]
FILE_TEMP_UPLOAD_PATH = "tmp/"
FILE_TEMP_UPLOAD_PATH = os.path.abspath(pathlib.Path().absolute()) + '/'

app = Flask(__name__)
CORS(app, supports_credentials=True)

api = Api(app)
CORS(app, supports_credentials=True)

#################################################
#       Local Testing configs                   #
#################################################
# index_cache_config = {"host": "127.0.0.1",
#                       "port": 6379}
#
# file_cache_config = {"host": "127.0.0.1",
#                      "port": 6379}
#
# rabbitmq_config = {"user": "guest",
#                    "password": "guest",
#                    "host": "127.0.0.1",
#                    "port": "5672",
#                    "queue_name": "file_uploads_queue"}

#################################################
#       Docker Testing configs                  #
#################################################
index_cache_config = {"host": "redis",
                      "port": 6379}

file_cache_config = {"host": "redis",
                     "port": 6379}

rabbitmq_config = {"user": "guest",
                   "password": "guest",
                   "host": "rabbitmq",
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
            resp = output_json({"msg": ERROR_INTERNAL_SERVER}, 500)

        os.remove(file_path)
        return resp


class UpdateFileStatus(Resource):
    def __init__(self, svc):
        self.svc = svc

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file_status', required=True, type=str,
                            help=ERROR_FILE_STATUS_NOT_PROVIDED)
        parser.add_argument('file_name', required=True, type=str,
                            help=ERROR_FILE_NAME_NOT_PROVIDED)
        parser.add_argument('error_msg', type=str)

        args = parser.parse_args()
        file_status, file_name = args["file_status"], args["file_name"]

        if file_status not in accepted_file_status:
            return output_json({"msg": ERROR_INVALID_FILE_STATUS}, 400)

        response = output_json({"msg": "success"}, 200)

        if file_status == accepted_file_status[0]:
            result = svc.delete_uploaded_file(file_name)
            if not result["success"]:
                if result["error"] == redis_driver.ERROR_KEY_NOT_FOUND:
                    result["error_msg"] = "Failed to update file status : " + \
                        ERROR_INVALID_FILE_NAME
                    response = output_json({"msg": result["error_msg"]}, 400)
                else:
                    response = output_json({"msg": ERROR_INTERNAL_SERVER}, 500)

        return response


svc = init(index_cache_config, file_cache_config, rabbitmq_config)

api.add_resource(Ping, '/ping')
api.add_resource(UploadFile, '/file/upload',
                 resource_class_kwargs={"svc": svc})
api.add_resource(UpdateFileStatus, '/file/update/status',
                 resource_class_kwargs={"svc": svc})

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False,
            passthrough_errors=True, host='0.0.0.0', port=3500)
