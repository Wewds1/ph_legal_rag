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