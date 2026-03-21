import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from app.database import HOST, PORT, USER, DBPASSWORD, DATABASE
import mysql.connector

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


def get_all_user_databases() -> dict:
    conn = get_pg_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT idusuario, db_asignada FROM mapeo_usuarios")
        return {row["idusuario"]: row["db_asignada"] for row in cursor.fetchall()}
    finally:
        conn.close()


def sincronizar_usuarios():

    mysql_conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=DBPASSWORD,
        database=DATABASE,
        charset="utf8",
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
            INSERT INTO mapeo_usuarios (idusuario, usuario) 
            VALUES (%s, %s) 
            ON CONFLICT (idusuario) DO UPDATE SET usuario = EXCLUDED.usuario
        """,
            (u_id, u_name),
        )
    pg_conn.commit()
    cursor.close()
    pg_conn.close()


def asignar_db_usuario(
    user_id: int, database: str | None = None, clave: str | None = None
):
    """Asigna la base de datos y clave a un usuario en PostgreSQL y MySQL
    Solo actualiza los campos que se envíen (si es None, se mantiene el valor actual)
    """
    set_clauses = []
    values = []

    if database is not None:
        set_clauses.append("db_asignada = %s")
        values.append(database)

    if clave is not None:
        set_clauses.append("clave = %s")
        values.append(clave)

    pg_rows_affected = 0
    if set_clauses:
        values.append(user_id)
        query = (
            f"UPDATE mapeo_usuarios SET {', '.join(set_clauses)} WHERE idusuario = %s"
        )

        pg_conn = get_pg_connection()
        cursor = pg_conn.cursor()
        cursor.execute(query, values)
        pg_conn.commit()
        pg_rows_affected = cursor.rowcount
        cursor.close()
        pg_conn.close()

    mysql_rows_affected = 0
    if clave is not None:
        mysql_conn = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=DBPASSWORD,
            database=DATABASE,
            charset="utf8",
        )
        cursor = mysql_conn.cursor()
        cursor.execute(
            "UPDATE usuario SET clave = %s WHERE idusuario = %s",
            (clave, user_id),
        )
        mysql_conn.commit()
        mysql_rows_affected = cursor.rowcount
        cursor.close()
        mysql_conn.close()

    return f"Postgresql: {pg_rows_affected} MySQL: {mysql_rows_affected}"
