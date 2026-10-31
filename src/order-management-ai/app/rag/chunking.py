def chunk_text(
    text: str,
    max_chars: int = 1800,
    overlap_chars: int = 250,
) -> list[str]:
    normalized = text.strip()

    if not normalized:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in normalized.split("\n\n")
        if paragraph.strip()
    ]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = (
            f"{current}\n\n{paragraph}"
            if current
            else paragraph
        )

        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(paragraph) <= max_chars:
            current = paragraph
            continue

        start = 0

        while start < len(paragraph):
            end = start + max_chars

            chunks.append(
                paragraph[start:end]
            )

            start = end - overlap_chars

        current = ""

    if current:
        chunks.append(current)

    return chunks