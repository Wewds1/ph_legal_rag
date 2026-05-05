from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_index: int
    section_label: str
    char_start: int
    char_end: int
    token_count: int
    chunk_text: str


def chunk_text(text: str, size: int = 3500, overlap: int = 400) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    start = 0
    index = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end]
        chunks.append(
            TextChunk(
                chunk_index=index,
                section_label="body",
                char_start=start,
                char_end=end,
                token_count=max(1, len(chunk) // 4),
                chunk_text=chunk,
            )
        )
        if end == len(text):
            break
        start = end - overlap
        index += 1

    return chunks