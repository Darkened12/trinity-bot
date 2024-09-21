from typing import List

from discord import ButtonStyle, User, Interaction
from discord.ui import Button, button
from .base_view import BaseView, character_selection_embed

from app.controllers.database_controller import Database
from .cf_selection_view import CFSelectionView
from .tag_selection_view import TagSelectionView


class GameSelectionView(BaseView):
    def __init__(self, database: Database, cf_character_names: List[str], tag_character_names: List[str],
                 author: User, is_changed_allowed: bool = False):
        super().__init__(author)
        self.db = database
        self.cf_names = cf_character_names
        self.tag_names = tag_character_names
        self.is_changed_allowed = is_changed_allowed

    @button(label='BlazBlue Centralfiction', style=ButtonStyle.green, emoji='<:cf_icon:966052275686608936>', row=0)
    async def on_cf_selection(self, btn: Button, interaction: Interaction):
        return await interaction.response.edit_message(view=CFSelectionView(
            character_names=self.cf_names,
            database=self.db,
            author=self.author,
            is_change_allowed=self.is_changed_allowed
        ), embed=character_selection_embed)

    @button(label='BlazBlue Cross Tag Battle', style=ButtonStyle.primary, emoji='<:tag_icon:966052796753379358>', row=0)
    async def on_tag_selection(self, btn: Button, interaction: Interaction):
        view = await TagSelectionView(
            database=self.db,
            author=self.author,
            is_change_allowed=self.is_changed_allowed
        )
        await interaction.response.edit_message(view=view, embed=character_selection_embed)