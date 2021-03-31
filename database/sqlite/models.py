from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Server(Base):
    __tablename__ = 'servers'

    def __repr__(self):
        return f'Server {self.server_name} of id {self.server_id}'

    id = Column(Integer, primary_key=True, nullable=False)
    server_id = Column(Integer, nullable=False)
    server_name = Column(String)
    joined_at = Column(DateTime)
    bot_prefix = Column(String)
    allowed_channels = relationship('AllowedChannel', cascade="delete")


class AllowedChannel(Base):
    __tablename__ = 'allowed_channels'

    def __repr__(self):
        return f'Channel {self.channel_name} of id {self.channel_id}'

    id = Column(Integer, primary_key=True, nullable=False)
    channel_id = Column(Integer, nullable=False)
    channel_name = Column(String)

    server_id = Column(Integer, ForeignKey('servers.server_id'))
