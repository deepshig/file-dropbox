from flask import Flask, request, jsonify, make_response

import json

from sql_db import clients_history, update_client_history

from mongo_db import upload_file, list_files


app = Flask(__name__)

'''
Route for getting client history - Uploads, Downloads done by the client
@returns - dict of jsons with keys uid, fileId, activity        
'''
@app.route('/clients/history/<client_id>', methods=['GET'])
def getClientHistory(client_id) -> str:
    clientId = client_id
    return json.dumps({'client_history': clients_history(clientId)})

'''
Route for updating clients_history table
@returns json - {"success":true}/{"success":false}
'''
@app.route('/clients/update/<client_id>', methods=['GET','POST'])
def updateClientHistory(client_id) -> str:
    if request.method == 'POST':
        clientId = client_id
        req_data = request.json
        succ=update_client_history(clientId,req_data)
        return make_response(jsonify(success=succ))
    return make_response(jsonify(success=False))

'''
Route for uploading the file to MongoDb
@returns json - {"success":False} - Incase of any failure
                {"fileId":id of the file on mongodb database incase of success} 
'''
@app.route('/file/upload', methods=['GET','POST'])
def fileUpload():
    if request.method == 'POST':
        if request.files:
           file = request.files["file"]
           fileId = upload_file(file)
           return json.dumps({"fileId":fileId})
    return make_response(jsonify(success=False))

@app.route('/file/list',method=['GET'])
def lstfiles():
    return json.dumps({'files':list_files()})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500)
