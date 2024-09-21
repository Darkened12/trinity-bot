import app.views.move_view as move_view

from discord import ButtonStyle, User, Interaction
from discord.ui import Button, button

from .base_view import BaseView

from .buttons.move_edit_view_button import MoveEditViewButton
from .selects.move_type_selection_menu import MoveTypeSelectionMenu

from app.models.move_model import Move as MoveModel
from app.controllers.character_controller import Character


class MoveEditView(BaseView):
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

        self.add_item(MoveTypeSelectionMenu(custom_id='type', placeholder='Edit Move Type', max_values=1,
                                            row=self.children[-1].row + 1, default_option=self.move.type,
                                            author=self.author, character=self.character, move=self.move))

    @button(label='Back to move', style=ButtonStyle.primary)
    async def back_to_move(self, btn: Button, interaction: Interaction):
        await interaction.response.edit_message(view=await move_view.MoveView(
            character=self.character,
            author=self.author,
            current_move=self.move.move_name,
            is_changed_allowed=True
        ))