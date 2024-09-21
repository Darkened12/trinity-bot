import app.views.character_view as character_view

from sqlalchemy.sql import select, and_

from discord import ButtonStyle, User, Interaction
from discord.ui import Button, button

from .base_view import BaseView

from .buttons.move_hitbox_button import MoveHitboxButton
from .buttons.move_edit_button import MoveEditButton

from app.models.character_model import Character as CharacterModel
from app.models.move_model import Move as MoveModel

from app.controllers.character_controller import Character


class MoveView(BaseView):
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
        await interaction.response.edit_message(view=character_view.CharacterView(character=self.character,
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
