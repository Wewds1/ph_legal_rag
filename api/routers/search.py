from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas import SearchRequest, SearchResult, SearchResponse
from database.connection import get_db
from engine.retrieval import Retriever


router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest, db: Session = Depends(get_db)):
    retriever = Retriever(db)
    rows = retriever.hybrid_search(request.query)
    
    results = []
    for row in rows:
        snippet = row.clean_text[:200] + "..." if len(row.clean_text) > 200 else row.clean_text
        
        results.append(
            SearchResult(
                case_title=row.title,
                gr_no=row.gr_no,
                source_url=row.source_url,
                snippet=snippet,
            )
        )
    
    return SearchResponse(results=results)