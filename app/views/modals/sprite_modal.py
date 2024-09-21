from discord import Interaction, InputTextStyle
from discord.ui import InputText

from .move_modal import MoveModal

from sqlalchemy.sql import update
from app.models.move_model import Move as MoveModel
from app.ext.connection import get_request


class SpriteModal(MoveModal):
    def add_move_input_text(self):
        self.add_item(InputText(style=InputTextStyle.paragraph, label=self.attr.title().replace('_', ''),
                                placeholder='direct image link...', min_length=0, max_length=300, value='',
                                required=True))

    async def callback(self, interaction: Interaction):
        await self.update_move()
        await self.on_change(
            target_name=self.attr,
            previous_value='Not Supported',
            actual_value=self.children[0].value,
            notes=self.children[1].value

        )
        embed, icon, sprite = await self.character.get_move(self.move.move_name, is_changed_allowed=True)
        return await interaction.response.edit_message(embed=embed, files=[icon, sprite])

    async def update_move(self):
        async with self.db.session() as session:
            sprite = await get_request(endpoint=self.children[0].value, mode='content')
            sql = update(MoveModel).values({self.attr: sprite}).where(MoveModel.id == self.move.id)
            await session.execute(sql)
            await session.commit()
