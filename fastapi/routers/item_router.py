from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from models.item_model import Item
from base_models import ItemBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/items", tags=["items"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(db: db_dep, item_base:ItemBase):
    create_item_model = Item(
        name=item_base.name,
        details=item_base.details,
        type=item_base.type,
        edition=item_base.edition,
        image=item_base.image,
        count=item_base.count,
        variant=item_base.variant,
        element=item_base.element,
        swapper=item_base.swapper,
        bot_count=item_base.bot_count,
        top_count=item_base.top_count
)
    db.add(create_item_model)
    db.commit()
    return {"status":201, "details":"Resource created"}

@router.get("/")
def get_items(db: db_dep, search:str="", variant:str="", is_captured:bool=False, is_uncaptured:bool=False, is_duplicate:bool=False, item_type:str="", element:str="", page:int=1,limit:int=10):
    filters = []
    if search:
        filters.append(Item.name.ilike("%"+search+"%"))
    if variant:
        filters.append(Item.variant.ilike("%"+variant+"%")) #todo transfer to DB's variant
    if is_captured:
        filters.append(Item.count > 0) #! won't work for swappers, complete when testable with front
    if is_uncaptured:
        filters.append(Item.count == 0) #! won't work for swappers, complete when testable with front
    if is_duplicate:
        filters.append(Item.count > 1) #! won't work for swappers, complete when testable with front
    if item_type:
        filters.append(Item.type.ilike("%"+item_type+"%")) #todo transfer to DB's variant
    if element:
        filters.append(Item.element.ilike("%"+element+"%")) #todo transfer to DB's variant
    if filters:
        query = db.query(Item).filter(and_(*filters))
    return query.offset((page-1)*limit).limit(limit).all()

@router.get("/{item_id}")
def get_item_details(db: db_dep, item_id:int):
    items = db.query(Item).filter(Item.id == item_id).first()
    return items

@router.patch("/{item_id}")
def update_item(db: db_dep, item_id:int, count_add:int=0, price:int=0, details:str="", bot_count_add:int=0, top_count_add:int=0):
    if bot_count_add or top_count_add:
        update_dict = {
        "price": price if price else Item.price,
        "details": details if details else Item.details,
        "top_count":Item.top_count + top_count_add,
        "bot_count":Item.bot_count + bot_count_add
        }
    else:
        update_dict = {
        "count":Item.count + count_add,
        "price": price if price else Item.price,
        "details": details if details else Item.details
        }
    db.query(Item).filter(Item.id == item_id).update(update_dict)
    db.commit()
    return {}
