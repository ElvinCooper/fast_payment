import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from app.database import HOST, PORT, USER, DBPASSWORD, DATABASE
import mysql.connector

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_BD")


def get_pg_connection():
    if not POSTGRES_URL:
        raise ValueError("POSTGRES_BD environment variable is not set")
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)


def get_user_database(user_id: int) -> str:
    conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.descbd 
            FROM ciausers u
            JOIN ciasetup c ON u.idcia = c.idcia
            WHERE u.idusers = %s
            """,
            (user_id,),
        )
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()


def get_all_user_databases() -> dict:
    conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.idusers, c.descbd 
            FROM ciausers u
            JOIN ciasetup c ON u.idcia = c.idcia
            """
        )
        return {row[0]: row[1] for row in cursor.fetchall()}
    finally:
        conn.close()


def asignar_db_usuario(user_id: int, clave: str):
    """Asigna la clave a un usuario en MySQL
    Actualiza la tabla usuario en la base de datos del usuario
    """
    db_asignada = get_user_database(user_id)
    if not db_asignada:
        return "Usuario no encontrado"

    mysql_conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=DBPASSWORD,
        database=db_asignada,
        charset="utf8",
    )
    cursor = mysql_conn.cursor()
    cursor.execute(
        "UPDATE usuario SET clave = %s WHERE idusuario = %s",
        (clave, user_id),
    )
    mysql_conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    mysql_conn.close()

    return f"Filas actualizadas: {rows_affected}"
