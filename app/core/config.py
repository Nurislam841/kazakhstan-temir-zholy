from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "KTZh API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ktzh.db"

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS - hardcoded to avoid parsing issues
    @property
    def cors_origins(self) -> List[str]:
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:5173",
        ]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # <-- ДОБАВЬТЕ ЭТУ СТРОКУ


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()