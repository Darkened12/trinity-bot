from .base_model import Base

from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary


class Gatling(Base):
    __tablename__ = 'gatlings'

    def __repr__(self):
        return f'{self.id}'

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    notes = Column(String)
    image = Column(LargeBinary)
