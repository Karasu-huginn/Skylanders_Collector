from sqlalchemy import Column, Integer, String, Date
from db import Base

class Edition(Base):
    __tablename__ = "edition"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    release_date = Column(Date) #* must respect YYYY-MM-DD hh:mm (doubt on MM-DD || DD-MM)