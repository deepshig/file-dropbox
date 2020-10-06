
def create_fileUpload_request(file_status, file_name):
    headers = {
        'accept':'application/json',
    }
    data = {
       'file_status':file_status,
       'file_name':file_name
    }
    return headers, data