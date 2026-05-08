"""
Backfill Tagalog translations into PostgreSQL and embed Tagalog text.

This script is intentionally self-contained so one command can do the full job:
    1. Read each processed case JSON.
    2. Translate the case and each chunk if Tagalog text is missing.
    3. Store the translated chunk text and its embedding in the database.

Learn:
    1. How to make a backfill resilient to missing intermediate files.
    2. How to match cases by either `gr_no` or `source_url`.
    3. How to keep translated text cached back into the JSON file.
"""

import json
from pathlib import Path
from typing import Optional
import google.generativeai as genai
from sqlalchemy import text
from database.connection import SessionLocal
from engine.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=settings.llm_api_key)

PROCESSED_DIR = Path("data/processed")
BATCH_SIZE = 10


def _save_case_translation(filepath: Path, case_data: dict, tagalog_title: Optional[str], tagalog_text: Optional[str]) -> None:
    if tagalog_title:
        case_data["tagalog_title"] = tagalog_title
    if tagalog_text:
        case_data["tagalog_text"] = tagalog_text
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(case_data, f, ensure_ascii=False, indent=2)

def ensure_schema():
    """Add tagalog_text and tagalog_embedding columns if they don't exist."""
    db = SessionLocal()
    try:
        # Check and add tagalog_text column
        db.execute(text("""
            ALTER TABLE case_chunks 
            ADD COLUMN IF NOT EXISTS tagalog_text TEXT;
        """))
        
        # Check and add tagalog_embedding column (store as text JSON for now)
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


def embed_tagalog_text(text: str) -> Optional[list]:
    """Embed Tagalog text using GenAI embedding model.
    
    Args:
        text: Tagalog text to embed
    
    Returns:
        Embedding vector or None on error
    """
    try:
        # Try GenAI embedding API
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text
        )
        return result.get("embedding", None) if result else None
    except Exception as e:
        logger.warning(f"Embedding error: {e}. Using placeholder.")
        return None


def translate_text(text: str) -> Optional[str]:
    """Translate English legal text to Filipino using the configured LLM."""
    if not text:
        return None

    try:
        model = genai.GenerativeModel(settings.llm_model)
        prompt = (
            "Translate the following Philippine legal text to natural Filipino. "
            "Preserve citations, names, case numbers, and legal terms. "
            "Do not summarize or add commentary.\n\n"
            f"{text}"
        )
        response = model.generate_content(prompt)
        return getattr(response, "text", None)
    except Exception as e:
        logger.warning(f"Translation error: {e}")
        return None


def ingest_tagalog_fields():
    """Read translated JSON files and insert Tagalog fields into DB."""

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

                # Fetch case from DB using the most reliable identifier available.
                if gr_no:
                    result = db.execute(text("""
                        SELECT id FROM cases WHERE gr_no = :gr_no LIMIT 1
                    """), {"gr_no": gr_no})
                else:
                    result = db.execute(text("""
                        SELECT id FROM cases WHERE source_url = :source_url LIMIT 1
                    """), {"source_url": source_url})

                case_row = result.fetchone()
                
                if not case_row:
                    logger.warning(f"Case {case_label} not found in DB. Skipping.")
                    continue
                
                case_id = case_row[0]

                # Translate the case text once and cache it back into the JSON file.
                tagalog_title = case_data.get("tagalog_title")
                tagalog_text = case_data.get("tagalog_text")
                if not tagalog_text:
                    tagalog_title = tagalog_title or translate_text(case_data.get("title", ""))
                    tagalog_text = translate_text(case_data.get("full_text") or case_data.get("clean_text", ""))
                    if tagalog_text:
                        _save_case_translation(filepath, case_data, tagalog_title, tagalog_text)
                
                # Get all chunks for this case.
                chunks_result = db.execute(text("""
                    SELECT id, chunk_text FROM case_chunks WHERE case_id = :case_id
                """), {"case_id": case_id})
                chunks = chunks_result.fetchall()

                # For each chunk, translate and embed the Tagalog version.
                for chunk_id, chunk_text in chunks:
                    translated_chunk = translate_text(chunk_text or "") or chunk_text or ""
                    embedding = embed_tagalog_text(translated_chunk)
                    embedding_json = json.dumps(embedding) if embedding else "[]"
                    
                    db.execute(text("""
                        UPDATE case_chunks 
                        SET tagalog_text = :tagalog_text,
                            tagalog_embedding = :embedding
                        WHERE id = :chunk_id
                    """), {"tagalog_text": translated_chunk, "embedding": embedding_json, "chunk_id": chunk_id})
                
                db.commit()
                processed += 1
                logger.info(f"✓ {case_label} ingested ({processed}/{len(case_files)})")
                
                # Pause every N cases
                if (i + 1) % BATCH_SIZE == 0:
                    logger.info(f"Batch done. Pausing...")
                    import time
                    time.sleep(2)
            
            except Exception as e:
                logger.error(f"Error processing {filepath.name}: {e}")
                db.rollback()
        
        logger.info(f"\n✓ Tagalog ingestion complete: {processed} cases processed")
    
    finally:
        db.close()


def main():
    logger.info("Starting Tagalog corpus backfill...")
    ensure_schema()
    ingest_tagalog_fields()


if __name__ == "__main__":
    main()