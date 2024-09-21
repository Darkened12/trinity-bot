import asyncio

from app.bot import bot as trinity
from app.bot import BOT_TOKEN

loop = asyncio.get_event_loop()
loop.create_task(trinity.start(BOT_TOKEN))  # you can keep adding more tasks (bots) if you want here
loop.run_forever()
