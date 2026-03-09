from fastapi import APIRouter, HTTPException, Depends
from app.schemas.routing_schema import UserDBRoutingResponse, UserDBRoutingUpdate
from app.database import get_connection
from app.auth_utils import get_current_user
from mysql.connector import MySQLConnection
from typing import List
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
HOST=os.getenv("HOST")
PORT=os.getenv("PORT")
USER= os.getenv("USER")
DBPASSWORD= os.getenv("DBPASSWORD")

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.get("/users", response_model=List[UserDBRoutingResponse])
def get_all_acces(conn: MySQLConnection = Depends(get_connection),):
    """Lista usuarios con acceso al sistema"""
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT idusuario, usuario FROM usuario WHERE idusuario not in (1, 2) ORDER BY idusuario")
    results = cursor.fetchall()
    cursor.close()
    
    return results


@router.put("/user/routing")
def asignar_acceso(user_data: UserDBRoutingUpdate, conn: MySQLConnection = Depends(get_connection),):
    """Asignar BD y clave a un usuario"""
    cursor = conn.cursor()
    
     # Verificar si el usuario existe
    cursor.execute("SELECT idusuario FROM usuario WHERE idusuario = %s", (user_data.idusuario,))
    user_exists = cursor.fetchone()
    
    if not user_exists:
        cursor.close()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # actualizar campos del usuario indicado
    query = """
       UPDATE usuario
       SET `database` = %s,
           clave = %s
       WHERE idusuario = %s
    """    
    
    cursor.execute(query, (user_data.database, user_data.clave, user_data.idusuario,),)
    conn.commit()    
    cursor.close()        

    return HTTPException(status_code=200, detail= {"message": "Usuario actualizado exitosamente"})


@router.get("/server/databases")
def get_server_databases(conn: MySQLConnection = Depends(get_connection), current_user: dict = Depends(get_current_user),):
    """Obtener las bases de datos disponibles en el servidor"""
    
    # Validar que el usuario sea administrador
    admin_user_ids = [1, 2, 3]
    if current_user.get('id') not in admin_user_ids:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Solo administradores pueden acceder a esta función")                    

    try:
        temp_conn = mysql.connector.connect(
            host=HOST, 
            port=PORT,
            user=USER,
            password=DBPASSWORD,
            connect_timeout=5,
        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute("SHOW DATABASES")
        
        databases = [db[0] for db in temp_cursor.fetchall() if db[0] not in ("information_schema", "performance_schema", "mysql", "sys")]
        temp_cursor.close()
        temp_conn.close()
        
        return {"databases": databases}
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error al conectar al servidor: {str(e)}"
        )
