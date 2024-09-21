from fuzzywuzzy import process
import functools
import typing
import asyncio
from typing import List


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return inner


def find_matchking_key(key, dic):
    for possible_key in dic.keys():
        if key.lower() in possible_key.lower():
            return possible_key
    else:
        raise KeyError


def desu_no(string):
    """1 in 3 chance"""
    # method disabled. Since I'm too lazy to remove this method properly, here goes the "fix".

    # number = random.randrange(1, 4)
    #
    # if number == 3:
    #     return string + ' desu no!'
    # else:
    #     return string + '!'

    return string + '!'


def has_bot_helper(member):
    """member needs to be a Discord.Member object"""
    for role in member.roles:
        if role.name == 'BOT Helper':
            return True
    else:
        return False


def has_admin(member):
    """member needs to be a Discord.Member object"""
    for role in member.roles:
        if role.name in ['Moderador', 'Admin']:
            return True
    else:
        return False


def get_ctx_args(ctx_obj):
    return ctx_obj.message.content.replace(ctx_obj.prefix + str(ctx_obj.command) + ' ', '')  # .split(' ')


def message_parser(ctx):
    message = get_ctx_args(ctx_obj=ctx)

    if 'movelist' in message.lower():
        character_name = message.replace('movelist', '')
        character_name = character_name.replace(' ', '')

        return {'get_movelist': character_name}
    else:
        character_name, move = message.split(' ', 1)
        return {'get_move': [character_name, move]}


def sorted_list(list_to_sort):
    """Must be list cointaining two lists"""
    zipped = zip(list_to_sort[0], list_to_sort[1])
    zipped = sorted(zipped, reverse=True)

    first_list = []
    second_list = []

    for item in zipped:
        first_list.append(str(item[0]))
        second_list.append(str(item[1]))

    return [first_list, second_list]


def get_discord_member(arg, members):
    """Finds a matching discord.Member"""
    for member in members:
        # trying first to match the exact provided name
        if arg.lower() == member.name.lower():
            return member
        elif member.nick is not None:
            if arg.lower() == member.nick.lower():
                return member
    else:
        for member in members:
            if arg.lower() in member.name.lower():
                return member
            elif member.nick is not None:
                if arg.lower() in member.nick.lower():
                    return member
                elif arg.lower() in str(member).lower():
                    # searching its tag (#number) name
                    return member
        else:
            return None


@run_in_executor
def string_match(string, list_of_strings):
    for item in list_of_strings:
        if item == string:
            return string

    result = process.extractOne(string, sorted(list_of_strings))
    if result is None:
        raise StringNotFoundError
    if result[1] > 70:
        return result[0]
    else:
        raise StringNotFoundError


@run_in_executor
def string_match_list(string, list_of_strings):
    result = process.extract(string, list_of_strings, limit=5)
    return list(map(lambda tuple_: tuple_[0], result))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def parse_mention(string):
    if '@' in string:
        return ''
    return f'"{string}"'


def get_token(path: str) -> str:
    with open(path, 'r') as file:
        return file.readline()


def split_list(initial_list: List, size_of_each_segment: int) -> List[List]:
    return [initial_list[x:x + size_of_each_segment] for x in range(0, len(initial_list), size_of_each_segment)]


def get_initial_and_last_letter_from_list(desired_list: List[str]) -> List[str]:
    return [desired_list[0][0].upper(), desired_list[-1][0].upper()]


def placeholder_parser(placeholder: str) -> str:
    if placeholder is None:
        return '-'
    if len(placeholder) > 100:
        return placeholder[:97] + '...'
    return placeholder


class StringNotFoundError(Exception):
    pass
