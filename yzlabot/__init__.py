import logging
import os

import i18n
import discord
from discord.ext import commands

from .help import YLHelpCommand

intents = discord.Intents.none()
intents.emojis = True
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.messages = True
intents.reactions = True

YB_BOT = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    case_insensitive=True,
    help_command=YLHelpCommand(),
    activity=discord.Game("YZ-LABO BOT SYSTEM"),
    intents=intents
)


def i18n_setup():
    i18n.set('filename_format', '{locale}.{format}')
    i18n.load_path.append(
        os.path.join(os.path.dirname(__file__), "..", "locale"))
    i18n.set("locale",
             os.environ.get("YB_LANG")
             if os.environ.get("YB_LANG") is not None else "jp")
    i18n.set("fallback", "jp")


i18n_setup()


@YB_BOT.event
async def on_ready():
    logging.info(f"Logged in as {YB_BOT.user}")
    app_info = await YB_BOT.application_info()
    logging.info(f"Application ID: {app_info.id}")
    if app_info.bot_public:
        logging.warning(
            "BOT is set to public BOT. "
            "We recommend that you disable this setting.")
    logging.info("YZ-LABOT is getting ready!")


@YB_BOT.command(
    brief=i18n.t("command.add_guild.brief"),
    description=i18n.t("command.add_guild.description")
)
@commands.is_owner()
@commands.dm_only()
async def add_guild(ctx: commands.Context):
    app_info = await YB_BOT.application_info()
    required_permission = discord.Permissions(
        administrator=True
    )
    await ctx.send(discord.utils.oauth_url(
        app_info.id,
        permissions=required_permission))


@YB_BOT.event
async def on_command(ctx: commands.Context):
    logging.info(
        f"{ctx.author.name}#{ctx.author.discriminator} "
        f"has sent command: {ctx.command}")


@YB_BOT.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(i18n.t("error.unknown_command", mention=ctx.message.author.mention))
    elif isinstance(error, commands.CommandInvokeError):
        logging.error(f"[Command error] {str(error)}")

        try:
            await ctx.send(i18n.t("error.invoke_message", mention=ctx.message.author.mention))
        except (discord.Forbidden, discord.HTTPException):
            logging.error("Can't send message. ignore.")

        try:
            app_info = await YB_BOT.application_info()
        except discord.HTTPException:
            logging.error("Can't fetch application info. Don't send error report.")
        else:
            try:
                embed = discord.embeds.Embed(
                    title=i18n.t("error.invoke_dm_title"),
                    description=f"```\n{error}\n```"
                )
                await app_info.owner.send(embed=embed)
            except discord.Forbidden:
                logging.error("Can't send error message because owner's DM is not allowed. ignore.")
            except discord.HTTPException:
                logging.error("Can't send error message. ignore.")


@add_guild.error
async def add_guild__error(ctx: commands.Context, error):
    if isinstance(error, commands.errors.PrivateMessageOnly):
        await ctx.send(i18n.t("error.dm_only", mention=ctx.message.author.mention))
    elif isinstance(error, commands.errors.CheckFailure):
        await ctx.send(i18n.t("error.check_forbidden", mention=ctx.message.author.mention))
