from fastapi import APIRouter, Depends, HTTPException
from models.edition_model import Edition
from models.item_model import Item
from base_models import EditionBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/editions", tags=["editions"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_edition(db: db_dep, edition_base:EditionBase):
    create_edition_model = Edition(
        name=edition_base.name,
        release_date=edition_base.release_date)
    db.add(create_edition_model)
    db.commit()
    return {"status":201, "details":"Resource created"}

@router.get("/")
def get_edition(db: db_dep):
    editions = db.query(Edition).all()
    return editions

@router.get("/{edition_id}/items")
def get_edition_items(db: db_dep, edition_id:int):
    items = db.query(Item).filter(Item.edition == edition_id).all()
    return items