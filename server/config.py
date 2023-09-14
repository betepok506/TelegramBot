import logging
import os
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    """App settings."""

    PROJECT_NAME: str = "server"
    DEBUG: bool = False
    ENVIRONMENT: str = "local"

    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD") # , 'postgres')
    DATABASE_URI: str = os.getenv('DATABASE_URI') # , 'localhost:6501')
    POSTGRES_USER: str = os.getenv('POSTGRES_USER') # , 'postgres')
    SQLALCHEMY_DATABASE_URL: str = f"postgresql+asyncpg://postgres:postgres@{DATABASE_URI}/{POSTGRES_PASSWORD}"

    # Database
    DATABASE_URL: str = SQLALCHEMY_DATABASE_URL

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
