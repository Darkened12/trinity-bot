from discord import Embed
from database.sqlite import sqlite
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
sqlite.Database.base = Base


class HelpModel(Base):
    __tablename__ = 'help'
    id = Column(Integer, primary_key=True, nullable=False)
    identifier = Column(String, nullable=False, unique=True)
    title = Column(String)
    description = Column(String, nullable=False)
    footer = Column(String)
    image_url = Column(String)
    thumbnail = Column(String)


class Help:
    """Handles the queries from SQLAlchemy"""
    def __init__(self, db_path='sqlite:///static/databases/help.db', color=None):
        self.db = sqlite.Database(db_name=db_path)
        self.color = color

    def get_page(self, identifier):
        page = self.db.session.query(HelpModel).filter(HelpModel.identifier == identifier).first()
        embed = Embed(
            title=page.title,
            description=page.description,
            color=self.color
        )
        if page.image_url is not None:
            embed.set_image(url=page.image_url)
        if page.footer is not None:
            embed.set_footer(text=page.footer)
        if page.thumbnail is not None:
            embed.set_thumbnail(url=page.thumbnail)
        return embed

    def add(self, identifier, description, title=None, image_url=None, footer=None, thumbnail=None):
        self.db.session.add(HelpModel(
            identifier=identifier,
            description=description,
            title=title,
            footer=footer,
            image_url=image_url,
            thumbnail=thumbnail
        ))
        self.db.session.commit()

    def delete(self, identifier):
        obj = self.db.session.query(HelpModel).filter(HelpModel.identifier == identifier).first()
        self.db.session.delete(obj)
        self.db.session.commit()
        