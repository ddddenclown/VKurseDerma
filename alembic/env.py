from logging.config import fileConfig
from alembic import context
import asyncio
import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Импортируем модели и настройки
from models.user import Base
from models.post import Post
from models.profiles import Profile
from models.friendship import Friendship
from core.config import settings

# Асинхронная версия
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Асинхронный запуск миграций"""
    connectable = create_async_engine(settings.DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

# Запускаем миграции
asyncio.run(run_migrations_online())