from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from starlette import status
from typing import Annotated

from models.element_model import Element
from models.item_model import Item
from base_models import ElementBase, ElementResponse, ItemResponse
from db import get_db

router = APIRouter(prefix="/elements", tags=["elements"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_element(db: db_dep, element_base: ElementBase):
    create_element_model = Element(name=element_base.name)
    db.add(create_element_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("/", response_model=list[ElementResponse])
def get_elements(db: db_dep):
    return db.query(Element).all()


@router.get("/{element_id}", response_model=ElementResponse)
def get_element(db: db_dep, element_id: int):
    element = db.query(Element).filter(Element.id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    return element


@router.get("/{element_id}/items", response_model=list[ItemResponse])
def get_element_items(db: db_dep, element_id: int):
    element = db.query(Element).filter(Element.id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    return (
        db.query(Item)
        .options(
            joinedload(Item.edition),
            joinedload(Item.element),
            joinedload(Item.type),
            joinedload(Item.variant),
        )
        .filter(Item.element_id == element_id)
        .all()
    )
