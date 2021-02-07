import logging
from typing import Union, List

import i18n
import discord
from discord.ext import commands
from pydantic import ValidationError

from yzlabot import i18n_setup
from yzlabot.database import YBDatabase, Query
from yzlabot.models import Config, SelfRole

i18n_setup()

# config id constant
CONFIG_WELCOME_CHANNEL_ID = "welcome_channel_id"
CONFIG_GENERAL_ROLE_ID = "general_role_id"
CONFIG_WELCOME_MESSAGE_ID = "welcome_message_id"
CONFIG_MEMBER_NOTIFY_ID = "member_notify_id"
CONFIG_ROLE_TABLE = "self_role"
CONFIG_SELF_ROLE_CHANNEL_ID = "self_role_channel_id"


class ConfigCog(commands.Cog, name=i18n.t("cog.config.name")):
    __doc__ = i18n.t("cog.config.description")

    @commands.group(
        brief=i18n.t("command.config.brief"),
        description=i18n.t("command.config.description")
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                i18n.t("command.config.unknown_subcommand",
                       mention=ctx.message.author.mention,
                       command="!help config"))

    @config.error
    async def config__error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                i18n.t("error.check_forbidden",
                       mention=ctx.message.author.mention))

    # ==============
    # Welcome
    # ==============

    @config.group(
        name="welcome",
        brief=i18n.t("command.config._welcome.brief"),
        description=i18n.t("command.config._welcome.description")
    )
    async def config_welcome(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                i18n.t("command.config.unknown_subcommand",
                       mention=ctx.message.author.mention,
                       command="!help config welcome"))

    @config_welcome.command(
        name="set_channel",
        brief=i18n.t(
            "command.config._welcome._set_channel.brief"),
        descritpion=i18n.t(
            "command.config._welcome._set_channel.description")
    )
    async def config_welcome_set_channel(
            self, ctx: commands.Context, channel: discord.TextChannel):
        with YBDatabase(ctx.guild.id) as db:
            q = Query()
            cfg_model = Config(
                config_id=CONFIG_WELCOME_CHANNEL_ID,
                value=channel.id
            )
            db.upsert(
                cfg_model.dict(),
                q.config_id == CONFIG_WELCOME_CHANNEL_ID
            )
        await ctx.send(
            i18n.t("command.config._welcome._set_channel.success",
                   channel=channel.mention))

    @config_welcome.command(
        name="set_role",
        brief=i18n.t(
            "command.config._welcome._set_role.brief"),
        description=i18n.t(
            "command.config._welcome._set_role.description")
    )
    async def config_welcome_set_role(
            self, ctx: commands.Context, role: discord.Role):
        with YBDatabase(ctx.guild.id) as db:
            q = Query()
            cfg_model = Config(
                config_id=CONFIG_GENERAL_ROLE_ID,
                value=role.id
            )
            db.upsert(
                cfg_model.dict(),
                q.config_id == CONFIG_GENERAL_ROLE_ID
            )
        await ctx.send(
            i18n.t("command.config._welcome._set_role.success",
                   role=role.name)
        )

    @config_welcome.command(
        name="set_notify_channel",
        brief=i18n.t(
            "command.config._welcome._set_notify_channel.brief"),
        description=i18n.t(
            "command.config._welcome._set_notify_channel.description")
    )
    async def config_welcome_set_notify_channel(
            self, ctx: commands.Context, channel: discord.TextChannel):
        with YBDatabase(ctx.guild.id) as db:
            q = Query()
            cfg_model = Config(
                config_id=CONFIG_MEMBER_NOTIFY_ID,
                value=channel.id
            )
            db.upsert(
                cfg_model.dict(),
                q.config_id == CONFIG_MEMBER_NOTIFY_ID
            )
        await ctx.send(
            i18n.t("command.config._welcome._set_notify_channel.success",
                   channel=channel.mention))

    @config_welcome.command(
        name="remove_notify_channel",
        brief=i18n.t(
            "command.config._welcome._remove_notify_channel.brief"),
        description=i18n.t(
            "command.config._welcome._remove_notify_channel.description")
    )
    async def config_welcome_remove_notify_channel(
            self, ctx: discord.TextChannel):
        with YBDatabase(ctx.guild.id) as db:
            q = Query()
            db.remove(q.config_id == CONFIG_MEMBER_NOTIFY_ID)
        await ctx.send(
            i18n.t("command.config._welcome._remove_notify_channel.success"))

    @config_welcome.command(
        name="apply",
        brief=i18n.t(
            "command.config._welcome._apply.brief"),
        descritpion=i18n.t(
            "command.config._welcome._apply.description")
    )
    async def config_welcome_apply(self, ctx: commands.Context):
        with YBDatabase(ctx.guild.id) as db:
            q = Query()
            q_res_wci = db.search(q.config_id == CONFIG_WELCOME_CHANNEL_ID)
            q_res_gri = db.search(q.config_id == CONFIG_GENERAL_ROLE_ID)
            if len(q_res_wci) == 0 or len(q_res_gri) == 0:
                await ctx.send(
                    i18n.t("command.config._welcome._apply.err_no_data",
                           mention=ctx.message.author.mention))
                return
            async with ctx.typing():
                cfg = Config(**q_res_wci[0])
                channel = ctx.guild.get_channel(int(cfg.value))
                if channel is not None:
                    channel_length = len(
                        await channel.history(limit=None).flatten()
                    )
                    await channel.purge(limit=channel_length)
                    msg = await channel.send(i18n.t("text.welcome"))
                    await msg.add_reaction("👍")
                    cfg_model = Config(
                        config_id=CONFIG_WELCOME_MESSAGE_ID,
                        value=msg.id
                    )
                    db.upsert(
                        cfg_model.dict(),
                        q.config_id == CONFIG_WELCOME_MESSAGE_ID
                    )
                else:
                    await ctx.send(
                        i18n.t("command.config._welcome._apply.err_unknown_ch",
                               mention=ctx.message.author.mention))
                    return
        await ctx.send(i18n.t("command.config._welcome._apply.done"))

    # ==============
    # Self role
    # ==============

    @config.group(
        brief=i18n.t("command.config._self_role.brief"),
        description=i18n.t("command.config._self_role.description"),
    )
    async def self_role(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                i18n.t("command.config.unknown_subcommand",
                       mention=ctx.message.author.mention,
                       command="!help config self_role"))

    @self_role.command(
        name="add",
        brief=i18n.t("command.config._self_role._add.brief"),
        description=i18n.t("command.config._self_role._add.description")
    )
    async def self_role_add(
            self,
            ctx: commands.Context,
            emoji: Union[discord.Emoji, discord.PartialEmoji, str],
            role: discord.Role):
        role_perm_dict = dict(iter(role.permissions))
        restrict_perms = dict(iter(discord.Permissions(
            administrator=True,
            ban_members=True,
            deafen_members=True,
            kick_members=True,
            manage_channels=True,
            manage_emojis=True,
            manage_nicknames=True,
            manage_permissions=True,
            manage_roles=True,
            manage_webhooks=True,
            mention_everyone=True,
            move_members=True,
            mute_members=True,
            view_audit_log=True,
            view_guild_insights=True
        )))
        for p in restrict_perms:
            if role_perm_dict[p] and (restrict_perms[p] is True):
                await ctx.send(
                    i18n.t("command.config._self_role._add.err_no_safe_role",
                           mention=ctx.message.author.mention))
                return
        with YBDatabase(ctx.guild.id) as db:
            sr_db = db.table(CONFIG_ROLE_TABLE)
            q = Query()
            try:
                await ctx.message.add_reaction(emoji)
            except (
                    discord.HTTPException,
                    discord.NotFound,
                    discord.InvalidArgument):
                await ctx.send(
                    i18n.t(
                        "command.config._self_role._add.err_unusable_emoji",
                        mention=ctx.message.author.mention)
                )
                return
            role_cfg = SelfRole(
                role_id=role.id,
                emoji=str(emoji)
            )
            # noinspection PyTypeChecker
            sr_db.upsert(role_cfg.dict(),
                         q.role_id == role.id)
        await ctx.send(i18n.t("command.config._self_role._add.success"))

    @self_role.command(
        name="remove",
        brief=i18n.t("command.config._self_role._remove.brief"),
        description=i18n.t("command.config._self_role._remove.description")
    )
    async def self_role_remove(
            self, ctx: commands.Context, role: discord.Role):
        with YBDatabase(ctx.guild.id) as db:
            sr_db = db.table(CONFIG_ROLE_TABLE)
            q = Query()
            # noinspection PyTypeChecker
            sr_db.remove(q.role_id == role.id)
        await ctx.send(i18n.t("command.config._self_role._remove.success"))

    @self_role.command(
        name="set_channel",
        brief=i18n.t(
            "command.config._self_role._set_channel.brief"),
        description=i18n.t(
            "command.config._self_role._set_channel.description")
    )
    async def self_role_set_channel(
            self, ctx: commands.Context, channel: discord.TextChannel):
        with YBDatabase(ctx.guild.id) as db:
            q = Query()
            cfg_src = Config(
                config_id=CONFIG_SELF_ROLE_CHANNEL_ID,
                value=channel.id
            )
            db.upsert(
                cfg_src.dict(),
                q.config_id == CONFIG_SELF_ROLE_CHANNEL_ID
            )
        await ctx.send(
            i18n.t("command.config._self_role._set_channel.success",
                   channel=channel.mention))

    @self_role.command(
        name="apply",
        brief=i18n.t(
            "command.config._self_role._apply.brief"),
        description=i18n.t(
            "command.config._self_role._apply.description")
    )
    async def self_role_apply(self, ctx: commands.Context):
        with YBDatabase(ctx.guild.id) as db:
            async with ctx.typing():
                q = Query()
                src_id = db.search(q.config_id == CONFIG_SELF_ROLE_CHANNEL_ID)
                if len(src_id) == 0:
                    await ctx.send(i18n.t(
                        "command.config._self_role._apply.err_no_channel",
                        mention=ctx.message.author.mention
                    ))
                    return
                cfg_src = Config(**src_id[0])
                target_channel = ctx.guild.get_channel(int(cfg_src.value))
                if target_channel is None:
                    await ctx.send(i18n.t(
                        "command.config._self_role._apply.err_no_channel",
                        mention=ctx.message.author.mention
                    ))
                    return
                channel_length = len(
                    await target_channel.history(limit=None).flatten()
                )
                await target_channel.purge(limit=channel_length)
                sr_db = db.table(CONFIG_ROLE_TABLE)
                sr_obj: List[SelfRole] = []
                if len(sr_db.all()) == 0:
                    await ctx.send(i18n.t(
                        "command.config._self_role._apply.err_no_self_roles",
                        mention=ctx.message.author.mention
                    ))
                    return

                for obj in sr_db.all():
                    try:
                        sr_obj.append(SelfRole(**obj))
                    except ValidationError as e:
                        logging.error(f"Append error. ignore.: {e}")

                separate = 0
                messages: List[str] = [""]
                reactions = [[]]
                for i, role in enumerate(sr_obj):
                    if i != 0 and i % 20 == 0:
                        separate += 1
                        messages.append("")
                        reactions.append([])
                    guild_role = ctx.guild.get_role(role.role_id)
                    if guild_role is not None:
                        messages[separate] += \
                            f"{role.emoji}: {guild_role.name}\n"
                        reactions[separate].append(role.emoji)

                await target_channel.send(i18n.t("text.self_role"))
                for i in range(separate + 1):
                    msg = await target_channel.send(messages[i])
                    for reaction in reactions[i]:
                        await msg.add_reaction(reaction)

        await ctx.send(i18n.t("command.config._self_role._apply.success"))
