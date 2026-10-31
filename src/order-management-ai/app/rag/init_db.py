from app.core.config import settings
from app.rag.database import get_connection


def initialize_rag_database() -> None:
    dimensions = settings.embedding_dimensions

    if dimensions <= 0:
        raise RuntimeError(
            "EMBEDDING_DIMENSIONS must be greater than zero."
        )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE EXTENSION IF NOT EXISTS vector;"
            )

            cursor.execute(
                "CREATE SCHEMA IF NOT EXISTS rag;"
            )

            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS rag.knowledge_chunks
                (
                    id UUID PRIMARY KEY,

                    source VARCHAR(500) NOT NULL,

                    title VARCHAR(500),

                    chunk_index INTEGER NOT NULL,

                    content TEXT NOT NULL,

                    metadata JSONB NOT NULL
                        DEFAULT '{{}}'::jsonb,

                    embedding VECTOR({dimensions})
                        NOT NULL,

                    created_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT uq_knowledge_chunk
                        UNIQUE (source, chunk_index)
                );
                """
            )

        connection.commit()

    print(
        "RAG database initialized successfully."
    )


if __name__ == "__main__":
    initialize_rag_database()