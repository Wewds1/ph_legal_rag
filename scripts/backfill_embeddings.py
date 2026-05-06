from __future__ import annotations

import google.generativeai as genai
from sqlalchemy import text
from engine.config import settings
from database.connection import SessionLocal
import time


BATCH_SIZE = 32


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Gemini API."""
    if not settings.llm_api_key:
        print("⚠️ LLM_API_KEY not set. Skipping embeddings.")
        return [[0.0] * 768 for _ in texts]
    
    try:
        genai.configure(api_key=settings.llm_api_key)
        model = genai.GenerativeModel(settings.embedding_model)
        
        embeddings = []
        for text in texts:
            result = model.embed_content(text)
            embeddings.append(result["embedding"])
        
        return embeddings
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return [[0.0] * 768 for _ in texts]


def main():
    db = SessionLocal()
    
    print("🔍 Finding chunks without embeddings...")
    
    # Count total chunks needing embeddings
    count_stmt = text("""
        SELECT COUNT(*) FROM case_chunks
        WHERE embedding_text IS NULL
    """)
    total = db.execute(count_stmt).scalar()
    print(f"📊 Found {total} chunks to embed")
    
    if total == 0:
        print("✅ All chunks already embedded!")
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
        
        print(f"\n📦 Processing batch of {len(texts)} chunks...")
        
        try:
            embeddings = embed_texts(texts)
            
            # Update each chunk
            for chunk_id, embedding in zip(chunk_ids, embeddings):
                update_stmt = text("""
                    UPDATE case_chunks
                    SET embedding = :embedding::vector
                    WHERE id = :id
                """)
                
                # Convert embedding to PostgreSQL vector format
                vector_str = "[" + ",".join(map(str, embedding)) + "]"
                
                db.execute(update_stmt, {"embedding": vector_str, "id": str(chunk_id)})
            
            db.commit()
            processed += len(texts)
            print(f"✅ Embedded {len(texts)} chunks ({processed}/{total})")
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            db.rollback()
            failed += len(texts)
            print(f"❌ Batch failed: {e}")
            break
    
    db.close()
    
    print(f"\n🎉 Backfill complete!")
    print(f"   ✅ Processed: {processed}")
    print(f"   ❌ Failed: {failed}")


if __name__ == "__main__":
    main()