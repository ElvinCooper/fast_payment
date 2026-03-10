import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_BD")


def get_pg_connection():
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)


def get_user_database(user_id: int) -> str:
    conn = get_pg_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT db_asignada FROM mapeo_usuarios WHERE idusuario = %s", (user_id,)
        )
        result = cursor.fetchone()
        return result["db_asignada"] if result else None
    finally:
        conn.close()


def sincronizar_usuarios():
    import mysql.connector
    from app.database import HOST, PORT, USER, DBPASSWORD, DATABASE

    mysql_conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=DBPASSWORD,
        database=DATABASE,
        charset='utf8'
    )
    cursor = mysql_conn.cursor()
    cursor.execute("SELECT idusuario, usuario FROM usuario")
    usuarios = cursor.fetchall()
    mysql_conn.close()

    pg_conn = get_pg_connection()
    cursor = pg_conn.cursor()
    for u_id, u_name in usuarios:
        cursor.execute(
            """
            INSERT INTO mapeo_usuarios (user_id, username) 
            VALUES (%s, %s) 
            ON CONFLICT (user_id) DO NOTHING
        """,
            (u_id, u_name),
        )
    pg_conn.commit()
    cursor.close()
    pg_conn.close()
