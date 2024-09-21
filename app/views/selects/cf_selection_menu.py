from discord import User, Interaction
from discord.ui import Select
from app.controllers.character_controller import Character
from app.controllers.database_controller import Database

from typing import List

from app.views.character_view import CharacterView


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
        await interaction.response.edit_message(view=CharacterView(character=character, author=self.author,
                                                                         is_changed_allowed=self.view.is_changed_allowed),
                                                embed=embed, file=icon)
