from discord import User, Interaction
from discord.ui import Select

import app_files.blazblue.discord_ui.views as views
import app_files.blazblue.discord_ui.modals as modals

from sqlalchemy.sql import update
from app_files.blazblue.character import Character
from database.psql.psql import Database
from database.psql.models import Move as MoveModel
from typing import List


class TagSelectionMenu(Select):
    def __init__(self, placeholder: str, characters: List[str], database: Database, author: User):
        super().__init__(placeholder=placeholder, min_values=1, max_values=1)
        self.database = database
        self.author = author

        for character in characters:
            self.add_option(label=character)

    async def callback(self, interaction: Interaction):
        character = Character(database=self.database, game_id=2, name=self.values[0],
                              is_changed_allowed=self.view.is_changed_allowed)
        await character.query()
        embed, icon = character.general_info
        await character.query()
        await interaction.response.edit_message(view=views.CharacterView(character=character, author=self.author,
                                                                         is_changed_allowed=self.view.is_changed_allowed),
                                                embed=embed, file=icon)


class CFSelectionMenu(Select):
    def __init__(self, character_names: List[str],
                 initial_letters: List[str],
                 database: Database,
                 author: User = None):
        super().__init__(
            placeholder=f"{initial_letters[0]} to {initial_letters[1]}...",
            min_values=1,
            max_values=1,
        )
        self.database = database
        self.game_id = 1
        self.author = author
        for name in character_names:
            self.add_option(label=name)

    async def callback(self, interaction: Interaction):
        character = Character(database=self.database, game_id=self.game_id, name=self.values[0],
                              is_changed_allowed=self.view.is_changed_allowed)
        await character.query()
        embed, icon = character.general_info
        await character.query()
        await interaction.response.edit_message(view=views.CharacterView(character=character, author=self.author,
                                                                         is_changed_allowed=self.view.is_changed_allowed),
                                                embed=embed, file=icon)


class MoveSelectionMenu(Select):
    def __init__(self, placeholder: str, move_names: List[str],
                 character: Character,
                 author: User = None):
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
        )
        self.character = character
        self.author = author

        for name in move_names:
            self.add_option(label=name)

    async def callback(self, interaction: Interaction):
        parsed_name = self.character.move_type_parsing(self.values[0])
        embed, icon, sprite = await self.character.get_move(parsed_name,
                                                            is_changed_allowed=self.view.is_changed_allowed)
        await interaction.response.edit_message(view=await views.MoveView(character=self.character,
                                                                          author=self.author,
                                                                          current_move=embed.title.split(' - ')[-1],
                                                                          is_changed_allowed=self.view.is_changed_allowed),
                                                embed=embed, files=[icon, sprite])


class MoveTypeSelection(Select, modals.FrameDataUpdate):
    def __init__(self, character: Character, move: MoveModel, author: User, default_option, custom_id, placeholder,
                 max_values, row):
        Select.__init__(self, custom_id=custom_id, placeholder=placeholder, max_values=max_values, row=row)
        modals.FrameDataUpdate.__init__(self, move=move, character=character, author=author)
        self.character = character
        self.move = move

        options = [
            'normals',
            'drives',
            'specials',
            'universal mechanics',
            'skills',
            'extra skills',
            'partner skills',
            'distortion skills',
            'astral heat',
            'orphans'
        ]
        for option in options:
            self.add_option(label=option, default=option == default_option)

    async def callback(self, interaction: Interaction):
        old_value = self.move.type
        await self.update_move()
        await self.on_change(
            target_name='type',
            previous_value=old_value,
            actual_value=self.values[0],
            notes=''
        )
        embed, icon, sprite = await self.character.get_move(self.move.move_name,
                                                            is_changed_allowed=True)

        for option in self.options:
            if option.label == self.values[0]:
                option.default = True
            else:
                option.default = False

        return await interaction.message.edit(embed=embed, view=self.view, files=[icon, sprite])

    async def update_move(self):
        async with self.db.session() as session:
            sql = update(MoveModel).values(type=self.values[0]).where(MoveModel.id == self.move.id)
            await session.execute(sql)
            await session.commit()
        await self.character.query()
