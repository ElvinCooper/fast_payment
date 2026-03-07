from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserDBRoutingBase(BaseModel):
    user_id: int
    ip_address: str = Field(..., max_length=45)
    port: Optional[int] = 3306
    db_name: str = Field(..., max_length=100)
    db_user: str = Field(..., max_length=50)
    db_password: str = Field(..., max_length=255)


class UserDBRoutingCreate(UserDBRoutingBase):
    pass


class UserDBRoutingResponse(UserDBRoutingBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
