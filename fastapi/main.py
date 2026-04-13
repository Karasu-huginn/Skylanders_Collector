import os
from pathlib import Path
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from db import engine, Base
import routers.edition_router as edition_router
import routers.item_router as item_router
import routers.type_router as type_router
import routers.variant_router as variant_router
import routers.element_router as element_router

app = FastAPI()

api_router = APIRouter(prefix="/api")
api_router.include_router(edition_router.router)
api_router.include_router(type_router.router)
api_router.include_router(variant_router.router)
api_router.include_router(element_router.router)
api_router.include_router(item_router.router)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Serve built React frontend in production
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    # Figurine images, icons, logos
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve React SPA — returns index.html for all non-API, non-asset routes."""
        file_path = STATIC_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
