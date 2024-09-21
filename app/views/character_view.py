from discord import User, ButtonStyle, Interaction
from discord.ui import button, Button
import app.views.cf_selection_view as cf_selection_view

from app.controllers.character_controller import Character, get_all_characters_names
from app.ext.tools import split_list
from app.views.base_view import BaseView, character_selection_embed
from app.views.buttons.character_edit_button import CharacterEditButton

from app.views.selects.move_selection_menu import MoveSelectionMenu
from app.views.tag_selection_view import TagSelectionView


class CharacterView(BaseView):
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
            'Universal Mechanics and Supers': ['Gatlings'],
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
            return await interaction.response.edit_message(embed=character_selection_embed, view=cf_selection_view.CFSelectionView(
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