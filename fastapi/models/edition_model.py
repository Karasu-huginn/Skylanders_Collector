from sqlalchemy import Column, ForeignKey, Integer, String, Date
from db import Base

class Editions(Base):
    __tablename__ = "editions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    release_date = Column(Date)