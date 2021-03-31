import io
from discord import File, Embed
from database.psql.models import Character, Move
from sqlalchemy.sql import select, and_
from exceptions import CharacterNotFound, MoveNotFound


async def execute(db, game_id, ctx, args, lang='en-us'):
    async with ctx.channel.typing():
        character_name = args.split(' ', 1)[0]
        parsed_character_name = parse_character_name(character_name.lower() if ' ' in args else args.lower())

        async with db.session() as session:
            sql = select(Character).where(and_(Character.game_id == game_id)). \
                where(Character.name.ilike(f'%{parsed_character_name}%'))

            query_result = await session.execute(sql)
            character = query_result.scalars().first()

        if character is None:
            if lang == 'pt-br':
                return await ctx.send(f'Personagem "{parsed_character_name}" não encontrado!')
            return await ctx.send(f'Character "{parsed_character_name}" was not found!')

        if ' ' not in args.lower():
            embed = Embed(
                title=character.name,
                description=character.notes.replace('*', '\\*') if character.notes != '-' else None,
                colour=int(character.color, 0)
            )
            if character.health != '-':
                embed.add_field(name='Health', value=character.health)
            if character.jump_startup != '-':
                embed.add_field(name='Jump Startup', value=character.jump_startup)
            if character.combo_rate not in ['-', None]:
                embed.add_field(name='Combo Rate', value=character.combo_rate)
            if character.dash != '-':
                embed.add_field(name='Dash', value=character.dash)

            icon = File(fp=io.BytesIO(character.icon), filename='icon.png')
            embed.set_thumbnail(url="attachment://icon.png")
            return await ctx.send(file=icon, embed=embed)

        elif 'movelist' in args.lower():
            async with db.session() as session:
                sql = select(Move).where(Move.character_id == character.id).order_by(Move.id)
                query_result = await session.execute(sql)
                moves = query_result.scalars()

            embed = Embed(
                title=f'{character.name} - Movelist',
                description='\n'.join([move.move_name for move in moves]),
                colour=int(character.color, 0)
            )
            icon = File(fp=io.BytesIO(character.icon), filename='icon.png')
            embed.set_thumbnail(url="attachment://icon.png")
            return await ctx.send(file=icon, embed=embed)
        else:
            move_arg = args.split(' ', 1)[1]

            async with db.session() as session:
                sql = select(Move).where(and_(Move.character_id == character.id)). \
                    where(Move.move_name.ilike(f'%{move_arg}%')).order_by(Move.id)

                query_result = await session.execute(sql)
                move = query_result.scalars().first()

            if move is None:
                if lang == 'pt-br':
                    return await ctx.send(f'Move "{move_arg}" não encontrado!')
                return await ctx.send(f'Move "{move_arg}" was not found!')

            embed = Embed(
                title=f'{character.name} - {move.move_name}',
                description=move.notes.replace('*', '\\*') if move.notes != '-' else '',
                colour=int(character.color, 0)
            )

            def add_embed_fields(emb, name, value):
                if value not in ['-', None]:
                    if 'P1' not in value:
                        value = value.replace('*', '\\*')
                    emb.add_field(name=name, value=value)

            add_embed_fields(embed, name='Damage', value=move.damage)
            add_embed_fields(embed, name='Startup', value=move.startup)
            add_embed_fields(embed, name='Active', value=move.active)
            add_embed_fields(embed, name='Recovery', value=move.recovery)
            add_embed_fields(embed, name='Frame Advantage', value=move.frame_adv)
            add_embed_fields(embed, name='Guard', value=move.guard)
            add_embed_fields(embed, name='Attribute', value=move.attribute)
            add_embed_fields(embed, name='Invul/GP', value=move.invul)
            add_embed_fields(embed, name='Blockstun', value=move.blockstun)
            add_embed_fields(embed, name='Blockstop', value=move.blockstop)
            add_embed_fields(embed, name='Prorate', value=move.prorate)
            add_embed_fields(embed, name='Cancel', value=move.cancel)

            icon = File(fp=io.BytesIO(character.icon), filename='icon.png')
            sprite = File(fp=io.BytesIO(move.sprite), filename='sprite.png')

            embed.set_thumbnail(url="attachment://icon.png")
            embed.set_image(url="attachment://sprite.png")
            return await ctx.send(files=[icon, sprite], embed=embed)


def parse_character_name(name):
    if name.lower() == 'mu':
        return 'mu-12'
    elif name.lower() == 'nu':
        return 'nu-13'
    return name
