from sqlalchemy import Column, ForeignKey, Integer, String, Date
from db import Base

class Swapper(Base):
    __tablename__ = "swapper"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    edition = Column(Integer, ForeignKey("editions.id"))
    image = Column(String, nullable=True)
    variant = Column(String, nullable=True)
    element = Column(String)
    bottom_count = Column(Integer, default=0)
    top_count = Column(Integer, default=0)