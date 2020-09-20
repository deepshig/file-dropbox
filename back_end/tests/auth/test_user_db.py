import pytest
import uuid
import sys
import psycopg2
from psycopg2 import Error
sys.path.append('../')

from src.auth.user_db import UserDB  # NOQA


@pytest.fixture(scope="session")
def test_db():
    test_db_config = {"user": "postgres",
                      "password": "postgres",
                      "host": "127.0.0.1",
                      "port": "5432",
                      "db_name": "user_auth_test"}

    db = UserDB(test_db_config)
    return db


def tear_down(cursor, db_driver):
    cursor.execute("TRUNCATE users;")
    db_driver.connection.commit()
    cursor.close()
    db_driver.connection.close()


def test_create_user(test_db):
    user_details = {"id": uuid.uuid4(),
                    "role": "dummy",
                    "access_token": uuid.uuid4(),
                    "logged_in": True}
    result = test_db.create_user(user_details)
    assert result["user_created"] == True

    fetch_user_query = '''SELECT * FROM users WHERE id = %s'''
    try:
        cursor = test_db.db_driver.connection.cursor()
        cursor.execute(fetch_user_query, [user_details["id"]])
        test_db.db_driver.connection.commit()

        fetched_user = cursor.fetchone()

        assert fetched_user[1] == user_details["role"]
        assert fetched_user[2] == user_details["access_token"]
        assert fetched_user[3] == user_details["logged_in"]
    except psycopg2.Error as err:
        print("Error while checking if user created : ", err)
    finally:
        tear_down(cursor, test_db.db_driver)
