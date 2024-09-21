from .base_model import Base

from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary


class Move(Base):
    __tablename__ = 'moves'

    def __repr__(self):
        return f'{self.move_name}'

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'))

    move_name = Column(String)
    damage = Column(String)
    cancel = Column(String)
    prorate = Column(String)
    attribute = Column(String)
    guard = Column(String)
    startup = Column(String)
    active = Column(String)
    recovery = Column(String)
    frame_adv = Column(String)
    level = Column(String)
    starter = Column(String)
    blockstun = Column(String)
    hitstun = Column(String)
    untechable = Column(String)
    hitstunch = Column(String)
    untechch = Column(String)
    blockstop = Column(String)
    hitstop = Column(String)
    chstop = Column(String)
    invul = Column(String)
    hitbox = Column(LargeBinary)
    type = Column(String)
    notes = Column(String)
    sprite = Column(LargeBinary)
