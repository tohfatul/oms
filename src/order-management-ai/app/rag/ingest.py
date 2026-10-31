from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from psycopg.types.json import Jsonb

from app.rag.chunking import chunk_text
from app.rag.database import get_connection
from app.rag.embedding_service import OpenAIEmbeddingService


PROJECT_ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_DIR = (
    PROJECT_ROOT
    / "knowledge"
)


def ingest_document(
    path: Path,
    embedding_service: OpenAIEmbeddingService,
) -> int:
    source = path.name

    text = path.read_text(
        encoding="utf-8"
    )

    chunks = chunk_text(text)

    if not chunks:
        return 0

    embeddings = embedding_service.embed_texts(
        chunks
    )

    if len(chunks) != len(embeddings):
        raise RuntimeError(
            "Embedding count does not match chunk count."
        )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM rag.knowledge_chunks
                WHERE source = %s;
                """,
                (source,),
            )

            for index, (
                chunk,
                embedding,
            ) in enumerate(
                zip(
                    chunks,
                    embeddings,
                    strict=True,
                )
            ):
                chunk_id = uuid5(
                    NAMESPACE_URL,
                    f"{source}:{index}",
                )

                cursor.execute(
                    """
                    INSERT INTO rag.knowledge_chunks
                    (
                        id,
                        source,
                        title,
                        chunk_index,
                        content,
                        metadata,
                        embedding
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    );
                    """,
                    (
                        chunk_id,
                        source,
                        extract_title(text),
                        index,
                        chunk,
                        Jsonb({
                            "source_type": "markdown",
                            "file_name": source,
                        }),
                        embedding,
                    ),
                )

        connection.commit()

    return len(chunks)


def extract_title(
    text: str,
) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("# "):
            return stripped[2:].strip()

    return None


def ingest_all() -> None:
    if not KNOWLEDGE_DIR.exists():
        raise RuntimeError(
            f"Knowledge directory does not exist: "
            f"{KNOWLEDGE_DIR}"
        )

    documents = sorted(
        KNOWLEDGE_DIR.glob("*.md")
    )

    if not documents:
        raise RuntimeError(
            "No Markdown knowledge documents found."
        )

    embedding_service = (
        OpenAIEmbeddingService()
    )

    total_chunks = 0

    for document in documents:
        count = ingest_document(
            document,
            embedding_service,
        )

        total_chunks += count

        print(
            f"Ingested {document.name}: "
            f"{count} chunks"
        )

    print(
        f"Knowledge ingestion complete. "
        f"Total chunks: {total_chunks}"
    )


if __name__ == "__main__":
    ingest_all()