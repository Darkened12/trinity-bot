import sqlalchemy
import collections
from sqlalchemy.sql import select, and_

from discord import Embed, ButtonStyle, User, Interaction
from discord.ui import View, Button, button, Item

from .selects import TagSelectionMenu, CFSelectionMenu, MoveSelectionMenu, MoveTypeSelection
from .buttons import CharacterEditButton, MoveHitboxButton, MoveEditButton, MoveEditViewButton

from database.psql.psql import Database
from database.psql.models import Character as CharacterModel, Move as MoveModel
from app_files.blazblue.character import Character, get_all_characters_names
from typing import List
from tools import split_list, get_initial_and_last_letter_from_list


class AuthenticationError(Exception):
    pass


class CustomView(View):
    """Implements user authentication"""

    def __init__(self, author: User, is_change_allowed: bool = False):
        super().__init__()
        self.author: User = author
        self.is_changed_allowed = is_change_allowed

    async def interaction_check(self, interaction: Interaction) -> bool:
        if not interaction.user == self.author:
            raise AuthenticationError
        return True

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        if type(error) is AuthenticationError:
            error_message = "You cannot interact with other user's command!"
            return await interaction.response.send_message(
                error_message,
                ephemeral=True)
        raise error


character_selection_embed = Embed(
    description='Select your character below...',
    color=0xfedbb6
)


class GameSelectionView(CustomView):
    def __init__(self, database: Database, cf_character_names: List[str], tag_character_names: List[str],
                 author: User, is_changed_allowed: bool = False):
        super().__init__(author)
        self.db = database
        self.cf_names = cf_character_names
        self.tag_names = tag_character_names
        self.is_changed_allowed = is_changed_allowed

    @button(label='BlazBlue Centralfiction', style=ButtonStyle.green, emoji='<:cf_icon:966052275686608936>', row=0)
    async def on_cf_selection(self, btn: Button, interaction: Interaction):
        return await interaction.response.edit_message(view=CFSelectionView(
            character_names=self.cf_names,
            database=self.db,
            author=self.author,
            is_change_allowed=self.is_changed_allowed
        ), embed=character_selection_embed)

    @button(label='BlazBlue Cross Tag Battle', style=ButtonStyle.primary, emoji='<:tag_icon:966052796753379358>', row=0)
    async def on_tag_selection(self, btn: Button, interaction: Interaction):
        view = await TagSelectionView(
            database=self.db,
            author=self.author,
            is_change_allowed=self.is_changed_allowed
        )
        await interaction.response.edit_message(view=view, embed=character_selection_embed)


class TagSelectionView(CustomView):
    def __init__(self, author: User, database: Database, is_change_allowed: bool = False):
        super().__init__(author=author, is_change_allowed=is_change_allowed)
        self.db = database

    def __await__(self):
        return self.init().__await__()

    @staticmethod
    def parse_query_result(query_result: sqlalchemy.engine.ScalarResult) -> dict:
        parsed_result = {}
        for game_prefix, character_name in query_result.all():
            if game_prefix in ['AB', 'AH', 'SK']:
                game_prefix = 'Other games'
            if game_prefix not in parsed_result.keys():
                parsed_result.update({game_prefix: []})
            parsed_result[game_prefix].append(character_name)
        return parsed_result

    async def init(self) -> object:
        async with self.db.session() as session:
            c = CharacterModel
            sql = select(c.game_prefix, c.name).where(c.game_id == 2).order_by(c.game_prefix, c.name)
            query_result = await session.execute(sql)

        parsed_result = self.parse_query_result(query_result)
        menus: List[TagSelectionMenu] = []
        for game_prefix, characters in zip(parsed_result.keys(), parsed_result.values()):
            menus.append(TagSelectionMenu(
                placeholder=game_prefix.upper(),
                characters=characters,
                database=self.db,
                author=self.author
            ))
        menus_deque = collections.deque(menus)
        menus_deque.rotate(-1)
        for item in list(menus_deque):
            self.add_item(item)
        return self


