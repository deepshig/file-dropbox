import uuid
from . import user_db


class Authenticator:
    def __init__(self, db_config):
        self.db = user_db.UserDB(db_config)

    def create_user(self, role):
        user_details = {"id": uuid.uuid4(),
                        "role": role,
                        "access_token": uuid.uuid4(),
                        "logged_in": True}

        result = self.db.create_user(user_details)
        if result["user_created"]:
            return user_details
        else:
            return result
