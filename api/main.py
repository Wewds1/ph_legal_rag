from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from api.routers import health, search, chat

app = FastAPI(
    title="Legal RAG",
    description="Philippine Jurisprudence Search"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (OK for localhost)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router)
app.include_router(search.router)
app.include_router(chat.router)

# Serve static files from app/
app_dir = Path(__file__).parent.parent / "app"
if (app_dir / "static").exists():
    app.mount("/static", StaticFiles(directory=str(app_dir / "static")), name="static")

# Serve index.html as root
@app.get("/")
async def serve_index():
    html_path = app_dir / "index.html"
    if html_path.exists():
        return FileResponse(html_path, media_type="text/html")
    return {"message": "index.html not found"}