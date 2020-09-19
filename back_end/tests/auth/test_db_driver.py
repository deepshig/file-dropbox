import pytest
import sys
import psycopg2
from psycopg2 import Error
sys.path.insert(0, '..')

from src.auth.db_driver import DBDriver  # NOQA


@pytest.fixture(scope="session")
def test_db_driver():
    test_db_config = {"user": "postgres",
                      "password": "postgres",
                      "host": "127.0.0.1",
                      "port": "5432",
                      "db_name": "user_auth_test"}
    test_db = DBDriver()
    test_db.connect(test_db_config)
    return test_db


def test_create_users_table(test_db_driver):
    cursor = test_db_driver.connection.cursor()
    table_exists_query = '''SELECT exists(SELECT relname FROM pg_class WHERE relname='users');'''

    test_db_driver.create_users_table()
    try:
        cursor.execute(table_exists_query)
        exists = cursor.fetchone()[0]
        assert exists == True
    except psycopg2.Error as err:
        print("Error while checking if table exists : ", err)
    finally:
        cursor.close()
        test_db_driver.connection.close()
