from pymongo import MongoClient
from config import config
import logging.handlers
import sys

# logger = logging.getLogger()
# fh = logging.handlers.RotatingFileHandler(filename=config["logging"]["file_path"], maxBytes=10240, backupCount=5)
# #fh.setLevel(logging.DEBUG)#no matter what level I set here
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# logger.addHandler(fh)
# logger.setLevel(logging.INFO)


class MongoDatabase(object):
     def __init__(self):

          try:
               self.client = MongoClient(config["db"]["url"])  # configure db url
               self.db = self.client[config["db"]["name"]] # configure db name
               logging.info("MongoDB - Connection established")
               print("Connection to MongoDb established", file=sys.stderr)
          except Exception as e:
               print("Connectopn failes")
               #logging.error("MongoDB - Unable to connect")

     def insert(self, dict):
          logging.info(dict)
          try:
               inserted = self.db["fileInfo"].insert_one(dict) # insert data to db
               logging.info("MongoDB - Inserted to the MongoDB")
               print("Insert to MongoDb", file=sys.stderr)

          except Exception as e:
               print("Unable to insert to MongoDb", file=sys.stderr)
               logging.error("MongoDB - Unable to insert")
               logging.error(e)
          return str(inserted.inserted_id)

     def find(self, clientId, cursor=False):  # find all from db
         try:
               found = self.db["fileInfo"].find({ "clientId": str(clientId) })
               found = list(found)
               for i in range(len(found)):  # to serialize object id need to convert string
                    if "_id" in found[i]:
                         found[i]["_id"] = str(found[i]["_id"])
               logging.info("MongoDB - Got client History")
         except Exception as e:
                print("coneection failed")
                logging.error("MongoDB - Unable to search")
         return found

