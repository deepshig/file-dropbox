# import pymongo
#
# client = pymongo.MongoClient("mongodb://:27017/")
#
# db = client["test_database"]
#
# courses = db["course"]
#
#
# dict = {"name":"Shubham","activity":"test"}
#
#
# x = courses.insert_one(dict)
# print(x)

# import boto3
# import os
#
# client = boto3.client('s3',
#                         aws_access_key_id = "AKIA5UVQCCOP2IPAQU5J",
#                         aws_secret_access_key = "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")
#
#
# file = open('saveimg_h50_w50_score1_search20.jpg','rb')
# upload_file_bucket = 'weightsbucket'
# upload_file_key = 'weights/' + str(file)
# print(upload_file_key)
# client.upload_fileobj(file, upload_file_bucket, str(upload_file_key))

#import redis
from flask import Flask
import logging

logging.basicConfig(filename="/logs/logFile.txt",filemode="a+",format='%(asctime)s %(levelname)s-%(message)s',
                     datefmt='%Y-%m-%d %H:%M:%S')


app = Flask(__name__)
#redis = redis.Redis(host='redis', port=6379, db=0)
@app.route('/')
def hello_world():
    return 'Hello, World!'
@app.route('/visitor')
def visitor():
    #redis.incr('visitor')
    #visitor_num = redis.get('visitor').decode("utf-8")
    logging.warning('visitor API')
    return "Visitor: %s" % (1)
@app.route('/visitor/reset')
def reset_visitor():
    #redis.set('visitor', 0)
    #visitor_num = redis.get('visitor').decode("utf-8")
    logging.warning('Reset API')
    return "Visitor is reset to %s" % (2)
if __name__ == '__main__':
    app.run(host='0.0.0.0')


# @app.route('/client/history/<client_id>', methods=['GET'])
# def getClientHistory(client_id) -> str:
#     clientId = client_id
#     return json.dumps({'client_history': clients_history(clientId)})
#
# @app.route('/file/upload', methods=['GET','POST'])
# def fileUpload():
#     if request.method == 'POST':
#         if request.files:
#            file = request.files["file"]
#            print("Request form",file=sys.stderr)
#            app.logger.info(request.form)
#            id,col = update_col(request.form,file,mongo)
#            succ = update_client_history(request.form,id,file.filename)
#            return json.dumps({"filename": file.filename, "mongo_db_id":str(id)})
#     return make_response(jsonify(success=False))


# @app.route('/client/list',methods=['GET'])
# def lstfiles():
#     return json.dumps({'files':list_files()})


# @app.route('/clients/update/<client_id>', methods=['GET','POST'])
# def updateClientHistory(client_id) -> str:
#     if request.method == 'POST':
#         clientId = client_id
#         req_data = request.json
#         succ=update_client_history(clientId,req_data)
#         return make_response(jsonify(success=succ))
#     return make_response(jsonify(success=False))















