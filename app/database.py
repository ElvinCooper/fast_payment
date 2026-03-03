import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()
HOST = os.getenv("HOST", "localhost")
DATABASE = os.getenv("DATABASE")
USER = os.getenv("USER")
DBPASSWORD = os.getenv("DBPASSWORD")


def get_connection():
    """conexion nueva por cada request."""

    conn = mysql.connector.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=DBPASSWORD,
        charset="utf8",
        collation="utf8_general_ci",
    )
    try:
        yield conn
    finally:
        conn.close()
