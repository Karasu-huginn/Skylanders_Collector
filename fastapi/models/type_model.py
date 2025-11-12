from sqlalchemy import Column, Integer, String, Date
from db import Base

class Type(Base):
    __tablename__ = "type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)