from .base_model import Base

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary


class Character(Base):
    __tablename__ = 'characters'

    def __repr__(self):
        return f'{self.name}'

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'))
    game_prefix = Column(String)
    moves = relationship('Move', cascade='delete')

    health = Column(String)
    combo_rate = Column(String)
    jump_startup = Column(String)
    dash = Column(String)
    unique_movement = Column(String)
    notes = Column(String)
    color = Column(String)
    icon = Column(LargeBinary)
