from fastapi import APIRouter


router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(query: str):
    return {"answer": "Not implemented yet"}