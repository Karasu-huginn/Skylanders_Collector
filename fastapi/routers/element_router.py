from fastapi import APIRouter, Depends, HTTPException
from models.element_model import Element
from models.item_model import Item
from base_models import ElementBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/elements", tags=["elements"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_element(db: db_dep, item_base:ElementBase):
    create_element_model = Element(name=item_base.name)
    db.add(create_element_model)
    db.commit()
    return {"status":201, "details":"Resource created"}

@router.get("/")
def get_items(db: db_dep):
    return db.query(Element).all()

@router.get("/{element_id}")
def get_item_details(db: db_dep, element_id:int):
    return db.query(Element).filter(Element.id == element_id).first()

@router.get("/{element_id}/items")
def get_item_details(db: db_dep, element_id:int):
    return db.query(Item).filter(Item.element == element_id).all() #todo paginate ?