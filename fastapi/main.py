from typing import Annotated, List
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import get_db, engine, Base
import routers.edition_router as edition_router
import routers.item_router as item_router
import routers.type_router as type_router
import routers.variant_router as variant_router
import routers.element_router as element_router

app = FastAPI()
app.include_router(edition_router.router)
app.include_router(type_router.router)
app.include_router(variant_router.router)
app.include_router(element_router.router)
app.include_router(item_router.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174","http://localhost:5173"],    #todo change after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)
db_dep = Annotated[Session, Depends(get_db)]

#* FastAPI endpoints
@app.get("/{item_id}")
def root(item_id:int):
    return {"var":item_id}
