import sys
import asyncio
import tools
from discord import Embed, Game, Bot, Option, AutocompleteContext, ApplicationContext
from database.psql import psql
from database.channel_logging import ChannelLogging
from app_files.blazblue.character import Character, get_all_characters_names, get_all_move_names, \
    CharacterNotFoundError, MoveNotFoundError
from app_files.blazblue.discord_ui.views import GameSelectionView, CharacterView, MoveView
from exceptions import *
from tools import string_match_list, string_match
from typing import List, Dict

# aiopg throwing exception without this
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TRINITY_COLOR = 0xfedbb6
TRINITY_TOKEN: str = ''  # bot token here
ALLOWED_CHANNEL_ID: int = 000000000000000000  # where frame data can be edited
LOGGING_CHANNEL_ID: int = 000000000000000000  # where frame data edits will be logged

postgres = psql.Database()

bot = Bot()
logger: ChannelLogging

cf_character_names: List[str]
tag_character_names: List[str]
cf_move_names: Dict[str, List]
tag_move_names: Dict[str, List]
games_names: List[str] = ['cf', 'tag']

character_selection_embed = Embed(
    description='Select your character below...',
    color=0xfedbb6
)


async def update_character_and_move_names():
    global cf_character_names, tag_character_names, cf_move_names, tag_move_names
    cf_character_names = await get_all_characters_names(database=postgres, game_id=1)
    tag_character_names = await get_all_characters_names(database=postgres, game_id=2)
    cf_move_names = await get_all_move_names(database=postgres, game_id=1)
    tag_move_names = await get_all_move_names(database=postgres, game_id=2)


def get_game_id(option: str) -> int:
    if 'cf' in option.lower():
        return 1
    return 2


def get_game_id_in_ctx(ctx: AutocompleteContext) -> int:
    if 'game_name' in ctx.options.keys():
        return get_game_id(ctx.options['game_name'])
    else:
        return get_game_id(ctx.command.qualified_name)


def autocomplete_parser(items_: list) -> list:
    if len(items_) >= 25:
        items_[24] = 'and more... just start typing!'
    return items_


async def autocomplete_game(ctx: AutocompleteContext) -> list:
    if ctx.value:
        if type(ctx.value) is str:
            match = await string_match_list(ctx.value, games_names)
            return autocomplete_parser(match)
        else:
            return []
    return autocomplete_parser(games_names)


async def autocomplete_move_names(ctx: AutocompleteContext) -> list:
    if type(ctx.value) is not str:
        return []

    game_id = get_game_id_in_ctx(ctx)
    character_name = ctx.options['character_name']

    if game_id == 1:
        if character_name not in cf_character_names:
            try:
                character_name = await string_match(character_name, cf_character_names)
            except tools.StringNotFoundError:
                return []

        if not ctx.value:
            return autocomplete_parser(cf_move_names[character_name])

        match = await string_match_list(ctx.value, cf_move_names[character_name])
        return autocomplete_parser(match)

    elif game_id == 2:
        if character_name not in tag_character_names:
            try:
                character_name = await string_match(character_name, tag_character_names)
            except tools.StringNotFoundError:
                return []

        if not ctx.value:
            return autocomplete_parser(tag_move_names[character_name])

        match = await string_match_list(ctx.value, tag_move_names[character_name])
        return autocomplete_parser(match)


async def autocomplete_character_names(ctx: AutocompleteContext) -> list:
    if type(ctx.value) is not str:
        return []

    game_id = get_game_id_in_ctx(ctx)
    if game_id == 1:
        if not ctx.value:
            return autocomplete_parser(cf_character_names)
        match = await string_match_list(ctx.value, cf_character_names)
        return autocomplete_parser(match)
    elif game_id == 2:
        if not ctx.value:
            return autocomplete_parser(tag_character_names)
        match = await string_match_list(ctx.value, tag_character_names)
        return autocomplete_parser(match)


