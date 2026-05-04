from fastapi import FastAPI
from api.routers.health import router as health_router
from api.routers.search import router as search_router
from api.routers.chat import router as chat_router

app = FastAPI(title="Legal RAG")
app.include_router(health_router)
app.include_router(search_router)
app.include_router(chat_router)
