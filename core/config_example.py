from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ВКурсеДерьма"
    API_V1_STR: str = "/api/v1"
<<<<<<< HEAD:core/config_example.py
    SECRET_KEY: str = "YOUR_KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "YOUR_PASSWORD"
    POSTGRES_DB: str = "YOUR_DB"
=======
    SECRET_KEY: str = "какой то там"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "пароль"
    POSTGRES_DB: str = "VKurseDerma"
>>>>>>> e15fa6ef169d2c3fbd0f877b00c48c31c5d968bb:core/config.py
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"

    @property
    def DATABASE_URL(self) -> str:
        return (
<<<<<<< HEAD:core/config_example.py
            "postgresql+asyncpg://postgres:{POSTGRES_PASSWORD}}@localhost:5432/mydatabase"
=======
            "postgresql+asyncpg://postgres:{пароль}@localhost:5432/mydatabase"
>>>>>>> e15fa6ef169d2c3fbd0f877b00c48c31c5d968bb:core/config.py
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
