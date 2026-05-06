from __future__ import annotations

from sqlalchemy import text, or_


class Retriever:
    def __init__(self, db):
        self.db = db

    def exact_search(self, query: str):
        """Exact G.R. number match."""
        stmt = text(
            """
            SELECT id, gr_no, title, source_url, clean_text
            FROM cases
            WHERE gr_no ILIKE :query
            LIMIT 10
            """
        )
        return self.db.execute(stmt, {"query": f"%{query}%"}).fetchall()

    def keyword_search(self, query: str):
        """Title and case text keyword search."""
        stmt = text(
            """
            SELECT id, gr_no, title, source_url, clean_text
            FROM cases
            WHERE title ILIKE :query OR clean_text ILIKE :query
            LIMIT 10
            """
        )
        return self.db.execute(stmt, {"query": f"%{query}%"}).fetchall()

    def hybrid_search(self, query: str):
        """Combine exact and keyword search."""
        exact = self.exact_search(query)
        if exact:
            return exact
        return self.keyword_search(query)
    
    def vector_search(self, query: str):
        """Vector similarity search using embeddings."""
        if not settings.llm_api_key:
            return []
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.llm_api_key)
            model = genai.GenerativeModel(settings.embedding_model)
            
            query_embedding = model.embed_content(query)["embedding"]
            vector_str = "[" + ",".join(map(str, query_embedding)) + "]"
            
            stmt = text("""
                SELECT cc.id, c.gr_no, c.title, c.source_url, c.clean_text,
                    1 - (cc.embedding <=> :query_embedding::vector) as similarity
                FROM case_chunks cc
                JOIN cases c ON cc.case_id = c.id
                WHERE cc.embedding IS NOT NULL
                ORDER BY similarity DESC
                LIMIT 10
            """)
            
            return self.db.execute(stmt, {"query_embedding": vector_str}).fetchall()
        except Exception as e:
            print(f"Vector search error: {e}")
            return []