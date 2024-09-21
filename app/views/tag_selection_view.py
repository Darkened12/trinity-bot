import sqlalchemy
import collections
from sqlalchemy.sql import select

from discord import User

from app.controllers.database_controller import Database
from app.models.character_model import Character as CharacterModel
from typing import List

from app.views.base_view import BaseView
from app.views.selects.tag_selection_menu import TagSelectionMenu


class TagSelectionView(BaseView):
    def __init__(self, author: User, database: Database, is_change_allowed: bool = False):
        super().__init__(author=author, is_change_allowed=is_change_allowed)
        self.db = database

    def __await__(self):
        return self.init().__await__()

    @staticmethod
    def parse_query_result(query_result: sqlalchemy.engine.ScalarResult) -> dict:
        parsed_result = {}
        for game_prefix, character_name in query_result.all():
            if game_prefix in ['AB', 'AH', 'SK']:
                game_prefix = 'Other games'
            if game_prefix not in parsed_result.keys():
                parsed_result.update({game_prefix: []})
            parsed_result[game_prefix].append(character_name)
        return parsed_result

    async def init(self) -> object:
        async with self.db.session() as session:
            c = CharacterModel
            sql = select(c.game_prefix, c.name).where(c.game_id == 2).order_by(c.game_prefix, c.name)
            query_result = await session.execute(sql)

        parsed_result = self.parse_query_result(query_result)
        menus: List[TagSelectionMenu] = []
        for game_prefix, characters in zip(parsed_result.keys(), parsed_result.values()):
            menus.append(TagSelectionMenu(
                placeholder=game_prefix.upper(),
                characters=characters,
                database=self.db,
                author=self.author
            ))
        menus_deque = collections.deque(menus)
        menus_deque.rotate(-1)
        for item in list(menus_deque):
            self.add_item(item)
        return self
