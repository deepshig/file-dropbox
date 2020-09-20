import psycopg2
import uuid
import sys
from psycopg2 import Error, extras
sys.path.append('../')
from . import db_driver  # NOQA
# from db_driver import DBDriver  # NOQA


class UserDB:
    def __init__(self, db_config):
        self.db_driver = db_driver.DBDriver()
        self.db_driver.connect(db_config)
        self.db_driver.create_users_table()

    def create_user(self, user_details):
        psycopg2.extras.register_uuid()
        create_user_query = '''INSERT INTO users(id, role, access_token, logged_in, created_at, updated_at) VALUES ((%s), (%s), (%s), (%s), now(), now())'''

        cursor = self.db_driver.connection.cursor()
        try:
            cursor.execute(create_user_query, [user_details["id"],
                                               user_details["role"],
                                               user_details["access_token"],
                                               user_details["logged_in"]])
            self.db_driver.connection.commit()
        except psycopg2.Error as err:
            return {"user_created": False,
                    "error": err}
        else:
            return {"user_created": True}
        finally:
            cursor.close()


db_config = {"user": "postgres",
             "password": "postgres",
             "host": "127.0.0.1",
             "port": "5432",
             "db_name": "user_auth_test"}

user_details = {"id": str(uuid.uuid4()),
                "role": "dummy",
                "access_token": uuid.uuid4(),
                "logged_in": True}x
