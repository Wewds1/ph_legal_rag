from __future__ import annotations

import google.generativeai as genai
from sqlalchemy import text
from engine.config import settings
from database.connection import SessionLocal
import json
import time


BATCH_SIZE = 32


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Gemini API."""
    if not settings.llm_api_key:
        print("LLM_API_KEY not set. Skipping embeddings.")
        return [[0.0] * 768 for _ in texts]
    
    try:
        genai.configure(api_key=settings.llm_api_key)
        
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text
            )
            embeddings.append(result["embedding"])
        
        return embeddings
    except Exception as e:
        print(f"Embedding error: {e}")
        return [[0.0] * 768 for _ in texts]

def main():
    db = SessionLocal()
    
    print("Checking embedding status...")
    
    # Count chunks without embeddings
    count_stmt = text("""
        SELECT COUNT(*) FROM case_chunks
        WHERE embedding_text IS NULL
    """)
    total = db.execute(count_stmt).scalar()
    print(f"Found {total} chunks without embeddings")
    
    if total == 0:
        print("All chunks already processed!")
        db.close()
        return
    
    print("Marking chunks as processed (vector embeddings skipped)...")
    print("System will use keyword search instead of vector search.")
    
    # Mark all chunks as processed with empty embedding marker
    update_stmt = text("""
        UPDATE case_chunks
        SET embedding_text = '[]'
        WHERE embedding_text IS NULL
    """)
    
    db.execute(update_stmt)
    db.commit()
    
    print(f"Updated {total} chunks")
    db.close()
    
    print("\nBackfill complete!")
    print("Your system is ready with keyword-based search.")
    print("Vector search can be added later with a working embedding model.")


if __name__ == "__main__":
    main()