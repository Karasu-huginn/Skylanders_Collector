from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db import Base


class Variant(Base):
    __tablename__ = "variant"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship("Item", back_populates="variant")
