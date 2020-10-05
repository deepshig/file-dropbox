from bson import objectid
from mongo_dbconf import dbConf

def upload_file(file):
     fs,_ = dbConf()
     fileId = fs.put(file, filename=file.filename)
     return fileId

def list_files():
    fs,db = dbConf()
    return db.fs.files.find()

