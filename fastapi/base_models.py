from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


# --- Create schemas (accept IDs, used for POST bodies) ---

class EditionBase(BaseModel):
    name: str
    release_date: date


class VariantBase(BaseModel):
    name: str


class TypeBase(BaseModel):
    name: str


class ElementBase(BaseModel):
    name: str


class ItemBase(BaseModel):
    name: str
    details: str
    type_id: int
    edition_id: int
    image: str
    count: int = 0
    price: int = 0
    variant_id: int
    element_id: Optional[int] = None
    swapper: bool
    top_count: Optional[int] = None
    bot_count: Optional[int] = None


# --- Response schemas (nested objects, used for GET responses) ---

class EditionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    release_date: date


class VariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ElementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    details: Optional[str]
    type: TypeResponse
    edition: EditionResponse
    image: Optional[str]
    count: int
    price: int
    variant: VariantResponse
    element: Optional[ElementResponse] = None
    swapper: bool
    top_count: Optional[int]
    bot_count: Optional[int]


class ItemsListResponse(BaseModel):
    items: list[ItemResponse]
