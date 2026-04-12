from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated

from models.type_model import Type
from base_models import TypeBase, TypeResponse
from db import get_db

router = APIRouter(prefix="/types", tags=["types"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_type(db: db_dep, type_base: TypeBase):
    create_type_model = Type(name=type_base.name)
    db.add(create_type_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("/", response_model=list[TypeResponse])
def get_types(db: db_dep):
    return db.query(Type).all()


@router.get("/{type_id}", response_model=TypeResponse)
def get_type(db: db_dep, type_id: int):
    type_obj = db.query(Type).filter(Type.id == type_id).first()
    if not type_obj:
        raise HTTPException(status_code=404, detail="Type not found")
    return type_obj
