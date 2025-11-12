from fastapi import APIRouter, Depends, HTTPException
from models.type_model import Type
from base_models import TypeBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/types", tags=["types"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_type(db: db_dep, item_base:TypeBase):
    create_type_model = Type(name=item_base.name)
    db.add(create_type_model)
    db.commit()
    return {"status":201, "details":"Resource created"}

@router.get("/")
def get_items(db: db_dep):
    return db.query(Type).all()

@router.get("/{type_id}")
def get_item_details(db: db_dep, type_id:int):
    return db.query(Type).filter(Type.id == type_id).first()
