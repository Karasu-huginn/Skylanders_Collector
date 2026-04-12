from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from starlette import status
from typing import Annotated

from models.variant_model import Variant
from models.item_model import Item
from base_models import VariantBase, VariantResponse, ItemResponse
from db import get_db

router = APIRouter(prefix="/variants", tags=["variants"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_variant(db: db_dep, variant_base: VariantBase):
    create_variant_model = Variant(name=variant_base.name)
    db.add(create_variant_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("/", response_model=list[VariantResponse])
def get_variants(db: db_dep):
    return db.query(Variant).all()


@router.get("/{variant_id}", response_model=VariantResponse)
def get_variant(db: db_dep, variant_id: int):
    variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant


@router.get("/{variant_id}/items", response_model=list[ItemResponse])
def get_variant_items(db: db_dep, variant_id: int):
    variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return (
        db.query(Item)
        .options(
            joinedload(Item.edition),
            joinedload(Item.element),
            joinedload(Item.type),
            joinedload(Item.variant),
        )
        .filter(Item.variant_id == variant_id)
        .all()
    )
