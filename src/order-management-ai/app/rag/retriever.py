from dataclasses import dataclass

from pgvector import Vector

from app.rag.database import get_connection
from app.rag.embedding_service import OpenAIEmbeddingService


@dataclass(frozen=True)
class KnowledgeResult:
    source: str
    title: str | None
    content: str
    similarity: float


class KnowledgeRetriever:
    def __init__(self):
        self.embedding_service = OpenAIEmbeddingService()

    def search(
        self,
        query: str,
        limit: int = 4,
    ) -> list[KnowledgeResult]:
        embedding = self.embedding_service.embed_query(query)

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        source,
                        title,
                        content,
                        1 - (embedding <=> %s) AS similarity
                    FROM rag.knowledge_chunks
                    ORDER BY embedding <=> %s
                    LIMIT %s;
                    """,
                    (
                        Vector(embedding),
                        Vector(embedding),
                        limit,
                    ),
                )

                rows = cursor.fetchall()

        return [
            KnowledgeResult(
                source=row[0],
                title=row[1],
                content=row[2],
                similarity=float(row[3]),
            )
            for row in rows
        ]


knowledge_retriever = KnowledgeRetriever()