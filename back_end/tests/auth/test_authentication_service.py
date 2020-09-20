import pytest
import uuid
import sys
import psycopg2
from psycopg2 import Error
sys.path.append('../')

from src.auth.user_db import ERROR_USER_NOT_FOUND  # NOQA
from src.auth.authentication_service import Authenticator, ERROR_UNAUTHORISED_REQUEST  # NOQA

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


def test_get_user():
    """
    failure : user does not exist
    """
    auth = Authenticator(test_db_config)
    user_id = uuid.uuid4()
    access_token = uuid.uuid4()

    fetched_user = auth.get_user(user_id, access_token)
    assert fetched_user["user_fetched"] == False
    assert fetched_user["error"] == ERROR_USER_NOT_FOUND

    """
    failure : user not authorrised to view this user
    """
    correct_access_token = uuid.uuid4()
    create_user_query = '''INSERT INTO users(id, role, access_token, logged_in, created_at, updated_at) VALUES ((%s), (%s), (%s), (%s), now(), now())'''
    cursor = auth.db.db_driver.connection.cursor()
    psycopg2.extras.register_uuid()

    try:
        cursor.execute(create_user_query, [
            user_id, "admin", correct_access_token, False])
        auth.db.db_driver.connection.commit()
    except psycopg2.Error as err:
        print("Error in creating test user : ", err)

    fetched_user = auth.get_user(user_id, access_token)
    assert fetched_user["user_fetched"] == False
    assert fetched_user["error"] == ERROR_UNAUTHORISED_REQUEST

    """
    success
    """
    fetched_user = auth.get_user(user_id, correct_access_token)
    assert fetched_user["user_fetched"] == True
    assert fetched_user["id"] == user_id
    assert fetched_user["access_token"] == correct_access_token
    assert fetched_user["role"] == "admin"
    assert fetched_user["logged_in"] == False

    tear_down(cursor, auth.db.db_driver)
