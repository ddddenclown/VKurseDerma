from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ВКурсеДерьма"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "ваш секретный ключ"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "ващ секретный пароль"
    POSTGRES_DB: str = "VKurseDerma"
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
