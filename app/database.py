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


def get_connection():
    """conexion nueva por cada request."""

    try:
        # Primero conectar sin especificar base de datos
        conn = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=DBPASSWORD,
            charset="utf8",
            ssl_disabled=True,
            autocommit=True,
            connect_timeout=10
        )

        # Luego seleccionar la base de datos
        cursor = conn.cursor()
        cursor.execute(f"USE {DATABASE}")
        cursor.close()

        yield conn

    except Error as e:
        print(f"Error de conexión: {e}")
        raise e
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
