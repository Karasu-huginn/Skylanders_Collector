from sqlalchemy import Column, ForeignKey, Integer, String, Date
from db import Base

class VillainSensei(Base):
    __tablename__ = "villain_sensei"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    edition = Column(Integer, ForeignKey("editions.id"))
    image = Column(String, nullable=True)
    count = Column(Integer, default=0)
    variant = Column(String, nullable=True)
    element = Column(String)