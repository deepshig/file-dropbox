from datetime import datetime


def create_fileUpload_request(file_status, file_name, user_id, user_name):
    headers = {
        'accept':'application/json',
    }
    data = {
       'file_status':file_status,
       'file_name':file_name,
       'user_id': user_id,
       'user_name': user_name

    }
    return headers, data


def create_mongoDb_insert_obj(msg):
    dict = {}
    dict["clientName"] = msg["user_name"]
    dict["clientId"] = msg["user_id"]
    dict["filename"] = msg["file_name"]
    dict["activity"] = 1
    dict["created"] = datetime.now()
    return dict
