from __future__ import annotations

from uuid import uuid4
from sqlalchemy import text


def insert_case(db, parsed_case):
    stmt = text(
        """
        INSERT INTO cases (
            id, source, source_url, gr_no, title,
            decision_date, justice, category,
            full_text, clean_text, text_hash,
            scraped_at, parsed_at
        ) VALUES (
            :id, :source, :source_url, :gr_no, :title,
            :decision_date, :justice, :category,
            :full_text, :clean_text, :text_hash,
            NOW(), NOW()
        )
        ON CONFLICT (source_url) DO UPDATE SET
            gr_no = EXCLUDED.gr_no,
            title = EXCLUDED.title,
            decision_date = EXCLUDED.decision_date,
            justice = EXCLUDED.justice,
            category = EXCLUDED.category,
            full_text = EXCLUDED.full_text,
            clean_text = EXCLUDED.clean_text,
            text_hash = EXCLUDED.text_hash,
            updated_at = NOW()
        """
    )

    db.execute(
        stmt,
        {
            "id": str(uuid4()),
            "source": parsed_case.source,
            "source_url": parsed_case.source_url,
            "gr_no": parsed_case.gr_no,
            "title": parsed_case.title,
            "decision_date": parsed_case.decision_date,
            "justice": parsed_case.justice,
            "category": parsed_case.category,
            "full_text": parsed_case.full_text,
            "clean_text": parsed_case.clean_text,
            "text_hash": parsed_case.text_hash,
        },
    )
    db.commit()


def insert_chunks(db, case_id, chunks):
    """Insert text chunks for a case."""
    stmt = text(
        """
        INSERT INTO case_chunks (
            id, case_id, chunk_index, section_label,
            char_start, char_end, token_count, chunk_text
        ) VALUES (
            :id, :case_id, :chunk_index, :section_label,
            :char_start, :char_end, :token_count, :chunk_text
        )
        """
    )

    for chunk in chunks:
        db.execute(
            stmt,
            {
                "id": str(uuid4()),
                "case_id": case_id,
                "chunk_index": chunk.chunk_index,
                "section_label": chunk.section_label,
                "char_start": chunk.char_start,
                "char_end": chunk.char_end,
                "token_count": chunk.token_count,
                "chunk_text": chunk.chunk_text,
            },
        )
    db.commit()