from slowapi import Limiter
from slowapi.util import get_remote_address
import os
from typing import Set
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

MobileApiKey = os.getenv("MobileApiKey")
XAppName= os.getenv("XAppName")

VALID_API_KEYS: Set[str] = set()


if MobileApiKey:
    VALID_API_KEYS.add(MobileApiKey)
VALID_API_KEYS.add("testapikey") 

if XAppName:
    VALID_API_KEYS.add(XAppName)   
VALID_API_KEYS.add("testappname")    


api_key_header = APIKeyHeader(name="XAPIKEY", auto_error=False)
app_name = APIKeyHeader(name="XAPPNAME", auto_error=False)

async def get_api_key( api_key_header_value: str = Security(api_key_header), app_name_value: str = Security(app_name)):
    """
    Esta función actúa como el 'decorador' de Flask.
    Valida si la clave proporcionada está en nuestra lista de permitidas.
    """
    if api_key_header_value in VALID_API_KEYS and app_name_value in VALID_API_KEYS:
        return api_key_header_value, app_name_value
    
   
    
    # Si no es válida, lanza una excepción HTTP 401
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API Key inválida o no proporcionada",
    )