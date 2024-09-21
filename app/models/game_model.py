from .base_model import Base

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String



class Game(Base):
    __tablename__ = 'games'

    def __repr__(self):
        return f"{self.full_name} - {self.short_name}"

    id = Column(Integer, primary_key=True)
    short_name = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    characters = relationship('Character', cascade="delete")
