import mysql.connector
from mysql.connector import Error
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_connection(user_id: int | None = None, db_name: str | None = None):
    """Conexión dinámica por request - usa db_name del token si está disponible"""

    target_db = db_name
    if not target_db and user_id:
        from app.mysql_db import get_user_database

        target_db = get_user_database(user_id)
    if not target_db:
        target_db = settings.DATABASE

    try:
        conn = mysql.connector.connect(
            host=settings.HOST,
            port=settings.PORT,
            user=settings.USER,
            password=settings.DBPASSWORD,
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
            host=settings.HOST,
            port=settings.PORT,
            user=settings.USER,
            password=settings.DBPASSWORD,
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
