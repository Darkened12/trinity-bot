import datetime
from database.sqlite.models import Server, AllowedChannel


class Servers:
    """Handles the server configuration using SQLAlchemy"""
    def __init__(self, db_obj, guild_discord_obj):
        self._db = db_obj
        self.discord_obj = guild_discord_obj
        self._server_query = self._get_server_query()

        self.name = self._server_query.server_name
        self.joined_at = self._server_query.joined_at
        self.bot_prefix = self._server_query.bot_prefix
        self.allowed_channels = self._server_query.allowed_channels

    def _get_server_query(self):
        query = self._db.session.query(Server)
        filtered_query = query.filter(Server.server_id == self.discord_obj.id)
        return filtered_query.first()

    @staticmethod
    def add_server(database, discord_obj):
        database.session.add(Server(
            server_id=discord_obj.id,
            server_name=discord_obj.name,
            joined_at=datetime.datetime.now(),
        ))
        return database.session.commit()

    def commit(self):
        self._db.session.commit()

    def get_discord_channel(self, channel_id):
        for channel in self.discord_obj.channels:
            if channel.id == channel_id:
                return channel

    def get_channel_by_id(self, channel_id):
        for channel in self.allowed_channels:
            if channel.channel_id == channel_id:
                return channel

    def delete_channel_by_id(self, channel_id):
        for channel in self.allowed_channels:
            if channel.channel_id == channel_id:
                query = self._db.session.query(AllowedChannel)
                desired_channel = query.filter(AllowedChannel.channel_id == channel.channel_id).first()
                if desired_channel:
                    self._db.session.delete(desired_channel)
                    self.commit()
                    return

    def add_channel_by_id(self, channel_id):
        discord_channel = self.get_discord_channel(channel_id)
        self._db.session.add(AllowedChannel(channel_id=discord_channel.id,
                                            channel_name=discord_channel.name,
                                            server_id=self.discord_obj.id))
        self.commit()
        return

    def is_channel_allowed(self, channel_discord_id):
        return channel_discord_id in [channel.channel_id for channel in self.allowed_channels]

    def set_bot_prefix(self, prefix):
        self._db.session.query(Server).filter(Server.server_id == self.discord_obj.id).update({'bot_prefix': prefix})
        self.commit()
        return


if __name__ == '__main__':
    pass
    # database = sqlite.Database(dsn='sqlite_dbs:///database/sqlite_dbs/servers.db', new_database=True)
