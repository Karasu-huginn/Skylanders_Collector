from fastapi import APIRouter, Depends, HTTPException
from models.magic_item_model import MagicItem
from base_models import MagicItemBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/magic_items", tags=["magic_items"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_magic_item():
    return {}
#todo create sql insert statement

@router.get("/")
def get_magic_items(search:str="",page:int=1,limit:int=10):
    return {}

@router.patch("/")
def add_magic_item():
    return {}
#todo get var from link without query param



"""
@router.get("/")
def get_(search:str="",page:int=1,limit:int=10):
    return {}
    
@router.patch("/")
def add_():
    return {}
"""