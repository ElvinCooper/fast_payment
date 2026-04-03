import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import get_settings

settings = get_settings()

POSTGRES_URL = settings.POSTGRES_BD


def get_pg_connection():
    if not POSTGRES_URL:
        raise ValueError("POSTGRES_BD environment variable is not set")
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)


def get_user_database(user_id: int) -> str:
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
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


def get_user_type(user_id: int) -> str:
    """Obtiene el tipo de usuario desde ciausers"""
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tipouser FROM ciausers WHERE idusers = %s",
            (user_id,),
        )
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()


def get_tipos_usuario() -> list:
    """Obtiene los tipos de usuario distintos desde ciausers"""
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT tipouser FROM ciausers WHERE tipouser IS NOT NULL AND tipouser not in ('root')"
        )
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_user_db_from_ciausers(usuario: str, clave: str) -> dict | None:
    """Obtiene la BD asignada y el id del usuario desde ciausers usando empresa_id"""
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.idusers, u.estatus, u.tipouser, u.empresa_id,
                   c.idcia, c.descbd, c.cidescripcion
            FROM ciausers u
            JOIN ciasetup c ON u.empresa_id = c.idcia
            WHERE u.usuario = %s AND u.clave = %s
            """,
            (usuario, clave),
        )
        result = cursor.fetchone()
        if result:
            return {
                "idusers": result["idusers"],
                "estatus": result["estatus"],
                "tipouser": result["tipouser"],
                "empresa_id": result["empresa_id"],
                "idcia": result["idcia"],
                "db_asignada": result["descbd"],
                "empresa": result["cidescripcion"],
            }
        return None
    finally:
        conn.close()


def get_all_empresas() -> list:
    """Obtiene todas las empresas desde ciasetup"""
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT idcia, cidescripcion, descbd FROM ciasetup")
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_user_databases() -> dict:
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
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
    """Asigna la clave a un usuario en MySQL"""
    import mysql.connector

    db_asignada = get_user_database(user_id)
    if not db_asignada:
        return "Usuario no encontrado"

    mysql_conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
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


def actualizar_usuario_cia(
    user_id: int,
    idcia: int,
    clave: str | None = None,
    estatus: int | None = None,
    tipouser: str | None = None,
):
    """Actualiza campos de un usuario en la tabla ciausers (bd central)"""
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor()

        campos = []
        valores = []

        if clave is not None:
            campos.append("clave = %s")
            valores.append(clave)
        if estatus is not None:
            campos.append("estatus = %s")
            valores.append(str(estatus))
        if tipouser is not None:
            campos.append("tipouser = %s")
            valores.append(tipouser)

        if not campos:
            return "No hay campos para actualizar"

        valores.append(user_id)
        valores.append(idcia)

        # nosec: B608
        query = (
            f"UPDATE ciausers SET {', '.join(campos)} WHERE idusers = %s AND idcia = %s"
        )

        cursor.execute(query, valores)
        conn.commit()
        rows_affected = cursor.rowcount

        cursor.close()

        if rows_affected == 0:
            return "Usuario no encontrado en ciausers"
        return "Usuario actualizado exitosamente"
    finally:
        conn.close()


def update_user_default_empresa(user_id: int, empresa_id: int) -> bool:
    """Actualiza el campo empresa_id en ciausers (MySQL ciadatabase) para el user_id dado"""
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ciausers SET empresa_id = %s WHERE idusers = %s",
            (empresa_id, user_id),
        )
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        return rows_affected > 0
    finally:
        conn.close()


def get_user_empresas(user_id: int) -> list:
    """Obtiene las empresas asociadas a un usuario via userempresa + ciasetup"""
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT e.idcia, e.cidescripcion, e.descbd
            FROM userempresa ue
            JOIN ciasetup e ON ue.empresa_id = e.idcia
            WHERE ue.user_id = %s
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def validate_user_empresa(user_id: int, empresa_id: int) -> dict | None:
    """Valida que un usuario pertenece a una empresa y retorna info de la BD"""
    import mysql.connector

    conn = mysql.connector.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.DBPASSWORD,
        database="ciadatabase",
        charset="utf8",
    )
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT e.idcia, e.cidescripcion, e.descbd
            FROM userempresa ue
            JOIN ciasetup e ON ue.empresa_id = e.idcia
            WHERE ue.user_id = %s AND ue.empresa_id = %s
            """,
            (user_id, empresa_id),
        )
        return cursor.fetchone()
    finally:
        conn.close()
