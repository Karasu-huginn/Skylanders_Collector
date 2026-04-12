from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from db import Base


class Edition(Base):
    __tablename__ = "edition"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    release_date = Column(Date)  # YYYY-MM-DD

    items = relationship("Item", back_populates="edition")
