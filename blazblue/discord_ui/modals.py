import asyncio
import trinity_bot
from io import BytesIO

from discord import Embed, File, User, Interaction, InputTextStyle
from discord.ui import Modal, InputText

import app_files.blazblue.discord_ui.views as views

from sqlalchemy.sql import select, update
from database.psql.models import Move as MoveModel, Character as CharacterModel
from app_files.blazblue.character import Character
from conn.connection import get_request


class FrameDataUpdate:
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


class CharacterModal(Modal):
    def __init__(self, character: Character, author: User):
        super().__init__(title=f'{character.data.name} - Stats')
        self.author = author
        self.character = character

        self.add_item(InputText(style=InputTextStyle.short, custom_id='health', label='Health',
                                placeholder=character.data.health, min_length=4, max_length=5, value='',
                                required=False))
        self.add_item(InputText(style=InputTextStyle.short, custom_id='jump_startup', label='Jump Startup',
                                placeholder=character.data.jump_startup, min_length=1, max_length=2, value='',
                                required=False))
        if self.character.game_id == 1:
            self.add_item(InputText(style=InputTextStyle.short, custom_id='combo_rate', label='Combo Rate',
                                    placeholder=character.data.combo_rate, min_length=3, max_length=3, value='',
                                    required=False))
        self.add_item(InputText(style=InputTextStyle.paragraph, custom_id='dash', label='Dash',
                                placeholder=character.data.dash, min_length=0, max_length=100, value='',
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
                                                       view=views.CharacterView(new_character_obj, self.author,
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


class MoveModal(Modal, FrameDataUpdate):
    def __init__(self, attr: str, move: MoveModel, character: Character, author: User):
        FrameDataUpdate.__init__(self, move=move, character=character, author=author)
        Modal.__init__(self, title=attr, custom_id=attr)
        self.attr = attr
        self.add_move_input_text()
        self.add_notes_input_text()

    def add_move_input_text(self):
        self.add_item(InputText(style=InputTextStyle.paragraph, label=self.attr.title().replace('_', ''),
                                placeholder=self.move[self.attr], min_length=0, max_length=50, value='',
                                required=True))

    def add_notes_input_text(self):
        self.add_item(InputText(style=InputTextStyle.short, custom_id='change_note', label='Change Reason',
                                placeholder='Not obligatory', min_length=0, max_length=100, value='',
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
        view = views.MoveEditView(self.character, interaction.user, self.move)
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
