import discord

from discord.ext import commands

from yzlabot.models import Config, SelfRole
from yzlabot.database import YBDatabase, Query
from yzlabot.cogs import (
    CONFIG_SELF_ROLE_CHANNEL_ID,
    CONFIG_ROLE_TABLE
)


class SelfRoleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(
            self, payload: discord.RawReactionActionEvent):
        if payload.member.bot:
            return

        with YBDatabase(payload.guild_id) as db:
            q = Query()
            src_db = db.search(q.config_id == CONFIG_SELF_ROLE_CHANNEL_ID)
            if len(src_db) == 0:
                return
            cfg_src = Config(**src_db[0])
            if str(cfg_src.value) == payload.channel_id:
                return
            db_sr = db.table(CONFIG_ROLE_TABLE)
            # noinspection PyTypeChecker
            react_db = db_sr.search(q.emoji == payload.emoji.name)
            if len(react_db) != 1:
                return

            sr = SelfRole(**react_db[0])
            await payload.member.add_roles(
                payload.member.guild.get_role(sr.role_id)
            )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
            self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        with YBDatabase(payload.guild_id) as db:
            q = Query()
            src_db = db.search(q.config_id == CONFIG_SELF_ROLE_CHANNEL_ID)
            if len(src_db) == 0:
                return
            cfg_src = Config(**src_db[0])
            if str(cfg_src.value) == payload.channel_id:
                return
            db_sr = db.table(CONFIG_ROLE_TABLE)
            # noinspection PyTypeChecker
            react_db = db_sr.search(q.emoji == payload.emoji.name)
            if len(react_db) != 1:
                return

            sr = SelfRole(**react_db[0])
            await member.remove_roles(
                guild.get_role(sr.role_id)
            )
