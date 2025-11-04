from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class EditionBase(BaseModel):
    name:str
    release_date: datetime  #* must respect YYYY-MM-DD hh:mm (doubt on MM-DD || DD-MM)

class ItemBase(BaseModel):
    name:str
    details:str
    type : str
    edition:int
    image:str
    count:int = 0
    price:int = 0
    variant:str
    element:str
    swapper:bool
    top_count:Optional[int] = None
    bot_count:Optional[int] = None