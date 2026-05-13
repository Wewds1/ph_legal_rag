"""
Backfill Tagalog translations into PostgreSQL using Ollama.

What this script does:
1. Reads each processed case JSON.
2. Translates case text in smaller chunks using a local/remote Ollama model.
3. Stores translated chunk text in the database.
4. Caches translated case text back into the JSON file.

This version uses Ollama (unlimited requests, no rate limits).
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

from ollama import chat
from sqlalchemy import text

from database.connection import SessionLocal
from engine.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
BATCH_SIZE = 10
MAX_TRANSLATE_CHARS = 2200
OLLAMA_MODEL = "minimax-m2.5:cloud" 

def _save_case_translation(
    filepath: Path,
    case_data: dict,
    tagalog_title: Optional[str],
    tagalog_text: Optional[str],
) -> None:
    if tagalog_title:
        case_data["tagalog_title"] = tagalog_title
    if tagalog_text:
        case_data["tagalog_text"] = tagalog_text

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(case_data, f, ensure_ascii=False, indent=2)


def ensure_schema() -> None:
    """Add Tagalog columns if they don't exist yet."""
    db = SessionLocal()
    try:
        db.execute(text("""
            ALTER TABLE case_chunks
            ADD COLUMN IF NOT EXISTS tagalog_text TEXT;
        """))
        db.execute(text("""
            ALTER TABLE case_chunks
            ADD COLUMN IF NOT EXISTS tagalog_embedding TEXT DEFAULT '[]';
        """))
        db.commit()
        logger.info("✓ Schema updated with tagalog_text and tagalog_embedding")
    except Exception as e:
        logger.error(f"Schema error: {e}")
        db.rollback()
    finally:
        db.close()


def split_text(text_value: str, max_chars: int = MAX_TRANSLATE_CHARS) -> list[str]:
    """Split long text into paragraph-aware chunks."""
    text_value = (text_value or "").strip()
    if not text_value:
        return []

    paragraphs = [part.strip() for part in text_value.split("\n\n") if part.strip()]
    if not paragraphs:
        return [text_value[:max_chars]]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""

            start = 0
            while start < len(paragraph):
                chunks.append(paragraph[start : start + max_chars])
                start += max_chars
            continue

        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    return chunks


def translate_chunk(text_value: str) -> Optional[str]:
    """Translate one chunk of legal text to Filipino using Ollama."""
    text_value = (text_value or "").strip()
    if not text_value:
        return None

    try:
        prompt = (
            "Translate the following Philippine legal text to natural Filipino. "
            "Preserve citations, case numbers, names, dates, and legal terms. "
            "Do not summarize, explain, or add commentary.\n\n"
            f"{text_value}"
        )

        response = chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        translated = (getattr(response, "message", None) or {}).get("content", "").strip()
        return translated or text_value

    except Exception as e:
        logger.warning(f"Translation error: {e}. Using original text.")
        return text_value


def translate_large_text(text_value: str) -> Optional[str]:
    """Translate a long document by splitting it into smaller chunks first."""
    text_value = (text_value or "").strip()
    if not text_value:
        return None

    chunks_list = split_text(text_value)
    translated_parts: list[str] = []

    for idx, chunk in enumerate(chunks_list, start=1):
        translated = translate_chunk(chunk)
        if translated:
            translated_parts.append(translated)
        else:
            translated_parts.append(chunk)
        logger.info(f"  Translated chunk {idx}/{len(chunks_list)}")
        time.sleep(0.1)

    joined = "\n\n".join(translated_parts).strip()
    return joined or None


def ingest_tagalog_fields() -> None:
    """Translate cases, update JSON cache, and write Tagalog text to DB."""
    db = SessionLocal()
    case_files = sorted(PROCESSED_DIR.glob("*.json"))
    processed = 0

    try:
        for i, filepath in enumerate(case_files):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    case_data = json.load(f)

                gr_no = case_data.get("gr_no")
                source_url = case_data.get("source_url")
                if not gr_no and not source_url:
                    continue

                case_label = gr_no or source_url
                logger.info(f"Ingesting {case_label}...")

                if gr_no:
                    result = db.execute(
                        text("SELECT id FROM cases WHERE gr_no = :gr_no LIMIT 1"),
                        {"gr_no": gr_no},
                    )
                else:
                    result = db.execute(
                        text("SELECT id FROM cases WHERE source_url = :source_url LIMIT 1"),
                        {"source_url": source_url},
                    )

                case_row = result.fetchone()
                if not case_row:
                    logger.warning(f"Case {case_label} not found in DB. Skipping.")
                    continue

                case_id = case_row[0]

                # Translate case title if not already done
                tagalog_title = case_data.get("tagalog_title")
                if not tagalog_title:
                    tagalog_title = translate_chunk(case_data.get("title", ""))

                # Translate full case text if not already done
                tagalog_text = case_data.get("tagalog_text")
                if not tagalog_text:
                    source_text = case_data.get("clean_text") or case_data.get("full_text", "")
                    tagalog_text = translate_large_text(source_text)
                    if tagalog_text:
                        _save_case_translation(filepath, case_data, tagalog_title, tagalog_text)

                # Get all chunks for this case
                chunks_result = db.execute(
                    text("""
                        SELECT id, chunk_text
                        FROM case_chunks
                        WHERE case_id = :case_id
                        ORDR BY chunk_index
                    """),
                    {"case_id": case_id},
                )
                chunks = chunks_result.fetchall()

                # Translate and save each chunk
                for chunk_index, (chunk_id, chunk_text) in enumerate(chunks, start=1):
                    translated_chunk = translate_chunk(chunk_text or "")

                    db.execute(
                        text("""
                            UPDATE case_chunks
                            SET tagalog_text = :tagalog_text,
                                tagalog_embedding = :embedding
                            WHERE id = :chunk_id
                        """),
                        {
                            "tagalog_text": translated_chunk or "",
                            "embedding": "[]",  # Embeddings via Ollama later if needed
                            "chunk_id": chunk_id,
                        },
                    )

                    logger.info(f"  chunk {chunk_index}/{len(chunks)} done")
                    time.sleep(0.05)

                db.commit()
                processed += 1
                logger.info(f"✓ {case_label} ingested ({processed}/{len(case_files)})")

                if (i + 1) % BATCH_SIZE == 0:
                    logger.info("Batch pause...")
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error processing {filepath.name}: {e}")
                db.rollback()

        logger.info(f"\n✓ Tagalog ingestion complete: {processed} cases processed")
    finally:
        db.close()


def main() -> None:
    logger.info(f"Starting Tagalog corpus backfill with Ollama model: {OLLAMA_MODEL}")
    ensure_schema()
    ingest_tagalog_fields()


if __name__ == "__main__":
    main()