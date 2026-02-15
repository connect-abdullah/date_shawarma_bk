from functools import lru_cache
from typing import List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    url: str = Field(default="")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)


class AuthSettings(BaseModel):
    secret_key: str = Field(default="your-secret-key-here-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # Application
    app_name: str = Field(default="Date Shawarma Backend API")
    version: str = Field(default="1.0.0")
    description: str = Field(default="Date Shawarma Backend API")
    debug: bool = Field(default=True)
    environment: str = Field(default="development")

    # API
    api_v1_str: str = Field(default="/api/v1")

    # CORS
    cors_origins: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins",
    )

    secret_key: str = Field(default="your-secret-key-here-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    DATABASE_URL: str = Field(default="postgresql://user:password@localhost:5432/dbname")

    # Email (SMTP)
    GOOGLE_SMTP: str = Field(default="smtp.gmail.com")
    GOOGLE_PORT: int = Field(default=587)
    GOOGLE_EMAIL: str = Field(default="")
    GOOGLE_PASSWORD: str = Field(default="")

    # Supabase (optional - for storage)
    SUPABASE_URL: str = Field(default="")
    SUPABASE_KEY: str = Field(default="")

    @property
    def database_settings(self) -> DatabaseSettings:
        return DatabaseSettings(
            url=self.DATABASE_URL,
            echo=self.debug
        )

    @property
    def auth_settings(self) -> AuthSettings:
        return AuthSettings(
            secret_key=self.secret_key,
            algorithm=self.algorithm,
            access_token_expire_minutes=self.access_token_expire_minutes,
            refresh_token_expire_days=self.refresh_token_expire_days
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