class CFSelectionView(CustomView):
    def __init__(self, character_names: List[str], database: Database, author: User,
                 is_change_allowed: bool = False):
        super().__init__(author=author)
        self.character_names = character_names
        self.database = database
        self.game_id = 1
        self.is_changed_allowed = is_change_allowed

        for list_of_names in split_list(self.character_names, 9):
            self.add_item(CFSelectionMenu(character_names=list_of_names,
                                          initial_letters=get_initial_and_last_letter_from_list(list_of_names),
                                          database=self.database,
                                          author=author))


class CharacterView(CustomView):
    cf_parser = {
            'normals': 'Normals and Drives',
            'drives': 'Normals and Drives',
            'orphans': 'Normals and Drives',
            'specials': 'Specials',
            'extra skills': 'Specials',
            'partner skills': 'Specials',
            'skills': 'Specials',
            'universal mechanics': 'Universal Mechanics and Supers',
            'astral heat': 'Universal Mechanics and Supers',
            'exceed accel': 'Universal Mechanics and Supers',
            'distortion skills': 'Universal Mechanics and Supers',
            'distortion skill': 'Universal Mechanics and Supers',
            'distortion drives': 'Universal Mechanics and Supers',
        }
    tag_parser = {
            'normals': 'Normals and Partner Skills',
            'drives': 'Normals and Partner Skills',
            'orphans': 'Normals and Partner Skills',
            'specials': 'Specials',
            'extra skills': 'Specials',
            'partner skills': 'Normals and Partner Skills',
            'skills': 'Specials',
            'universal mechanics': 'Universal Mechanics and Supers',
            'astral heat': 'Universal Mechanics and Supers',
            'exceed accel': 'Universal Mechanics and Supers',
            'distortion skills': 'Universal Mechanics and Supers',
            'distortion skill': 'Universal Mechanics and Supers',
            'distortion drives': 'Universal Mechanics and Supers',
        }

    def __init__(self, character: Character, author: User, is_changed_allowed: bool = False):
        super().__init__(author=author)
        self.character = character
        self.is_changed_allowed = is_changed_allowed

        if self.is_changed_allowed:
            self.add_item(CharacterEditButton())

        parsed_types = self.move_selection_parsing()
        for type_, move_names in zip(parsed_types.keys(), parsed_types.values()):
            for list_of_names in split_list(move_names, 25):
                self.add_item(MoveSelectionMenu(
                    placeholder=type_,
                    move_names=list_of_names,
                    character=self.character,
                    author=self.author
                ))

    def move_selection_parsing(self) -> dict:
        parser = self.cf_parser if self.character.data.game_id == 1 else self.tag_parser
        result = {
            f'Normals{" and Drives" if self.character.data.game_id == 1 else " and Partner Skills"}': [],
            'Specials': [],
            'Universal Mechanics and Supers': [],
        }
        move_names_with_types = self.character.move_names_with_types_to_dict
        for type_, move_names in zip(move_names_with_types.keys(), move_names_with_types.values()):
            parsed_type = parser[type_]
            result[parsed_type] += move_names
        return result

    @button(label='Back to character selection', custom_id='character_selection', style=ButtonStyle.gray, row=0)
    async def character_selection(self, btn: Button, interaction: Interaction):
        names = await get_all_characters_names(database=self.character.db, game_id=self.character.game_id)
        if self.character.game_id == 1:
            return await interaction.response.edit_message(embed=character_selection_embed, view=CFSelectionView(
                database=self.character.db,
                character_names=names,
                author=self.author,
                is_change_allowed=self.is_changed_allowed
            ), files=[])
        view = await TagSelectionView(
            database=self.character.db,
            author=self.author,
            is_change_allowed=self.is_changed_allowed
        )
        await interaction.response.edit_message(embed=character_selection_embed, view=view, files=[])


