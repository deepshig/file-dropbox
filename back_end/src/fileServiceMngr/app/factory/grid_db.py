
from pymongo import MongoClient
from gridfs import GridFS
from bson import objectid
from config import config
import logging.handlers


class GridFsDatabase(object):
    def __init__(self):
        try:
            self.db = MongoClient(config["db"]["url"]).mygrid #Configure DB url
            self.fs = GridFS(self.db, "fileStorage")
            logging.info("MongoDB GridFS - Connection established")
        except Exception as e:
            print("MongoDB GridFS - Connectopn failes")

    def insert(self, file_content, filename):
        try:
            ob = self.fs.put(file_content, encoding='utf-8', filename=filename)
            logging.info("MongoDB GridFs - Inserted to the MongoDB GridFs")
            print("Insert to MongoDb GridFs", file=sys.stderr)
        except Exception as e:
            print("Unable to insert to MongoDb GridFs", file=sys.stderr)
            logging.error("MongoDB GridFs - Unable to insert to MongoDB GridFs")
            logging.error(e)
            return None
        return ob


    def getFileContents(self,filename):
        try:
            f_id = self.db.fileStorage.files.find_one({"filename": filename}, {"_id": 1})
            file_content = self.fs.get(f_id['_id']).read()
            logging.info("MongoDB GridFs - Read the file contents")
        except Exception as e:
            print("Unable to insert to MongoDb GridFs", file=sys.stderr)
            logging.error("MongoDB GridFs - Unable to read file stored in MongoDB GridFs")
            logging.error(e)
            return None
        return file_content
