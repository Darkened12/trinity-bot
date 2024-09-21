from app import bot
import app.views.move_edit_view as move_edit_view

from discord import User, Interaction, InputTextStyle
from discord.ui import Modal, InputText

from app.controllers.frame_data_updater import FrameDataUpdater
from app.ext.tools import placeholder_parser
from sqlalchemy.sql import select, update
from app.models.move_model import Move as MoveModel
from app.controllers.character_controller import Character


class MoveModal(Modal, FrameDataUpdater):
    def __init__(self, attr: str, move: MoveModel, character: Character, author: User):
        FrameDataUpdater.__init__(self, move=move, character=character, author=author)
        Modal.__init__(self, title=attr, custom_id=attr)
        self.attr = attr
        self.add_move_input_text()
        self.add_notes_input_text()

    def add_move_input_text(self):
        self.add_item(InputText(style=InputTextStyle.paragraph, label=self.attr.title().replace('_', ''),
                                placeholder=placeholder_parser(self.move[self.attr]), min_length=0, max_length=2000,
                                value='',
                                required=True))

    def add_notes_input_text(self):
        self.add_item(InputText(style=InputTextStyle.short, custom_id='change_note', label='Change Reason',
                                placeholder='Not obligatory', min_length=0, max_length=200, value='',
                                required=False))

    async def callback(self, interaction: Interaction):
        old_value = self.move[self.attr]
        await self.update_move()
        await self.on_change(
            target_name=self.attr,
            previous_value=old_value,
            actual_value=self.children[0].value,
            notes=self.children[1].value

        )
        embed, icon, sprite = await self.character.get_move(self.move.move_name, is_changed_allowed=True)
        view = move_edit_view.MoveEditView(self.character, interaction.user, self.move)
        await interaction.response.edit_message(view=view, embed=embed, files=[icon, sprite])

    async def update_move(self):
        async with self.db.session() as session:
            sql = update(MoveModel).values({self.attr: self.children[0].value}).where(MoveModel.id == self.move.id)
            await session.execute(sql)
            await session.commit()

            if self.attr == 'move_name':
                await trinity_bot.update_character_and_move_names()
                await self.character.query()

            sql = select(MoveModel).where(MoveModel.id == self.move.id)
            query_result = await session.execute(sql)
            self.move = query_result.first()[0]
