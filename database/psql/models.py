from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Game(Base):
    __tablename__ = 'games'

    def __repr__(self):
        return f"{self.full_name} - {self.short_name}"

    id = Column(Integer, primary_key=True)
    short_name = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    characters = relationship('Character', cascade="delete")


class Character(Base):
    __tablename__ = 'characters'

    def __repr__(self):
        return f'{self.name}'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'))
    moves = relationship('Move', cascade='delete')

    health = Column(String)
    combo_rate = Column(String)
    jump_startup = Column(String)
    dash = Column(String)
    notes = Column(String)
    color = Column(String)
    icon = Column(LargeBinary)


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
    hitbox = Column(String)
    notes = Column(String)
    sprite = Column(LargeBinary)


if __name__ == '__main__':
    import asyncio
    from database.psql import Database
    Database.Base = Base

    async def run():
        db = await Database(new_database=True)

    asyncio.get_event_loop().run_until_complete(run())
