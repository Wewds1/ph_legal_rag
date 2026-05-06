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
                model="models/embedding-001",
                content=text
            )
            embeddings.append(result["embedding"])
        
        return embeddings
    except Exception as e:
        print(f"Embedding error: {e}")
        return [[0.0] * 768 for _ in texts]


def main():
    db = SessionLocal()
    
    print("Finding chunks without embeddings...")
    
    # Count total chunks needing embeddings
    count_stmt = text("""
        SELECT COUNT(*) FROM case_chunks
        WHERE embedding_text IS NULL
    """)
    total = db.execute(count_stmt).scalar()
    print(f"Found {total} chunks to embed")
    
    if total == 0:
        print("All chunks already embedded!")
        db.close()
        return
    
    processed = 0
    failed = 0
    
    # Fetch chunks in batches
    while True:
        fetch_stmt = text("""
            SELECT id, chunk_text FROM case_chunks
            WHERE embedding_text IS NULL
            LIMIT :limit
        """)
        
        rows = db.execute(fetch_stmt, {"limit": BATCH_SIZE}).fetchall()
        if not rows:
            break
        
        chunk_ids = [row[0] for row in rows]
        texts = [row[1] for row in rows]
        
        print(f"Processing batch of {len(texts)} chunks...")
        
        try:
            embeddings = embed_texts(texts)
            
            # Update each chunk with embedding
            for chunk_id, embedding in zip(chunk_ids, embeddings):
                # Store as JSON string (embedding_text is TEXT column)
                vector_json = json.dumps(embedding)
                
                update_stmt = text(f"""
                    UPDATE case_chunks
                    SET embedding_text = '{vector_json}'
                    WHERE id = '{str(chunk_id)}'
                """)
                
                db.execute(update_stmt)
            
            db.commit()
            processed += len(texts)
            print(f"Embedded {len(texts)} chunks ({processed}/{total})")
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            db.rollback()
            failed += len(texts)
            print(f"Batch failed: {e}")
            break
    
    db.close()
    
    print("\nBackfill complete!")
    print(f"   Processed: {processed}")
    print(f"   Failed: {failed}")


if __name__ == "__main__":
    main()