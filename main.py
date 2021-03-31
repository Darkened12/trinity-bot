import sys
import asyncio
from discord import Embed, Game
from discord.ext import menus
from discord.ext.commands import Bot, has_guild_permissions
from discord.ext.commands.errors import CommandNotFound
from discord.utils import find
from database.psql import psql
from database.sqlite import sqlite
from database.file_hosting import DiscordFile
from database.channel_hosting import ChannelHosting
from app import character
from app.servers import Servers
from app.helper import Help
from exceptions import *

# aiopg throwing exception without this
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



global servers_file

TRINITY_COLOR = 0xfedbb6
TRINITY_TOKEN = 'bot token here'

postgres = psql.Database()
servers_file = DiscordFile('servers.db', 'static/databases/')
bo_bleis_channel = 824932611704094770
helper = Help(color=TRINITY_COLOR)

def get_prefix(bot, message):
    if not bot.is_ready():
        return '?'

    server = Servers(db_obj=servers_db, guild_discord_obj=message.guild)
    return '?' if server.bot_prefix is None else server.bot_prefix

bot = Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True)

@bot.event
async def on_guild_join(guild):
    Servers.add_server(servers_db, guild)
    embed = Embed(
        title=f'Hello {guild.name}!',
        description="""I'm only able to work on channels where ?allow has been used by an admin. If you wish to stop me from working on a channel use ?deny!

Use ?help in order to acquaint yourself with my features and have fun!""",
        color=TRINITY_COLOR
    )

    bobleis = ChannelHosting()
    await bobleis.init(bot.get_channel(bo_bleis_channel))
    embed.set_image(url=bobleis.random())

    general_chat = find(lambda x: 'general' in x.name, guild.text_channels)

    if general_chat and general_chat.permissions_for(guild.me).send_messages:
        return await general_chat.send(embed=embed)
    else:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed.title += " (couldn't find the general channel!)"
                return await channel.send(embed=embed)

@bot.event
async def on_ready():
    global servers_db, servers_file

    print('Trinity: Initializing...')

    servers_file.set_channel(bot.get_channel('integer where the db is being hosted'))
    await servers_file.download()
    servers_db = sqlite.Database(db_name='sqlite:///static/databases/servers.db')

    await postgres.init()
    await bot.change_presence(activity=Game(name="?help"))
    print('Trinity: Bot Ready!')

@bot.event
async def on_command_error(ctx, ex):
    if isinstance(ex, CommandNotFound):
        return await ctx.send(f'Command "{ctx.message.content}" does not exist!')
    raise ex

@bot.command()
async def help(ctx):
    server = Servers(db_obj=servers_db, guild_discord_obj=ctx.guild)
    if server.is_channel_allowed(ctx.channel.id):
        class HelpMenu(menus.Menu):
            async def send_initial_message(self, ctx, channel):
                return await channel.send(embed=helper.get_page('main_page'))

            @menus.button('\N{BLACK CIRCLE FOR RECORD}')
            async def on_main_page(self, payload):
                await self.message.edit(embed=helper.get_page('main_page'))

            @menus.button('\N{REGIONAL INDICATOR SYMBOL LETTER F}')
            async def on_frame_data(self, payload):
                await self.message.edit(embed=helper.get_page('frame_data'))

            @menus.button('\N{REGIONAL INDICATOR SYMBOL LETTER S}')
            async def on_server_config(self, payload):
                await self.message.edit(embed=helper.get_page('server_config'))

            @menus.button('\N{REGIONAL INDICATOR SYMBOL LETTER C}')
            async def on_credits(self, payload):
                embed_ = helper.get_page('credits')
                await self.message.edit(embed=embed_)

            @menus.button('\N{BLACK SQUARE FOR STOP}')
            async def on_stop(self, payload):
                bobleis = ChannelHosting()
                await bobleis.init(bot.get_channel(bo_bleis_channel))
                embed = Embed(title='Good Games!', color=helper.color)
                embed.set_image(url=bobleis.random())
                await self.message.edit(embed=embed)
                self.stop()

        menu = HelpMenu()
        await menu.start(ctx)

@bot.command()
async def cf(ctx, *, args):
    return await character.execute(postgres, 1, ctx, args, lang='en-us')

@bot.command()
async def tag(ctx, *, args):
    return await character.execute(postgres, 2, ctx, args, lang='en-us')

@bot.command()
@has_guild_permissions(administrator=True)
async def prefix(ctx, args):
    server = Servers(db_obj=servers_db, guild_discord_obj=ctx.guild)
    server.set_bot_prefix(args)
    await servers_file.upload()
    return await ctx.send(embed=Embed(
        title='This is your new bot prefix:',
        description=args,
        color=TRINITY_COLOR
    ))

@bot.command()
@has_guild_permissions(administrator=True)
async def allow(ctx):
    server = Servers(db_obj=servers_db, guild_discord_obj=ctx.guild)
    server.add_channel_by_id(ctx.channel.id)
    await servers_file.upload()
    return await ctx.send(embed=Embed(
        color=0x00ff00,
        description=f'{ctx.channel.mention} is now allowed :white_check_mark:'
    ))

@bot.command()
@has_guild_permissions(administrator=True)
async def deny(ctx):
    server = Servers(db_obj=servers_db, guild_discord_obj=ctx.guild)
    server.delete_channel_by_id(ctx.channel.id)
    await servers_file.upload()
    return await ctx.send(embed=Embed(
        color=0xff0000,
        description=f'{ctx.channel.mention} is now denied :x:'
    ))

bot.run(TRINITY_TOKEN)
