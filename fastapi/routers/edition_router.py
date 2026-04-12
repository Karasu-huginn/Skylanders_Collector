from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from starlette import status
from typing import Annotated

from models.edition_model import Edition
from models.item_model import Item
from base_models import EditionBase, EditionResponse, ItemResponse
from db import get_db

router = APIRouter(prefix="/editions", tags=["editions"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_edition(db: db_dep, edition_base: EditionBase):
    create_edition_model = Edition(
        name=edition_base.name,
        release_date=edition_base.release_date,
    )
    db.add(create_edition_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("/", response_model=list[EditionResponse])
def get_editions(db: db_dep):
    return db.query(Edition).all()


@router.get("/{edition_id}/items", response_model=list[ItemResponse])
def get_edition_items(db: db_dep, edition_id: int):
    edition = db.query(Edition).filter(Edition.id == edition_id).first()
    if not edition:
        raise HTTPException(status_code=404, detail="Edition not found")
    return (
        db.query(Item)
        .options(
            joinedload(Item.edition),
            joinedload(Item.element),
            joinedload(Item.type),
            joinedload(Item.variant),
        )
        .filter(Item.edition_id == edition_id)
        .all()
    )
