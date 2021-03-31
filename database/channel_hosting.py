import random


class ChannelHosting:
    """Gets all attachments on all messages from a given Discord channel"""
    def __init__(self):
        self.channel_obj = None
        self.files = []

    async def init(self, channel_obj):
        self.channel_obj = channel_obj
        async for message in self.channel_obj.history():
            for file in message.attachments:
                self.files.append(file.url)
        return self

    def random(self):
        return random.choice(self.files)