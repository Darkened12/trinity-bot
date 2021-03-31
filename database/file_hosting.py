from conn.connection import get_request
from data_handling import write_file
from exceptions import ChannelNotSetError
from discord import File


class DiscordFile:
    """Handles file hosting on a Discord channel"""
    def __init__(self, file_name, file_path=''):
        self.discord_channel = None
        self.file_name = file_name
        self.file_path = file_path

    def set_channel(self, discord_channel):
        self.discord_channel = discord_channel

    async def download(self):
        if self.discord_channel is None:
            raise ChannelNotSetError

        message = await self.discord_channel.fetch_message(self.discord_channel.last_message_id)
        file = await get_request(message.attachments[0].url, mode='read')
        return await write_file(self.file_path + self.file_name, file, mode='wb')

    async def upload(self):
        if self.discord_channel is None:
            raise ChannelNotSetError
        return await self.discord_channel.send(file=File(filename=self.file_name, fp=self.file_path + self.file_name))
