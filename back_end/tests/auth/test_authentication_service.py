import pytest
import uuid
import sys
import psycopg2
from psycopg2 import Error
sys.path.append('../')

from src.auth.user_db import UserDB, ERROR_USER_NOT_FOUND  # NOQA
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
    db = UserDB(test_db_config)
    auth = Authenticator(db)

    result = auth.create_user("admin")
    assert result["user_created"] == True
    assert result["role"] == "admin"

    cursor = auth.db.db_driver.connection.cursor()
    fetched_user = get_test_user(auth.db, cursor, result["id"])
    assert fetched_user["user_fetched"] == True
    assert fetched_user["role"] == "admin"

    tear_down(cursor, auth.db.db_driver)


def test_get_user():
    """
    failure : user does not exist
    """
    db = UserDB(test_db_config)
    auth = Authenticator(db)

    user_id = uuid.uuid4()
    access_token = uuid.uuid4()

    fetched_user = auth.get_user(user_id, access_token)
    assert fetched_user["user_fetched"] == False
    assert fetched_user["error"] == ERROR_USER_NOT_FOUND

    """
    failure : user not authorrised to view this user
    """
    correct_access_token = uuid.uuid4()
    cursor = auth.db.db_driver.connection.cursor()
    create_test_user(auth.db, cursor, user_id, correct_access_token)

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


def test_login():
    db = UserDB(test_db_config)
    auth = Authenticator(db)

    user_id = uuid.uuid4()
    """
    failure : user does not exit
    """
    result = auth.login(user_id)
    assert result["user_logged_in"] == False
    assert result["error"] == ERROR_USER_NOT_FOUND

    """
    success
    """
    cursor = auth.db.db_driver.connection.cursor()
    create_test_user(auth.db, cursor, user_id, uuid.uuid4())
    result = auth.login(user_id)
    assert result["user_logged_in"] == True

    fetched_user = get_test_user(auth.db, cursor, user_id)
    assert fetched_user["user_fetched"] == True
    assert fetched_user["id"] == user_id
    assert fetched_user["logged_in"] == True


def test_logout():
    db = UserDB(test_db_config)
    auth = Authenticator(db)

    user_id = uuid.uuid4()
    """
    failure : user does not exit
    """
    result = auth.logout(user_id)
    assert result["user_logged_out"] == False
    assert result["error"] == ERROR_USER_NOT_FOUND

    """
    success
    """
    cursor = auth.db.db_driver.connection.cursor()
    create_test_user(auth.db, cursor, user_id, uuid.uuid4())
    result = auth.logout(user_id)
    assert result["user_logged_out"] == True

    fetched_user = get_test_user(auth.db, cursor, user_id)
    assert fetched_user["user_fetched"] == True
    assert fetched_user["id"] == user_id
    assert fetched_user["logged_in"] == False


def create_test_user(db, cursor, user_id, access_token):
    create_user_query = '''INSERT INTO users(id, role, access_token, logged_in, created_at, updated_at) VALUES ((%s), (%s), (%s), (%s), now(), now())'''
    psycopg2.extras.register_uuid()

    try:
        cursor.execute(create_user_query, [
            user_id, "admin", access_token, False])
        db.db_driver.connection.commit()
    except psycopg2.Error as err:
        print("Error in creating test user : ", err)


def get_test_user(db, cursor, user_id):
    get_user_query = '''SELECT id, role, access_token, logged_in, created_at, updated_at FROM users WHERE id = (%s)'''
    try:
        cursor.execute(get_user_query, [user_id])
        db.db_driver.connection.commit()
    except psycopg2.Error as err:
        print("Error while fetching the test user : ", err)
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
