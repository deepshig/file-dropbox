from flask import Flask
from flask_restful import Resource, Api, output_json, reqparse
from flask_cors import CORS
from werkzeug import datastructures, utils
import os
import pathlib
from src.file_uploader import file_uploader_service
from src.file_uploader import file_cache
from src.file_uploader import index_cache
from src.file_uploader import rabbitmq
from src.file_uploader import redis_driver
from src.file_uploader import logger
# import file_uploader_service
# import file_cache
# import index_cache
# import rabbitmq
# import redis_driver
# import logger

INSIDE_CONTAINER = os.environ.get('IN_CONTAINER_FLAG', False)

ERROR_FILE_NOT_PROVIDED = "File not provided"
ERROR_FILE_STATUS_NOT_PROVIDED = "File status not provided"
ERROR_FILE_NAME_NOT_PROVIDED = "File name not provided"
ERROR_USER_ID_NOT_PROVIDED = "User ID not provided"
ERROR_USER_NAME_NOT_PROVIDED = "User name not provided"
ERROR_FILE_METADATA_NOT_PROVIDED = "File metadata not provided"
ERROR_INVALID_FILE_STATUS = "File status is invalid"
ERROR_FILE_DOES_NOT_EXIST = "File does not exist"
ERROR_MAX_ATTEMPTS_FOR_FILE_UPLOAD_REACHED = "File upload has been retried max number of times"
ERROR_INTERNAL_SERVER = "Internal Server Error"

accepted_file_status = ["uploaded_successfully", "upload_failed"]

LOG_FILE_PATH = "logs/log_file.txt"

if INSIDE_CONTAINER:
    FILE_TEMP_UPLOAD_PATH = "tmp/"
else:
    FILE_TEMP_UPLOAD_PATH = os.path.abspath(pathlib.Path().absolute()) + '/'

if not os.path.exists(FILE_TEMP_UPLOAD_PATH):
    os.makedirs(FILE_TEMP_UPLOAD_PATH)

app = Flask(__name__)
CORS(app, supports_credentials=True)

api = Api(app)
CORS(app, supports_credentials=True)


if INSIDE_CONTAINER:
    index_cache_config = {"host": "redis",
                          "port": 6379}

    file_cache_config = {"host": "redis",
                         "port": 6379}

    file_rabbitmq_config = {"user": "guest",
                            "password": "guest",
                            "host": "rabbitmq",
                            "port": "5672",
                            "connection_timeout_s": 1200,
                            "idle_connection_timeout_s": 1800,
                            "connection_retry_s": 5,
                            "queue_name": "file_uploads_queue"}

    user_rabbitmq_config = {"user": "guest",
                            "password": "guest",
                            "host": "rabbitmq",
                            "port": "5672",
                            "connection_timeout_s": 1200,
                            "idle_connection_timeout_s": 1800,
                            "connection_retry_s": 5,
                            "queue_name": "user_notification_queue"}

    admin_rabbitmq_config = {"user": "guest",
                             "password": "guest",
                             "host": "rabbitmq",
                             "port": "5672",
                             "connection_timeout_s": 1200,
                             "idle_connection_timeout_s": 1800,
                             "connection_retry_s": 5,
                             "queue_name": "admin_notification_queue"}
else:
    index_cache_config = {"host": "127.0.0.1",
                          "port": 6379}

    file_cache_config = {"host": "127.0.0.1",
                         "port": 6379}

    file_rabbitmq_config = {"user": "guest",
                            "password": "guest",
                            "host": "127.0.0.1",
                            "port": "5672",
                            "connection_timeout_s": 1200,
                            "idle_connection_timeout_s": 1800,
                            "connection_retry_s": 5,
                            "queue_name": "file_uploads_queue"}

    user_rabbitmq_config = {"user": "guest",
                            "password": "guest",
                            "host": "127.0.0.1",
                            "port": "5672",
                            "connection_timeout_s": 1200,
                            "idle_connection_timeout_s": 1800,
                            "connection_retry_s": 5,
                            "queue_name": "user_notification_queue"}

    admin_rabbitmq_config = {"user": "guest",
                             "password": "guest",
                             "host": "127.0.0.1",
                             "port": "5672",
                             "connection_timeout_s": 1200,
                             "idle_connection_timeout_s": 1800,
                             "connection_retry_s": 5,
                             "queue_name": "admin_notification_queue"}


class Ping(Resource):
    def get(self):
        logger.log_ping()
        return output_json({"ping": "pong"}, 200)


