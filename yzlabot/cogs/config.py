import i18n
import discord
from discord.ext import commands

from yzlabot import i18n_setup
from yzlabot.database import YBDatabase, Query
from yzlabot.models import Config

i18n_setup()

# config id constant
CONFIG_WELCOME_CHANNEL_ID = "welcome_channel_id"
CONFIG_GENERAL_ROLE_ID = "general_role_id"
CONFIG_WELCOME_MESSAGE_ID = "welcome_message_id"
CONFIG_MEMBER_NOTIFY_ID = "member_notify_id"


class ConfigCog(commands.Cog, name=i18n.t("cog.config.name")):
    __doc__ = i18n.t("cog.config.description")

    @commands.group(
        brief=i18n.t("command.config.brief"),
        description=i18n.t("command.config.description")
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                i18n.t("command.config.unknown_subcommand",
                       mention=ctx.message.author.mention,
                       command="!help config"))

    @config.error
    async def config__error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                i18n.t("error.check_forbidden",
                       mention=ctx.message.author.mention))

    @config.group(
        name="welcome",
        brief=i18n.t("command.config._welcome.brief"),
        description=i18n.t("command.config._welcome.description")
    )
    async def config_welcome(self, ctx):
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
