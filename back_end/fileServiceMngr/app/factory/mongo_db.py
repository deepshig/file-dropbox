from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import sys
from config import config
import logging

logging.basicConfig(filename=config["logging"]["file_path"],filemode="a+",format='%(asctime)s %(levelname)s-%(message)s',
                     datefmt='%Y-%m-%d %H:%M:%S')

class MongoDatabase(object):
     def __init__(self):
          try:
               self.client = MongoClient(config["db"]["url"])  # configure db url
               self.db = self.client[config["db"]["name"]] # configure db name
               logging.info("MongoDB - Connection established")
               print("Connection to MongoDb established", file=sys.stderr)
          except Exception as e:
               logging.error("MongoDB - Unable to connect")

     def insert(self, req,filename,url):
          dict = {}
          dict["clientName"] = req.get("clientName")[0]
          dict["clientId"]   =   req.get("clientId")[0]
          dict["filename"]   = filename
          dict["activity"]   = req.get("activity")[0]
          dict["url"]        = url
          dict["created"]   = datetime.now()
          try:
               inserted = self.db["fileInfo"].insert_one(dict) # insert data to db
               logging.info("MongoDB - Inserted to the MongoDB")
               print("Insert to MongoDb", file=sys.stderr)
          except Exception as e:
               print("Unable to insert to MongoDb", file=sys.stderr)
               logging.error("MongoDB - Unable to insert")
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
                logging.error("MongoDB - Unable to search")
         return found

