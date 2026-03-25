import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()
HOST = os.getenv("HOST", "localhost")
PORT = os.getenv("PORT", 3306)
DATABASE = os.getenv("DATABASE")
USER = os.getenv("USER")
DBPASSWORD = os.getenv("DBPASSWORD")


def get_connection(user_id: int = None):
    """conexion nueva por cada request."""
    from app.postgres_db import get_user_database

    db_name = DATABASE  
    if user_id:
        db_asignada = get_user_database(user_id) 
        if db_asignada:
            db_name = db_asignada

    try:
        conn = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=DBPASSWORD,
            database=db_name,
            charset="utf8",
            ssl_disabled=True,
            autocommit=True,
            connect_timeout=10,
        )

        yield conn

    except Error as e:
        print(f"Error de conexión: {e}")
        raise e
    finally:
        if "conn" in locals() and conn.is_connected():
            conn.close()
