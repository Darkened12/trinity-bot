from discord import User, Interaction
from discord.ui import Select

from app.controllers.character_controller import Character
from ..move_view import MoveView

from typing import List


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
        await interaction.response.edit_message(view=await MoveView(character=self.character,
                                                                          author=self.author,
                                                                          current_move=embed.title.split(' - ')[-1],
                                                                          is_changed_allowed=self.view.is_changed_allowed),
                                                embed=embed, files=[icon, sprite])
