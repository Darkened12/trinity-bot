from discord import Bot, Embed
from typing import Union


class ChannelLogging:
    def __init__(self, channel_id: int, bot: Bot):
        self.channel_id = channel_id
        self.bot = Bot
        self.channel = bot.get_channel(channel_id)

    async def log(self, message: Union[str, Embed], files: list = None):
        if files is None:
            files = []
        if type(message) == str:
            return await self.channel.send(message)
        elif isinstance(message, Embed):
            if files:
                if len(files) > 1:
                    return await self.channel.send(embed=message, files=files)
                return await self.channel.send(embed=message, file=files[0])
            return await self.channel.send(embed=message)
        raise TypeError('message should be str or embed')
