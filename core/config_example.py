from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ВКурсеДерьма"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "YOUR_KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "YOUR_PASSWORD"
    POSTGRES_DB: str = "YOUR_DB"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"

    @property
    def DATABASE_URL(self) -> str:
        return (
            "postgresql+asyncpg://postgres:{POSTGRES_PASSWORD}}@localhost:5432/mydatabase"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
