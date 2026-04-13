from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from starlette import status
from typing import Annotated, Optional

from models.item_model import Item
from base_models import ItemBase, ItemResponse, ItemsListResponse
from db import get_db

router = APIRouter(prefix="/items", tags=["items"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(db: db_dep, item_base: ItemBase):
    create_item_model = Item(
        name=item_base.name,
        details=item_base.details,
        type_id=item_base.type_id,
        edition_id=item_base.edition_id,
        image=item_base.image,
        count=item_base.count,
        variant_id=item_base.variant_id,
        element_id=item_base.element_id,
        swapper=item_base.swapper,
        bot_count=item_base.bot_count,
        top_count=item_base.top_count,
    )
    db.add(create_item_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("", response_model=ItemsListResponse)
def get_items(
    db: db_dep,
    search: str = "",
    is_captured: bool = False,
    is_uncaptured: bool = False,
    is_duplicate: bool = False,
    page: int = 1,
    limit: int = 10,
):
    filters = []
    if search:
        filters.append(Item.name.ilike("%" + search + "%"))
    if is_captured:
        filters.append(Item.count > 0)
    if is_uncaptured:
        filters.append(Item.count == 0)
    if is_duplicate:
        filters.append(Item.count > 1)
    query = db.query(Item).options(
        joinedload(Item.edition),
        joinedload(Item.element),
        joinedload(Item.type),
        joinedload(Item.variant),
    )
    if filters:
        query = query.filter(and_(*filters))
    items = query.offset((page - 1) * limit).limit(limit).all()
    return {"items": items}


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(db: db_dep, item_id: int):
    item = (
        db.query(Item)
        .options(
            joinedload(Item.edition),
            joinedload(Item.element),
            joinedload(Item.type),
            joinedload(Item.variant),
        )
        .filter(Item.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}")
def update_item(
    db: db_dep,
    item_id: int,
    count_add: int = 0,
    price: Optional[int] = None,
    details: str = "",
    bot_count_add: int = 0,
    top_count_add: int = 0,
):
    if bot_count_add or top_count_add:
        update_dict = {
            "price": price if price is not None else Item.price,
            "details": details if details else Item.details,
            "top_count": Item.top_count + top_count_add,
            "bot_count": Item.bot_count + bot_count_add,
        }
    else:
        update_dict = {
            "count": Item.count + count_add,
            "price": price if price is not None else Item.price,
            "details": details if details else Item.details,
        }
    try:
        rows = db.query(Item).filter(Item.id == item_id).update(update_dict)
        if rows == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Resource could not be updated")
    return {"status": 200, "details": "Resource updated"}
