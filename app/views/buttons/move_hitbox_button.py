from discord import ButtonStyle, Interaction
from discord.ui import Button


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
