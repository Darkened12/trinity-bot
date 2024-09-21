import asyncio
from app import bot
from io import BytesIO

from discord import Embed, File, User, Interaction


from app.models.move_model import Move as MoveModel
from app.controllers.character_controller import Character


class FrameDataUpdater:
    def __init__(self, move: MoveModel, character: Character, author: User):
        self.move = move
        self.character = character
        self.db = self.character.db
        self.author = author

    async def callback(self, interaction: Interaction):
        pass

    async def update_move(self):
        pass

    def get_character_icon(self):
        return File(BytesIO(self.character.data.icon), filename='icon.png')

    async def on_change(self, target_name: str, previous_value: str, actual_value: str, notes: str = ''):
        game = 'BBCF' if self.character.game_id == 1 else 'BBTAG'

        embed = Embed()
        embed.title = f'[{game}]: {self.character.data.name} - {self.move.move_name}'
        embed.colour = int(self.character.data.color, 0)

        if notes:
            embed.description = f'Motivo da mudança: {notes}'
        embed.add_field(name='Autor', value=f'{self.author.mention} ({self.author})', inline=False)
        embed.add_field(name='Alvo', value=f'{target_name}', inline=False)
        embed.add_field(name='Valor Antigo', value=f'{previous_value}', inline=False)
        embed.add_field(name='Novo Valor', value=f'{actual_value}', inline=False)
        embed.set_thumbnail(url="attachment://icon.png")

        running_loop = asyncio.get_running_loop()
        running_loop.create_task(trinity_bot.logger.log(embed, files=[self.get_character_icon()]))