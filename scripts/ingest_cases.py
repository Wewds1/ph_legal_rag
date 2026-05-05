from pathlib import Path
import json
from sqlalchemy import text
from dataclasses import dataclass

from database.connection import SessionLocal
from engine.ingest import insert_case, insert_chunks
from engine.chunking import chunk_text


@dataclass
class ParsedCase:
    source: str
    source_url: str
    gr_no: str | None
    title: str
    decision_date: str | None
    justice: str | None
    category: str | None
    full_text: str
    clean_text: str
    text_hash: str


def main():
    db = SessionLocal()
    processed_root = Path("data/processed")
    
    for json_file in sorted(processed_root.glob("*.json")):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        
        parsed_case = ParsedCase(
            source=data["source"],
            source_url=data["source_url"],
            gr_no=data["gr_no"],
            title=data["title"],
            decision_date=data["decision_date"],
            justice=data["justice"],
            category=data["category"],
            full_text=data["full_text"],
            clean_text=data["clean_text"],
            text_hash=data["text_hash"],
        )
        
        insert_case(db, parsed_case)
        
        result = db.execute(
            text("SELECT id FROM cases WHERE source_url = :url"),
            {"url": parsed_case.source_url}
        ).first()
        case_id = result[0] if result else None
        
        if case_id:
            # Generate chunks and insert
            chunks = chunk_text(parsed_case.clean_text)
            insert_chunks(db, case_id, chunks)
            print(f"Ingested: {parsed_case.title} ({len(chunks)} chunks)")
        else:
            print(f"Failed to get case_id for {parsed_case.title}")
    
    db.close()
    print("Ingestion complete!")


if __name__ == "__main__":
    main()