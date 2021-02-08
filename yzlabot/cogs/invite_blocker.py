import i18n
import re

import discord
from discord.ext import commands

from yzlabot import i18n_setup

i18n_setup()


class InviteBlockerCog(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        if message.author.guild_permissions.administrator:
            return

        if re.search(
            (
                r"(https?://)?"
                r"(discord\.gg/|"
                r"discord\.com/invite/|"
                r"discordapp\.com/invite/|"
                r"(.+)\.discord\.com/invite/|"
                r"(.+)\.discordapp\.com/invite/)"
                r"[a-zA-Z0-9_]+"
            ),
            message.content
        ):
            await message.delete()
            embed = discord.Embed(
                title=i18n.t("cog.invite_blocker.blocked.title"),
                description=i18n.t("cog.invite_blocker.blocked.description"),
                color=discord.Colour.red()
            )
            await message.channel.send(
                message.author.mention,
                embed=embed
            )
