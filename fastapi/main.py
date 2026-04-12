from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
