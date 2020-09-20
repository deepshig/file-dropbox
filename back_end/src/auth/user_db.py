# import db_driver
import psycopg2
import uuid
import sys
from psycopg2 import Error, extras
sys.path.append('../')
from . import db_driver  # NOQA

ERROR_USER_NOT_FOUND = "User not found"


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

    def get_user(self, user_id):
        psycopg2.extras.register_uuid()
        get_user_query = '''SELECT id, role, access_token, logged_in, created_at, updated_at FROM users WHERE id = (%s)'''

        cursor = self.db_driver.connection.cursor()
        try:
            cursor.execute(get_user_query, [user_id])
            self.db_driver.connection.commit()
        except psycopg2.Error as err:
            return {"user_fetched": False,
                    "error": err}
        else:
            user = cursor.fetchone()
            if user is not None:
                return {"user_fetched": True,
                        "id": user[0],
                        "role": user[1],
                        "access_token": user[2],
                        "logged_in": user[3]}
            else:
                return {"user_fetched": False,
                        "error": ERROR_USER_NOT_FOUND}
        finally:
            cursor.close()

    def login(self, user_id, access_token):
        psycopg2.extras.register_uuid()
        login_query = '''UPDATE users SET access_token = (%s), logged_in = (%s), updated_at = now() WHERE id = (%s)'''

        cursor = self.db_driver.connection.cursor()
        try:
            cursor.execute(login_query, [access_token, True, user_id])
            self.db_driver.connection.commit()
        except psycopg2.Error as err:
            return {"user_logged_in": False,
                    "error": err}
        else:
            if cursor.rowcount == 1:
                return {"user_logged_in": True}
            else:
                return {"user_logged_in": False,
                        "error": ERROR_USER_NOT_FOUND}
        finally:
            cursor.close()

    def logout(self, user_id):
        psycopg2.extras.register_uuid()
        logout_query = '''UPDATE users SET logged_in = (%s) WHERE id = (%s)'''

        cursor = self.db_driver.connection.cursor()
        try:
            cursor.execute(logout_query, [False, user_id])
            self.db_driver.connection.commit()
        except psycopg2.Error as err:
            return {"user_logged_out": False,
                    "error": err}
        else:
            if cursor.rowcount == 1:
                return {"user_logged_out": True}
            else:
                return {"user_logged_out": False,
                        "error": ERROR_USER_NOT_FOUND}
        finally:
            cursor.close()
