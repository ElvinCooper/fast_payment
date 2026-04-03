# Re-export dependencies for backward compatibility
from app.dependencies import (
    get_current_user,
    get_user_connection,
    get_db_from_token,
    create_access_token,
    create_refresh_token,
    is_token_revoked,
    CurrentUserDep,
)
