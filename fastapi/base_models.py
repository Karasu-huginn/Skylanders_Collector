from datetime import datetime
from pydantic import BaseModel

class EditionBase(BaseModel):
    name:str
    release_date: datetime  #* must respect YYYY-MM-DD hh:mm (doubt on MM-DD || DD-MM)

class ItemBase(BaseModel):
    name:str
    details:str
    type : str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str
    element:str
    swapper:bool
    bot_count:int | None
    top_count:int | None