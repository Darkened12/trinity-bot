import random
from app.ext.connection import is_url_ok


class ChannelHosting:
    """Gets all attachments on all messages from a given Discord channel"""
    def __init__(self):
        self.channel_obj = None
        self.files = []

    async def init(self, channel_obj):
        self.channel_obj = channel_obj
        async for message in self.channel_obj.history():
            for file in message.attachments:
                url_status = await is_url_ok(file.url)
                if url_status:
                    self.files.append(file.url)
        return self

    async def update(self):
        self.files = []
        await self.init(self.channel_obj)

    def random(self):
        return random.choice(self.files)