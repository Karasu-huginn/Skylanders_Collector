from sqlalchemy import Column, Integer, String, Date
from db import Base

class Variant(Base):
    __tablename__ = "variant"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)