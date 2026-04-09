from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: Optional[str] = None
    POSTGRES_URL: Optional[str] = None
    POSTGRES_PRISMA_URL: Optional[str] = None
    POSTGRES_URL_NON_POOLING: Optional[str] = None
    ALGORITHM: str
    SECRET_KEY: str
    EXP_TIME: int
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    AUTO_CREATE_TABLES: bool = False
    DB_USE_NULL_POOL: Optional[bool] = None
    VERCEL: Optional[str] = None

    @property
    def resolved_database_url(self) -> str:
        for value in (
            self.DATABASE_URL,
            self.POSTGRES_URL,
            self.POSTGRES_PRISMA_URL,
            self.POSTGRES_URL_NON_POOLING,
        ):
            if value:
                return value
        raise ValueError(
            "Database URL is not configured. Set DATABASE_URL or connect Vercel Postgres."
        )

    @property
    def should_use_null_pool(self) -> bool:
        if self.DB_USE_NULL_POOL is not None:
            return self.DB_USE_NULL_POOL
        return bool(self.VERCEL)


settings = Settings()
