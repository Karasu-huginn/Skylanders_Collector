from fastapi import APIRouter, Depends, HTTPException
from models.variant_model import Variant
from models.item_model import Item
from base_models import VariantBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/variants", tags=["variants"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_variant(db: db_dep, item_base:VariantBase):
    create_variant_model = Variant(name=item_base.name)
    db.add(create_variant_model)
    db.commit()
    return {"status":201, "details":"Resource created"}

@router.get("/")
def get_items(db: db_dep):
    return db.query(Variant).all()

@router.get("/{variant_id}")
def get_item_details(db: db_dep, variant_id:int):
    return db.query(Variant).filter(Variant.id == variant_id).first()

@router.get("/{variant_id}/items")
def get_item_details(db: db_dep, variant_id:int):
    return db.query(Item).filter(Item.variant == variant_id).all() #todo paginate ?