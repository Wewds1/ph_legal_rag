from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas import SearchRequest
from database.connection import get_db
from engine.retrieval import Retriever
from engine.generation import Generator


router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(request: SearchRequest, db: Session = Depends(get_db)):
    """Search cases and generate a conversational response."""
    retriever = Retriever(db)
    rows = retriever.hybrid_search(request.query)
    
    cases = [
        {
            "title": row.title,
            "gr_no": row.gr_no,
            "source_url": row.source_url,
            "snippet": row.clean_text[:300] + "..." if len(row.clean_text) > 300 else row.clean_text,
        }
        for row in rows
    ]
    
    generator = Generator()
    response = generator.answer(request.query, cases)
    
    return response