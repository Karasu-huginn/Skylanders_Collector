from datetime import datetime
from pydantic import BaseModel

class EditionBase(BaseModel):
    name:str
    release_date: datetime  #* must respect YYYY-MM-DD hh:mm (doubt on MM-DD || DD-MM)
    
class LevelBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0

class MagicItemBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str

class CreationCrystalBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str
    element:str

class VehicleBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str
    element:str

class TrapBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str
    element:str

class TrapMasterBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str
    element:str

class SwapperBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    variant:str
    element:str
    bottom_count:int = 0
    top_count:int = 0

class GiantBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str
    element:str

class SkylanderBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str
    element:str

class SenseiBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str
    element:str

class VillainSenseiBase(BaseModel):
    name:str
    edition:EditionBase
    image:str
    count:int = 0
    variant:str
    element:str