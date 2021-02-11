from typing import Union

import discord
import i18n
from discord.ext import commands

from yzlabot import i18n_setup

i18n_setup()


class UserInfoCog(commands.Cog, name=i18n.t("cog.config.userinfo")):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief=i18n.t("command.user_info.brief"),
        description=i18n.t("command.user_info.description")
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def user_info(
            self,
            ctx: commands.Context,
            target: Union[
                discord.Member,
                discord.User,
                int
            ]):
        async with ctx.typing():
            if isinstance(target, int):
                try:
                    target = await self.bot.fetch_user(target)
                except discord.NotFound:
                    await ctx.send(
                        i18n.t("command.user_info.err_unknown_user",
                               mention=ctx.message.author.mention)
                    )
                    return

            embed = discord.Embed(
                title=i18n.t("command.user_info.embed.title"),
                description=i18n.t("command.user_info.embed.description",
                                   user=str(target)),
                color=discord.Colour.blue()
            )
            embed.set_author(
                name=str(target),
                url=f"https://discord.com/users/{target.id}",
                icon_url=str(target.avatar_url)
            )
            embed.add_field(
                name=i18n.t("command.user_info.embed.user_id"),
                value=str(target.id),
                inline=True
            )
            embed.add_field(
                name=i18n.t("command.user_info.embed.name"),
                value=str(target.name),
                inline=True
            )
            embed.add_field(
                name=i18n.t("command.user_info.embed.discriminator"),
                value=str(target.discriminator),
                inline=True
            )
            embed.add_field(
                name=i18n.t("command.user_info.embed.registered"),
                value=target.created_at.strftime("%Y/%m/%d %H:%M:%S %A"),
                inline=True
            )
            embed.add_field(
                name=i18n.t("command.user_info.embed.bot"),
                value="✅" if target.bot else "❎",
                inline=True
            )
            if isinstance(target, discord.Member):
                embed.add_field(
                    name=i18n.t("command.user_info.embed.joined_at"),
                    value=target.joined_at.strftime("%Y/%m/%d %H:%M:%S %A"),
                    inline=True
                )
                if target.nick is not None:
                    embed.add_field(
                        name=i18n.t("command.user_info.embed.nickname"),
                        value=target.nick
                    )
            await ctx.send(embed=embed)
