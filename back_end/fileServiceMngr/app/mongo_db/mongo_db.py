from bson import objectid
from fileServiceMngr.app.mongo_db.mongo_dbconf import dbConf

def upload_file(file):
     fs,_ = dbConf()
     fileId = fs.put(file, filename=file.filename)
     return fileId

def list_files():
    fs,db = dbConf()
    return db.fs.files.find()

