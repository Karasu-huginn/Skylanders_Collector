from fastapi import APIRouter, Depends, HTTPException
from models.item_model import Item
from base_models import ItemBase
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

@router.get("/{item_id}")
def get_magic_item_details(item_id:int):
    return {}

@router.patch("/{item_id}")
def update_magic_item(item_id:int, count_add:int=0, price:int=0, details:str="", bot_count_add:int=0, top_count_add:int=0):
    return {}
