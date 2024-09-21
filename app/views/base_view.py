from discord import Embed,  User, Interaction
from discord.ui import View, Item


class AuthenticationError(Exception):
    pass


class BaseView(View):
    """Implements user authentication"""

    def __init__(self, author: User, is_change_allowed: bool = False):
        super().__init__()
        self.author: User = author
        self.is_changed_allowed = is_change_allowed

    async def interaction_check(self, interaction: Interaction) -> bool:
        if not interaction.user == self.author:
            raise AuthenticationError
        return True

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        if type(error) is AuthenticationError:
            error_message = "You cannot interact with other user's command!"
            return await interaction.response.send_message(
                error_message,
                ephemeral=True)
        raise error


character_selection_embed = Embed(
    description='Select your character below...',
    color=0xfedbb6
)
