from discord import User, Interaction
from discord.ui import Select

from app.controllers.frame_data_updater import FrameDataUpdater

from sqlalchemy.sql import update
from app.controllers.character_controller import Character
from app.models.move_model import Move as MoveModel


class MoveTypeSelectionMenu(Select, FrameDataUpdater):
    def __init__(self, character: Character, move: MoveModel, author: User, default_option, custom_id, placeholder,
                 max_values, row):
        Select.__init__(self, custom_id=custom_id, placeholder=placeholder, max_values=max_values, row=row)
        FrameDataUpdater.__init__(self, move=move, character=character, author=author)
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
