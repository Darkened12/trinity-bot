import asyncio
from app import bot
import app.views.character_view as character_view

from io import BytesIO
from app.ext.tools import placeholder_parser

from discord import Embed, File, User, Interaction, InputTextStyle
from discord.ui import Modal, InputText

from sqlalchemy.sql import select
from app.models.character_model import Character as CharacterModel
from app.controllers.character_controller import Character



class CharacterModal(Modal):  # a lot of things here should be moved to controllers.
    def __init__(self, character: Character, author: User):
        super().__init__(title=f'{character.data.name} - Stats')
        self.author = author
        self.character = character

        self.add_item(InputText(style=InputTextStyle.short, custom_id='health', label='Health',
                                placeholder=placeholder_parser(character.data.health), min_length=4, max_length=5,
                                value='',
                                required=False))
        self.add_item(InputText(style=InputTextStyle.short, custom_id='jump_startup', label='Jump Startup',
                                placeholder=placeholder_parser(character.data.jump_startup), min_length=1, max_length=2,
                                value='',
                                required=False))

        self.add_item(InputText(style=InputTextStyle.paragraph, custom_id='dash', label='Dash',
                                placeholder=placeholder_parser(character.data.dash), min_length=0, max_length=200,
                                value='',
                                required=False))

        self.add_item(InputText(style=InputTextStyle.paragraph, custom_id='unique_movement', label='Unique Movement',
                                placeholder=placeholder_parser(character.data.unique_movement), min_length=0,
                                max_length=200, value='',
                                required=False))

        self.add_item(InputText(style=InputTextStyle.short, custom_id='change_note', label='Change Reason',
                                placeholder='Not obligatory', min_length=0, max_length=100, value='',
                                required=False))

    async def callback(self, interaction: Interaction):
        async with self.character.db.session() as session:
            sql = select(CharacterModel).where(CharacterModel.id == self.character.data.id)
            query_result = await session.execute(sql)
            new_character: CharacterModel = query_result.first()[0]
            for input_text in self.children:
                if input_text.value != '' and input_text.custom_id != 'change_note':
                    old_value = new_character[input_text.custom_id]
                    new_character[input_text.custom_id] = input_text.value
                    await self.on_change(input_text.custom_id, old_value, input_text.value,
                                         notes=self.children[-1].value)
            await session.commit()
            await session.flush()

        new_character_obj = Character(self.character.db, self.character.data.name, self.character.game_id)
        await new_character_obj.query()
        embed, icon = new_character_obj.general_info
        return await interaction.response.edit_message(embed=embed,
                                                       view=character_view.CharacterView(new_character_obj, self.author,
                                                                                         is_changed_allowed=True),
                                                       file=icon)

    async def on_change(self, target_name: str, previous_value: str, actual_value: str, notes: str = ''):
        game = 'BBCF' if self.character.game_id == 1 else 'BBTAG'

        embed = Embed()
        embed.title = f'[{game}]: {self.character.data.name} - Stats'
        embed.colour = int(self.character.data.color, 0)

        if notes:
            embed.description = f'Motivo da mudança: {notes}'
        embed.add_field(name='Autor', value=f'{self.author.mention} ({self.author})', inline=False)
        embed.add_field(name='Alvo', value=f'{target_name}', inline=False)
        embed.add_field(name='Valor Antigo', value=f'{previous_value}', inline=False)
        embed.add_field(name='Novo Valor', value=f'{actual_value}', inline=False)
        embed.set_thumbnail(url="attachment://icon.png")

        # message = f'**{self.author}** editou o personagem de {game}` {self.character.data.name}` e alterou `' \
        #           f'{target_name}`: de `{previous_value}` para `{actual_value}`'
        running_loop = asyncio.get_running_loop()
        running_loop.create_task(trinity_bot.logger.log(embed, files=[self.get_character_icon()]))

    def get_character_icon(self):
        return File(BytesIO(self.character.data.icon), filename='icon.png')
