import os
import uuid
import logging

import psycopg2
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors

from app.utils.utils import hash_password

logger = logging.getLogger(__name__)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s: %(message)s',
    level=logging.INFO
)

dsl = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT')
}

if __name__ == "__main__":
    connection = psycopg2.connect(**dsl)

    hashed_password = hash_password(os.getenv("SUPERUSER_PASSWORD")).decode()

    superuser = {
        "id": str(uuid.uuid4()),
        "email": "superuser@test.ru",
        "password": hashed_password,
        "login": "superuser"

    }

    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO auth.user (id, email, login, password, is_superuser) \
                       VALUES(%s, %s, %s, %s, %s)", (
                           superuser["id"],
                           superuser["email"],
                           superuser["login"],
                           superuser["password"],
                           True
                           )
                       )
        connection.commit()
        logger.info("Superuser created")
    except errors.lookup(UNIQUE_VIOLATION) as e:
        logger.info("Superuser already exists")
    finally:
        cursor.close()
        connection.close()

