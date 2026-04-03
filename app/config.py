from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str
    EXPIRE_HOURS: int = 2
    ALGORITHM: str = "HS256"

    HOST: str = "localhost"
    PORT: int = 3306
    USER: str
    DBPASSWORD: str
    DATABASE: str

    POSTGRES_BD: str | None = None


@lru_cache()
def get_settings() -> Settings:
    return Settings()
