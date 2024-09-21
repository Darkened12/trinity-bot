from discord import ButtonStyle, Interaction
from discord.ui import Button

from sqlalchemy.sql import select, and_
from app.models.move_model import Move as MoveModel

from ..move_edit_view import MoveEditView


class MoveEditButton(Button):
    def __init__(self):
        super().__init__(label='Edit', style=ButtonStyle.primary, emoji='<:edit:966638166503206933>')

    async def callback(self, interaction: Interaction):
        async with self.view.character.db.session() as session:
            sql = select(MoveModel).where(and_(MoveModel.character_id == self.view.character.data.id)). \
                where(MoveModel.move_name == self.view.current_move)
            query_result = await session.execute(sql)
            move = query_result.first()[0]

        await interaction.response.edit_message(view=MoveEditView(
            character=self.view.character,
            author=self.view.author,
            move=move
        ))
