from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str


class SearchResult(BaseModel):
    case_title: str
    gr_no: str | None = None
    source_url: str
    snippet: str


class SearchResponse(BaseModel):
    results: list[SearchResult]