class UploadFile(Resource):
    def __init__(self, file_cacher, file_queue_manager, user_queue_manager, admin_queue_manager, index_cacher):
        self.svc = file_uploader_service.FileUploader(
            file_cacher, file_queue_manager, user_queue_manager, admin_queue_manager, index_cacher)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=datastructures.FileStorage, location='files',
                            help=ERROR_FILE_NOT_PROVIDED)
        parser.add_argument('user_id', required=True, type=str,
                            help=ERROR_USER_ID_NOT_PROVIDED)
        parser.add_argument('user_name', required=True, type=str,
                            help=ERROR_USER_NAME_NOT_PROVIDED)
        parser.add_argument('metadata', required=True,
                            type=str, help=ERROR_FILE_METADATA_NOT_PROVIDED)

        args = parser.parse_args()
        data_file, metadata = args['file'], args['metadata']
        user_id, user_name = args['user_id'], args['user_name']

        logger.log_upload_req_received(user_id, user_name)

        if data_file is None or data_file.filename == '':
            logger.log_upload_bad_request(
                user_id, user_name, ERROR_FILE_NOT_PROVIDED)
            return output_json({"msg": ERROR_FILE_NOT_PROVIDED}, 400)

        file_name = utils.secure_filename(data_file.filename)
        file_path = FILE_TEMP_UPLOAD_PATH + file_name
        data_file.save(file_path)

        result = self.svc.send_file_for_upload(
            file_path, user_id, user_name, metadata)
        if result["success"]:
            logger.log_upload_success(user_id, user_name)
            resp = output_json({"msg": index_cache.STATUS_FILE_CACHED,
                                "file_id": result["file_name"]}, 201)

        elif result["error"] == file_cache.ERROR_EMPTY_FILE or result["error"] == file_cache.ERROR_FILE_NOT_FOUND:
            logger.log_upload_bad_request(
                user_id, user_name, result["error_msg"])
            resp = output_json({"msg": result["error_msg"]}, 400)

        else:
            logger.log_upload_internal_server_error(
                user_id, user_name, result["error_msg"])
            resp = output_json({"msg": ERROR_INTERNAL_SERVER}, 500)

        os.remove(file_path)
        return resp


class UpdateFileStatus(Resource):
    def __init__(self, file_cacher, file_queue_manager, user_queue_manager, admin_queue_manager, index_cacher):
        self.svc = file_uploader_service.FileUploader(
            file_cacher, file_queue_manager, user_queue_manager, admin_queue_manager, index_cacher)

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file_status', required=True, type=str,
                            help=ERROR_FILE_STATUS_NOT_PROVIDED)
        parser.add_argument('file_name', required=True, type=str,
                            help=ERROR_FILE_NAME_NOT_PROVIDED)
        parser.add_argument('user_id', required=True, type=str,
                            help=ERROR_USER_ID_NOT_PROVIDED)
        parser.add_argument('user_name', required=True, type=str,
                            help=ERROR_USER_NAME_NOT_PROVIDED)
        parser.add_argument('error_msg', type=str)

        args = parser.parse_args()
        file_status, file_name = args["file_status"], args["file_name"]
        user_id, user_name = args["user_id"], args["user_name"]

        logger.log_status_update_req_received(
            user_id, user_name, file_name, file_status)

        if file_status not in accepted_file_status:
            logger.log_status_update_bad_request(
                user_id, user_name, file_name, file_status, ERROR_INVALID_FILE_STATUS)
            return output_json({"msg": ERROR_INVALID_FILE_STATUS}, 400)

        if file_status == accepted_file_status[0]:
            result = svc.delete_uploaded_file(file_name, user_id, user_name)
            if not result["success"]:
                if result["error"] == redis_driver.ERROR_KEY_NOT_FOUND:
                    logger.log_status_update_bad_request(
                        user_id, user_name, file_name, file_status, ERROR_FILE_DOES_NOT_EXIST)
                    return output_json(
                        {"msg": ERROR_FILE_DOES_NOT_EXIST}, 400)
                else:
                    logger.log_status_update_internal_server_error(
                        user_id, user_name, file_name, file_status, result["error_msg"])
                    return output_json({"msg": ERROR_INTERNAL_SERVER}, 500)

        elif file_status == accepted_file_status[1]:
            result = svc.handle_failed_upload(file_name, user_id, user_name)
            if not result["success"]:
                if result["error"] == index_cache.ERROR_MAX_ATTEMPTS_REACHED:
                    logger.log_status_update_max_retries(
                        user_id, user_name, file_name, file_status)
                    return output_json(
                        {"msg": ERROR_MAX_ATTEMPTS_FOR_FILE_UPLOAD_REACHED}, 200)
                else:
                    logger.log_status_update_internal_server_error(
                        user_id, user_name, file_name, file_status, result["error"])
                    return output_json({"msg": ERROR_INTERNAL_SERVER}, 500)

        logger.log_status_update_success(
            user_id, user_name, file_name, file_status)
        return output_json({"msg": "success"}, 200)


index_cacher = index_cache.IndexCache(index_cache_config)
file_cacher = file_cache.FileCache(file_cache_config)
file_queue_manager = rabbitmq.RabbitMQManager(file_rabbitmq_config)
user_queue_manager = rabbitmq.RabbitMQManager(user_rabbitmq_config)
admin_queue_manager = rabbitmq.RabbitMQManager(admin_rabbitmq_config)

api.add_resource(Ping, '/ping')
api.add_resource(UploadFile, '/file/upload',
                 resource_class_kwargs={"file_cacher": file_cacher,
                                        "file_queue_manager": file_queue_manager,
                                        "user_queue_manager": user_queue_manager,
                                        "admin_queue_manager": admin_queue_manager,
                                        "index_cacher": index_cacher})
api.add_resource(UpdateFileStatus, '/file/update/status',
                 resource_class_kwargs={"file_cacher": file_cacher,
                                        "file_queue_manager": file_queue_manager,
                                        "user_queue_manager": user_queue_manager,
                                        "admin_queue_manager": admin_queue_manager,
                                        "index_cacher": index_cacher})

if __name__ == '__main__':
    logger.setup(LOG_FILE_PATH)

    logger.log_server_start()
    app.run(debug=True, use_debugger=False, use_reloader=False,
            passthrough_errors=True, host='0.0.0.0', port=3500)
