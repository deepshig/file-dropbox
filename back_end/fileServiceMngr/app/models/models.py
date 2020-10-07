from factory.mongo_db import MongoDatabase


class model(object):
    def __init__(self):

        self.db = MongoDatabase()
        self.fields = {
            "clientName": "string",
            "clientId": "string",
            "fileName": "string",
            "activity": "int",
            "url"     : "string",
            "created": "datetime"
        }



    def create(self, req,filename,url):
        res = self.db.insert(req,filename,url)
        return  res

    def find(self, clientId): # find all
        return self.db.find(clientId)

    def find_by_id(self, id):
        return self.db.find_by_id(id, self.collection_name)

    # TODO

    def update(self, id, todo):
        self.validator.validate(todo, self.fields, self.update_required_fields, self.update_optional_fields)
        return self.db.update(id, todo,self.collection_name)

    def delete(self, id):
        return self.db.delete(id, self.collection_name)

