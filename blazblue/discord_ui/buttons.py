from discord import ButtonStyle, Interaction
from discord.ui import Button

import app_files.blazblue.discord_ui.views as views
import app_files.blazblue.discord_ui.modals as modals

from sqlalchemy.sql import select, and_
from database.psql.models import Move as MoveModel


class MoveEditButton(Button):
    def __init__(self):
        super().__init__(label='Edit', style=ButtonStyle.primary, emoji='<:edit:966638166503206933>')

    async def callback(self, interaction: Interaction):
        async with self.view.character.db.session() as session:
            sql = select(MoveModel).where(and_(MoveModel.character_id == self.view.character.data.id)). \
                where(MoveModel.move_name == self.view.current_move)
            query_result = await session.execute(sql)
            move = query_result.first()[0]

        await interaction.response.edit_message(view=views.MoveEditView(
            character=self.view.character,
            author=self.view.author,
            move=move
        ))


class MoveHitboxButton(Button):
    def __init__(self):
        super().__init__(label='Hitbox', custom_id='hitbox', style=ButtonStyle.gray)
        self.is_clicked: bool = False

    async def callback(self, interaction: Interaction):
        await self.on_click()

        embed, icon, sprite = await self.view.character.get_move(
            move_name=self.view.current_move,
            is_changed_allowed=self.view.is_changed_allowed,
            hitbox=self.is_clicked
        )
        await interaction.response.edit_message(view=self.view, embed=embed, files=[icon, sprite])

    def style_update(self):
        self.style = ButtonStyle.primary if self.is_clicked else ButtonStyle.gray

    async def on_click(self):
        self.is_clicked = not self.is_clicked
        self.style_update()

    async def on_move_change(self):
        return  # currently disabled
        self.is_clicked = False
        self.style_update()
        has_hitbox = await self.view.has_hitbox()
        self.disabled = not has_hitbox


class MoveEditViewButton(Button):
    async def callback(self, interaction: Interaction):
        if self.custom_id not in ['sprite', 'hitbox']:
            await interaction.response.send_modal(modals.MoveModal(
                attr=self.custom_id,
                move=self.view.move,
                character=self.view.character,
                author=self.view.author
            ))
        else:
            await interaction.response.send_modal(modals.SpriteModal(
                attr=self.custom_id,
                move=self.view.move,
                character=self.view.character,
                author=self.view.author
            ))


class CharacterEditButton(Button):
    def __init__(self):
        super().__init__(label='Edit', style=ButtonStyle.primary, emoji='<:edit:966638166503206933>')

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(modals.CharacterModal(self.view.character, self.view.author))
