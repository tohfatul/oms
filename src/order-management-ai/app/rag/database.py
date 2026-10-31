import psycopg
from pgvector.psycopg import register_vector

from app.core.config import settings


def get_connection():
    if not settings.database_host:
        raise RuntimeError(
            "DATABASE_HOST is not configured."
        )

    if not settings.database_username:
        raise RuntimeError(
            "DATABASE_USERNAME is not configured."
        )

    if not settings.database_password:
        raise RuntimeError(
            "DATABASE_PASSWORD is not configured."
        )

    connection = psycopg.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_username,
        password=settings.database_password,
        connect_timeout=10,
    )

    register_vector(connection)

    return connection