class MoveView(CustomView):
    def __init__(self, character: Character, author: User, current_move: str, is_changed_allowed: bool = False):
        super().__init__(author=author)
        self.character = character
        self.current_move = current_move
        self.is_changed_allowed = is_changed_allowed
        self.hitbox_state = False
        self.hitbox_button = MoveHitboxButton()

        # hitbox button is currently disabled.

        # self.add_item(self.hitbox_button)
        # self.children.append(self.children[-2])
        # self.children.pop(-3)

        if self.is_changed_allowed:
            self.add_item(MoveEditButton())

    def __await__(self):
        return self.init().__await__()

    async def init(self):
        self.hitbox_state = await self.has_hitbox()
        if not self.hitbox_state:
            self.hitbox_button.disabled = True
        return self

    async def has_hitbox(self):
        async with self.character.db.session() as session:
            sql = select(MoveModel.id).join(CharacterModel, CharacterModel.id == MoveModel.character_id). \
                where(and_(MoveModel.character_id == self.character.data.id)). \
                where(and_(MoveModel.move_name == self.current_move)). \
                where(MoveModel.hitbox != None)

            query_result = await session.execute(sql)
            null_check = query_result.first()
            return null_check is not None

    async def get_move_index(self):
        try:
            return self.character.movelist.index(self.current_move)
        except ValueError:
            await self.character.query()
            return self.character.movelist.index(self.current_move)

    @button(label='', custom_id='previous_move', style=ButtonStyle.gray, emoji='◀️')
    async def previous_move(self, btn: Button, interaction: Interaction):
        move_index = await self.get_move_index()
        self.current_move = self.character.movelist[move_index - 1]
        await self.hitbox_button.on_move_change()
        embed, icon, sprite = await self.character.get_move(self.current_move,
                                                            is_changed_allowed=self.is_changed_allowed)
        await interaction.response.edit_message(view=self, embed=embed, files=[icon, sprite])

    @button(label='Back to move selection', custom_id='move_selection', style=ButtonStyle.gray)
    async def move_selection(self, btn: Button, interaction: Interaction):
        embed, icon = self.character.general_info
        await interaction.response.edit_message(view=CharacterView(character=self.character,
                                                                   author=self.author,
                                                                   is_changed_allowed=self.is_changed_allowed),
                                                embed=embed, file=icon)

    @button(label='', custom_id='next_move', style=ButtonStyle.gray, emoji='▶️')
    async def next_move(self, btn: Button, interaction: Interaction):
        move_index = await self.get_move_index()
        self.current_move = self.character.movelist[move_index + 1]
        await self.hitbox_button.on_move_change()
        embed, icon, sprite = await self.character.get_move(self.current_move,
                                                            is_changed_allowed=self.is_changed_allowed)
        await interaction.response.edit_message(view=self, embed=embed, files=[icon, sprite])


class MoveEditView(CustomView):
    def __init__(self, character: Character, author: User, move: MoveModel):
        super().__init__(author=author)
        self.character = character
        self.move = move

        attrs = ['move_name', 'notes', 'damage', 'startup', 'active', 'recovery', 'frame_adv', 'guard', 'attribute',
                 'blockstun', 'prorate', 'invul', 'sprite', 'hitbox']

        for n, attr in enumerate(attrs):
            row = 0
            if n >= 12:
                row = 3
            elif n >= 8:
                row = 2
            elif n >= 4:
                row = 1

            self.add_item(MoveEditViewButton(label=attr, style=ButtonStyle.gray, custom_id=attr, row=row))

        self.add_item(MoveTypeSelection(custom_id='type', placeholder='Edit Move Type', max_values=1,
                                        row=self.children[-1].row + 1, default_option=self.move.type,
                                        author=self.author, character=self.character, move=self.move))

    @button(label='Back to move', style=ButtonStyle.primary)
    async def back_to_move(self, btn: Button, interaction: Interaction):
        await interaction.response.edit_message(view=await MoveView(
            character=self.character,
            author=self.author,
            current_move=self.move.move_name,
            is_changed_allowed=True
        ))
