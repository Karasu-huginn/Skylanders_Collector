from sqlalchemy import Column, Integer, String, Date
from db import Base

class Element(Base):
    __tablename__ = "element"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)