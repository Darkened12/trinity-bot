from discord import ButtonStyle, Interaction
from discord.ui import Button

from app.views.modals.character_modal import CharacterModal


class CharacterEditButton(Button):
    def __init__(self):
        super().__init__(label='Edit', style=ButtonStyle.primary, emoji='<:edit:966638166503206933>')

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(CharacterModal(self.view.character, self.view.author))