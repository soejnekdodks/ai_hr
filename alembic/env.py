import asyncio
from contextvars import ContextVar
from logging.config import fileConfig
from typing import Any

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

from alembic import context
from alembic.context import EnvironmentContext
from app.config import config as app_config
from app.database.schema import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

ctx_var: ContextVar[dict[str, Any]] = ContextVar("ctx_var")

section = config.config_ini_section
config.set_section_option(section, "DATABASE_URL", app_config.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migration(connection):
    try:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()
    except AttributeError:
        context_data = ctx_var.get()
        with EnvironmentContext(
            config=context_data["config"],
            script=context_data["script"],
            **context_data["opts"],
        ):
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()


async def run_async_migrations(connectable) -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    async with connectable.connect() as connection:
        await connection.run_sync(run_migration)
    await connectable.dispose()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    ctx_var.set(
        {
            "config": context.config,
            "script": context.script,
            "opts": context._proxy.context_opts,  # type: ignore
        }
    )
    connectable = context.config.attributes.get("connection")
    if connectable is None:
        connectable = async_engine_from_config(
            context.config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    if isinstance(connectable, AsyncEngine):
        asyncio.run(run_async_migrations(connectable))
    else:
        run_migration(connectable)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