@bot.event
async def on_ready():
    global cf_character_names, tag_character_names, cf_move_names, tag_move_names, logger

    print('Trinity: Initializing...')

    logger = ChannelLogging(LOGGING_CHANNEL_ID, bot)
    await postgres.init()
    await update_character_and_move_names()
    await bot.change_presence(activity=Game(name="/help"))

    print('Trinity: Bot Ready!')


@bot.slash_command(description="Opens up the game selection menu")
async def game(ctx: ApplicationContext):
    await ctx.defer()
    view = GameSelectionView(
        database=postgres,
        cf_character_names=cf_character_names,
        tag_character_names=tag_character_names,
        author=ctx.author,
        is_changed_allowed=ctx.channel_id == ALLOWED_CHANNEL_ID
    )

    return await ctx.respond(view=view)


@bot.slash_command(description="Shows information about a character")
async def character(ctx: ApplicationContext,
                    game_name: Option(str, "Enter the game prefix", autocomplete=autocomplete_game),
                    character_name: Option(str, "Enter the character name", autocomplete=autocomplete_character_names),
                    ):
    await ctx.defer()
    try:
        game_id = get_game_id(game_name)
        character_ = Character(database=postgres, name=character_name, game_id=game_id,
                               is_changed_allowed=ctx.channel_id == ALLOWED_CHANNEL_ID)
        await character_.query()
        view = CharacterView(character=character_,
                             author=ctx.author,
                             is_changed_allowed=ctx.channel_id == ALLOWED_CHANNEL_ID)
        embed, file = character_.general_info
        return await ctx.respond(embed=embed, file=file, view=view)
    except CharacterNotFoundError:
        return await ctx.respond(f'Character "{character_name}" was not found!', ephemeral=True)


async def get_move(ctx: ApplicationContext, character_name: str, move_name: str, game_id: int):
    await ctx.defer()
    try:
        character_ = Character(database=postgres, name=character_name, game_id=game_id,
                               is_changed_allowed=ctx.channel_id == ALLOWED_CHANNEL_ID)
        await character_.query()

        embed, icon, sprite = await character_.get_move(move_name)
        view = await MoveView(character=character_, author=ctx.author, current_move=embed.title.split(' - ')[-1],
                              is_changed_allowed=ctx.channel_id == ALLOWED_CHANNEL_ID)
        return await ctx.respond(embed=embed, files=(icon, sprite), view=view)
    except CharacterNotFoundError:
        return await ctx.respond(f'Character "{character_name}" was not found!', ephemeral=True)
    except MoveNotFoundError:
        return await ctx.respond(f'Move "{move_name}" was not found!', ephemeral=True)


@bot.slash_command(description="Shows information about a BlazBlue Centralfiction character's move")
async def cf(ctx: ApplicationContext,
             character_name: Option(str, "Enter the character name", autocomplete=autocomplete_character_names),
             move_name: Option(str, "Enter the move name", autocomplete=autocomplete_move_names)):
    return await get_move(ctx, character_name, move_name, 1)


@bot.slash_command(description="Shows information about a BlazBlue Centralfiction character's move")
async def tag(ctx: ApplicationContext,
              character_name: Option(str, "Enter the character name", autocomplete=autocomplete_character_names),
              move_name: Option(str, "Enter the move name", autocomplete=autocomplete_move_names)):
    return await get_move(ctx, character_name, move_name, 2)


@bot.slash_command(description="Teaches you how to use slash commands")
async def help(ctx: ApplicationContext):
    await ctx.defer(ephemeral=True)
    embed = Embed(description='When you type a "/" (slash) you will see a slash command menu appears. Click on my '
                              'profile picture and you will see all available commands and their descriptions!',
                  color=TRINITY_COLOR)
    embed.set_image(url='https://cdn.discordapp.com/attachments/915436897751433286/966090135609430056/unknown.png')
    return await ctx.respond(embed=embed, ephemeral=True)


if __name__ == '__main__':
    bot.run(TRINITY_TOKEN)
