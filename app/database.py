import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

HOST = os.getenv("HOST", "localhost")
PORT = os.getenv("PORT", 3306)
DATABASE = os.getenv("DATABASE")
USER = os.getenv("USER")
DBPASSWORD = os.getenv("DBPASSWORD")


def get_connection(user_id: int = None, db_name: str = None):
    """Conexión dinámica por request - usa db_name del token si está disponible"""

    # Prioridad: db_name del token > user_id lookup > DATABASE default
    target_db = db_name
    if not target_db and user_id:
        from app.postgres_db import get_user_database
        target_db = get_user_database(user_id)
    if not target_db:
        target_db = DATABASE

    try:
        conn = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=DBPASSWORD,
            database=target_db,
            charset="utf8",
            ssl_disabled=True,
            autocommit=True,
            connect_timeout=10,
        )

        yield conn

    except Error as e:
        logger.error(f"Error de conexión a {target_db}: {e}")
        raise e
    finally:
        if "conn" in locals() and conn.is_connected():
            conn.close()


def get_cia_connection():
    """Conexión directa a la base de datos central ciadatabase"""
    try:
        conn = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=DBPASSWORD,
            database="ciadatabase",
            charset="utf8",
            ssl_disabled=True,
            autocommit=True,
            connect_timeout=10,
        )
        yield conn
    except Error as e:
        logger.error(f"Error de conexión a ciadatabase: {e}")
        raise e
    finally:
        if "conn" in locals() and conn.is_connected():
            conn.close()
