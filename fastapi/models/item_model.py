from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db import Base


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    details = Column(String, nullable=True)
    type_id = Column("type", Integer, ForeignKey("type.id"), index=True)
    edition_id = Column("edition", Integer, ForeignKey("edition.id"), index=True)
    image = Column(String, nullable=True)
    count = Column(Integer, default=0)
    price = Column(Integer, default=0)
    variant_id = Column("variant", Integer, ForeignKey("variant.id"), index=True)
    element_id = Column("element", Integer, ForeignKey("element.id"), index=True, nullable=True)
    swapper = Column(Boolean)
    bot_count = Column(Integer, nullable=True)
    top_count = Column(Integer, nullable=True)

    type = relationship("Type", back_populates="items")
    edition = relationship("Edition", back_populates="items")
    variant = relationship("Variant", back_populates="items")
    element = relationship("Element", back_populates="items")
