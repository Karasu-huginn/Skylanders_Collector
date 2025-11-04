from typing import Annotated, List
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import get_db, engine, Base
import routers.edition_router as edition_router
import routers.item_router as item_router
from fastapi_pagination import add_pagination

app = FastAPI()
app.include_router(edition_router.router)
app.include_router(item_router.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_pagination(app)


Base.metadata.create_all(bind=engine)
db_dep = Annotated[Session, Depends(get_db)]

#* FastAPI endpoints
@app.get("/{item_id}")
def root(item_id:int):
    return {"var":item_id}
