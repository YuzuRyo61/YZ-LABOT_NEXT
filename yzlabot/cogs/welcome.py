import datetime
import logging

import i18n
import discord
from discord.ext import commands

from yzlabot import i18n_setup
from yzlabot.database import YBDatabase, Query
from yzlabot.cogs import (
    CONFIG_WELCOME_MESSAGE_ID,
    CONFIG_GENERAL_ROLE_ID,
    CONFIG_MEMBER_NOTIFY_ID
)
from yzlabot.models import Config

i18n_setup()


class WelcomeCog(commands.Cog):
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member.bot:
            return

        with YBDatabase(payload.guild_id) as db:
            q = Query()
            msg_id = db.search(q.config_id == CONFIG_WELCOME_MESSAGE_ID)
            gr_id = db.search(q.config_id == CONFIG_GENERAL_ROLE_ID)
            mn_id = db.search(q.config_id == CONFIG_MEMBER_NOTIFY_ID)
            if len(msg_id) == 0 or len(gr_id) == 0:
                logging.warning("Welcome message or general role is not configured.")
                return
            cfg_msg = Config(**msg_id[0])
            cfg_gr = Config(**gr_id[0])
            cfg_mn = Config(**mn_id[0]) if len(mn_id) > 0 else None

        if payload.message_id != int(cfg_msg.value):
            return

        if payload.emoji.name == "👍":
            normal_role = payload.member.guild.get_role(int(cfg_gr.value))
            if normal_role not in payload.member.roles:
                await payload.member.add_roles(
                    normal_role,
                    reason=i18n.t("cog.welcome.audit.agreed")
                )
                if payload.member.joined_at is not None and \
                        datetime.datetime.utcnow() <= \
                        payload.member.joined_at + datetime.timedelta(days=1):
                    if cfg_mn is not None:
                        notify_channel = \
                            payload.member.guild.get_channel(
                                int(cfg_mn.value))
                        await notify_channel.send(
                            i18n.t("cog.welcome.joined",
                                   user=payload.member.mention)
                        )
                    try:
                        await payload.member.send(
                            i18n.t("text.welcome_dm"))
                    except discord.Forbidden:
                        pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        # Ignore bot account
        if member.bot:
            return

        with YBDatabase(member.guild.id) as db:
            q = Query()
            gr_id = db.search(q.config_id == CONFIG_GENERAL_ROLE_ID)
            nc_id = db.search(q.config_id == CONFIG_MEMBER_NOTIFY_ID)
            if len(gr_id) == 0:
                logging.warning("General role is not configured.")
                return
            cfg_gr = Config(**gr_id[0])
            cfg_nc = Config(**nc_id[0]) if len(nc_id) > 0 else None

        # if left user is assigned general role
        if member.guild.get_role(int(cfg_gr.value)) in member.roles:
            if cfg_nc is not None:
                notify_channel = member.guild.get_channel(int(cfg_nc.value))
                if notify_channel is not None:
                    await notify_channel.send(i18n.t(
                        "cog.welcome.left",
                        user=member.mention
                    ))
                else:
                    logging.error("Notify channel is not found.")
