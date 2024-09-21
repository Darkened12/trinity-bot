import app.views.character_view as character_view

from discord import User, Interaction
from discord.ui import Select

from app.controllers.character_controller import Character
from app.controllers.database_controller import Database

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
        await interaction.response.edit_message(view=character_view.CharacterView(character=character, author=self.author,
                                                                                  is_changed_allowed=self.view.is_changed_allowed),
                                                embed=embed, file=icon)