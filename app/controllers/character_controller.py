import io
from app.controllers.database_controller import Database

from app.models.character_model import Character as CharacterModel
from app.models.move_model import Move
from app.models.gatling_model import Gatling

from discord import Embed, File
from sqlalchemy import select, and_
from app.ext.tools import string_match, StringNotFoundError
from typing import Tuple, List, Dict, Optional


async def get_all_characters_names(database: Database, game_id: int) -> List[str]:
    async with database.session() as session:
        sql = select(CharacterModel.name).where(CharacterModel.game_id == game_id)
        query_result = await session.execute(sql)
        names = query_result.scalars()
    return sorted([i for i in names])


async def get_all_move_names(database: Database, game_id: int) -> Dict[str, List]:
    async with database.session() as session:
        sql = select(Move.move_name, CharacterModel.name).join(CharacterModel, CharacterModel.id == Move.character_id) \
            .where(CharacterModel.game_id == game_id)
        query_result = await session.execute(sql)
        data = query_result.all()

        result_dict = {}
        for tuple_ in data:
            if tuple_[1] not in result_dict.keys():
                result_dict.update({tuple_[1]: ['Gatlings']})
            result_dict[tuple_[1]].append(tuple_[0])
        return result_dict


class CharacterNotFoundError(Exception):
    pass


class MoveNotFoundError(Exception):
    pass


