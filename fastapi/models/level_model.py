from sqlalchemy import Column, ForeignKey, Integer, String, Date
from db import Base

class Level(Base):
    __tablename__ = "level"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    edition = Column(Integer, ForeignKey("editions.id"))
    image = Column(String, nullable=True)
    count = Column(Integer, default=0)