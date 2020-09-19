import sys
import psycopg2
from psycopg2 import Error


class DBDriver:
    def __init__(self):
        self.connection = None

    def connect(self, db_config):
        try:
            self.connection = psycopg2.connect(user=db_config["user"],
                                               password=db_config["password"],
                                               host=db_config["host"],
                                               port=db_config["port"],
                                               database=db_config["db_name"])
        except psycopg2.Error as err:
            error_str = "Error while connecing to Authentication DB : " + \
                str(err)
            sys.exit(error_str)

    def shutdown(self):
        self.connection.close()

    def create_users_table(self):
        cursor = self.connection.cursor()

        create_table_query = '''CREATE TABLE IF NOT EXISTS users (
                                    id UUID PRIMARY KEY NOT NULL,
                                    role VARCHAR NOT NULL,
                                    access_token UUID,
                                    logged_in BOOL DEFAULT FALSE NOT NULL,
                                    created_at TIMESTAMP,
                                    updated_at TIMESTAMP);'''

        try:
            cursor.execute(create_table_query)
            self.connection.commit()
        except psycopg2.Error as err:
            error_str = "Error while creating table for Authentication DB : " + \
                str(err)
            sys.exit(error_str)
        finally:
            cursor.close()