class Character:
    move_types = [
        'distortion skills',
        'distortion drives',
        'normals',
        'drives',
        'specials',
        'universal mechanics',
        'extra skills',
        'partner skills',
        'skills',
        'astral heat',
        'orphans'
    ]

    def __init__(self, database: Database, name: str, game_id: int, is_changed_allowed: bool = False):
        self.db: Database = database
        self.game_id: int = game_id
        self.is_changed_allowed = is_changed_allowed

        self._name: str = self.parse_character_name(name)
        self.data: (CharacterModel, None) = None
        self._general_info: Optional[Tuple[Embed, File]] = None
        self._move_names: Optional[List[str]] = None
        self._move_names_with_types: Optional[List[str]] = None
        self.move_names_with_types_to_dict: Optional[Dict] = None

    @staticmethod
    def parse_character_name(name):
        if name.lower() == 'mu':
            return 'mu-12'
        elif name.lower() == 'nu':
            return 'nu-13'
        elif name.lower() == 'yu':
            return 'yu narukami'
        elif 'platwoobi' in name.lower():
            return 'platinum'
        return name

    @staticmethod
    def add_fields(embed, field_name, field_value):
        """Preventing repetition"""
        if field_value not in ['-', None]:
            embed.add_field(name=field_name, value=field_value)

    @staticmethod
    def discord_bold_formatter(string):
        return string.replace('*', '\\*').replace('\\*\\*', '**')

    @classmethod
    def add_embed_fields(cls, emb, name, value):
        if value not in ['-', None]:
            if 'P1' in value and '-' in value:
                return
            emb.add_field(name=name, value=cls.discord_bold_formatter(value))

    async def query(self):
        names = await get_all_characters_names(self.db, self.game_id)

        async with self.db.session() as session:
            try:
                parsed_character_name = await string_match(self._name, names)
            except StringNotFoundError:
                raise CharacterNotFoundError

            sql = select(CharacterModel).where(and_(CharacterModel.game_id == self.game_id)). \
                where(CharacterModel.name == parsed_character_name).order_by(CharacterModel.name)

            query_result = await session.execute(sql)
        character = query_result.scalars().first()
        self.data = character
        await self._get_move_names()
        self.move_names_with_types_to_dict = await self._moves_with_types_to_dict()

    async def _get_move_names(self):
        async with self.db.session() as session:
            sql = select(Move.type, Move.move_name).where(Move.character_id == self.data.id).order_by(Move.id)
            query_result = await session.execute(sql)
            moves = query_result.all()

        has_gatlings = await self.has_gatlings()

        self._move_names = []
        self._move_names_with_types = []
        if has_gatlings:
            self._move_names.append('Gatlings')

        for tuple_ in moves:
            self._move_names_with_types.append(f'({tuple_[0]}) {tuple_[1]}')
            self._move_names.append(tuple_[1])

    async def get_move(self, move_name: str, is_changed_allowed: bool = False, hitbox: bool = False) -> Tuple[
        Embed, File, File]:
        for move in self.moves:
            if move_name.lower() in move.lower():
                if move == 'Gatlings':
                    return await self.get_gatlings()

                async with self.db.session() as session:
                    sql = select(Move).where(and_(Move.move_name == move)) \
                        .where(Move.character_id == self.data.id).order_by(Move.id)
                    query_result = await session.execute(sql)
                    move = query_result.scalars().first()

                embed = Embed(
                    title=f'{self.data.name} - {move.move_name}',
                    description=self.discord_bold_formatter(move.notes) if move.notes != '-' else '',
                    colour=int(self.data.color, 0)
                )

                if is_changed_allowed:
                    self.add_embed_fields(embed, name='Type', value=move.type)
                self.add_embed_fields(embed, name='Damage', value=move.damage)
                self.add_embed_fields(embed, name='Startup', value=move.startup)
                self.add_embed_fields(embed, name='Active', value=move.active)
                self.add_embed_fields(embed, name='Recovery', value=move.recovery)
                self.add_embed_fields(embed, name='Frame Advantage', value=move.frame_adv)
                self.add_embed_fields(embed, name='Guard', value=move.guard)
                self.add_embed_fields(embed, name='Attribute', value=move.attribute)
                self.add_embed_fields(embed, name='Invul/GP', value=move.invul)
                self.add_embed_fields(embed, name='Blockstun', value=move.blockstun)
                self.add_embed_fields(embed, name='Blockstop', value=move.blockstop)
                self.add_embed_fields(embed, name='Prorate', value=move.prorate)
                self.add_embed_fields(embed, name='Cancel', value=move.cancel)

                icon = File(fp=io.BytesIO(self.data.icon), filename='icon.png')
                sprite = File(fp=io.BytesIO(move.sprite if not hitbox else move.hitbox), filename='sprite.png')

                embed.set_thumbnail(url="attachment://icon.png")
                embed.set_image(url="attachment://sprite.png")
                return embed, icon, sprite
        raise MoveNotFoundError(f'Move "{move_name}" was not found!')

    async def get_gatlings(self) -> Tuple[Embed, File, File]:
        async with self.db.session() as session:
            sql = select(Gatling).where(Gatling.character_id == self.data.id)

            result = await session.execute(sql)
            gatling = result.scalars().first()

        embed = Embed(
            title=f'{self.data.name} - Gatlings',
            description=gatling.notes,
            colour=int(self.data.color, 0)
        )
        icon = File(fp=io.BytesIO(self.data.icon), filename='icon.png')
        sprite = File(fp=io.BytesIO(gatling.image), filename='gatlings.png')
        embed.set_thumbnail(url="attachment://icon.png")
        embed.set_image(url="attachment://gatlings.png")
        return embed, icon, sprite

    async def has_gatlings(self) -> bool:
        async with self.db.session() as session:
            sql = select(Gatling.notes).where(Gatling.character_id == self.data.id)
            query = await session.execute(sql)
            return query.first() != ('',)

    @classmethod
    def move_type_parsing(cls, move_name: str) -> str:
        for type_ in cls.move_types:
            if type_ in move_name:
                return move_name.replace(f'({type_}) ', '')
        return move_name

    @property
    def general_info(self) -> (Embed, File):
        if not self._general_info:
            embed = Embed(
                title=self.data.name,
                description=self.data.notes.replace('*', '\\*') if self.data.notes not in ['-', None] else None,
                colour=int(self.data.color, 0)
            )

            self.add_fields(embed=embed, field_name='Health', field_value=self.data.health)
            self.add_fields(embed=embed, field_name='Jump Startup', field_value=self.data.jump_startup)
            self.add_fields(embed=embed, field_name='Combo Rate', field_value=self.data.combo_rate)
            self.add_fields(embed=embed, field_name='Dash', field_value=self.data.dash)
            self.add_fields(embed=embed, field_name='Unique Movement', field_value=self.data.unique_movement)

            icon = File(fp=io.BytesIO(self.data.icon), filename='icon.png')
            embed.set_thumbnail(url="attachment://icon.png")
            self._general_info = embed, icon
        elif self._general_info[-1].fp.closed:
            self._general_info[-1].fp = io.BytesIO(self.data.icon)  # re-opening file in memory
        return self._general_info

    @property
    def moves(self) -> List[str]:
        return self._move_names

    @property
    def moves_with_types(self) -> List[str]:
        return self._move_names_with_types

    async def _moves_with_types_to_dict(self) -> dict:
        async with self.db.session() as session:
            sql = select(Move.type, Move.move_name).where(Move.character_id == self.data.id). \
                order_by(Move.id)
            query_result = await session.execute(sql)

            result = {}
            for type_, move_name in query_result.all():
                if type_ not in result.keys():
                    result.update({type_: []})
                result[type_].append(move_name)
        return result

    @property
    def movelist(self):
        return [move for move in self.moves]
