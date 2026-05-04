from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.schemas import SearchRequest, SearchResponse
from database.connection import get_db


router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest, db: Session = Depends(get_db)):
    return SearchResponse(results=[])