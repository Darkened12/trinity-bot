from discord import User


from app.controllers.database_controller import Database
from typing import List
from app.ext.tools import split_list, get_initial_and_last_letter_from_list
from app.views.base_view import BaseView
from app.views.selects.cf_selection_menu import CFSelectionMenu


class CFSelectionView(BaseView):
    def __init__(self, character_names: List[str], database: Database, author: User,
                 is_change_allowed: bool = False):
        super().__init__(author=author)
        self.character_names = character_names
        self.database = database
        self.game_id = 1
        self.is_changed_allowed = is_change_allowed

        for list_of_names in split_list(self.character_names, 9):
            self.add_item(CFSelectionMenu(character_names=list_of_names,
                                          initial_letters=get_initial_and_last_letter_from_list(list_of_names),
                                          database=self.database,
                                          author=author))