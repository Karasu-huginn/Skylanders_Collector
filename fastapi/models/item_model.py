from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from db import Base

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    details = Column(String, nullable=True)
    type = Column(String)
    edition = Column(Integer, ForeignKey("edition.id"))
    image = Column(String, nullable=True)
    count = Column(Integer, default=0)
    price = Column(Integer, default=0)
    variant = Column(String, nullable=True)
    element = Column(String, nullable=True)
    swapper = Column(Boolean)
    bot_count = Column(Integer, nullable=True)
    top_count = Column(Integer, nullable=True)