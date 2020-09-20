import pytest
import uuid
import sys
import psycopg2
from psycopg2 import Error
sys.path.append('../')

from src.auth.user_db import UserDB, ERROR_USER_NOT_FOUND  # NOQA
from src.auth.authentication_service import Authenticator  # NOQA

test_db_config = {"user": "postgres",
                  "password": "postgres",
                  "host": "127.0.0.1",
                  "port": "5432",
                  "db_name": "user_auth_test"}


def tear_down(cursor, db_driver):
    cursor.execute("TRUNCATE users;")
    db_driver.connection.commit()
    cursor.close()
    db_driver.connection.close()


def test_create_user():
    """
    success
    """
    auth = Authenticator(test_db_config)
    result = auth.create_user("admin")
    assert result["role"] == "admin"

    cursor = auth.db.db_driver.connection.cursor()
    get_user_query = '''SELECT id, role, access_token, logged_in, created_at, updated_at FROM users WHERE id = (%s)'''

    try:
        cursor.execute(get_user_query, [result["id"]])
        auth.db.db_driver.connection.commit()
        assert cursor.fetchone() is not None
    except psycopg2.Error as err:
        print("Error while fetching the test user : ", err)
    finally:
        tear_down(cursor, auth.db.db_driver)
