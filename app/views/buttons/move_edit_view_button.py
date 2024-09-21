from ..modals.move_modal import MoveModal
from ..modals.sprite_modal import SpriteModal

from discord import Interaction
from discord.ui import Button


class MoveEditViewButton(Button):
    async def callback(self, interaction: Interaction):
        if self.custom_id not in ['sprite', 'hitbox']:
            await interaction.response.send_modal(MoveModal(
                attr=self.custom_id,
                move=self.view.move,
                character=self.view.character,
                author=self.view.author
            ))
        else:
            await interaction.response.send_modal(SpriteModal(
                attr=self.custom_id,
                move=self.view.move,
                character=self.view.character,
                author=self.view.author
            ))
