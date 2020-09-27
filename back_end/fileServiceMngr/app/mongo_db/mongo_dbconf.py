from pymongo import MongoClient
from gridfs import GridFs

def dbConf():
    db = MongoClient().mygrid
    fs = GridFs(db)
    return fs, db