# Re-export dependencies for backward compatibility
from app.dependencies import (  # noqa: F401
    get_current_user,
    get_user_connection,
    get_db_from_token,
    create_access_token,
    create_refresh_token,
    is_token_revoked,
    CurrentUserDep,
)
from app.mysql_db import get_user_empresas  # noqa: F401
