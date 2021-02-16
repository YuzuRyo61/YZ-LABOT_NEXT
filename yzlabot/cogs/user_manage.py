import asyncio
from typing import Union, Optional

import discord
import i18n
from discord.ext import commands

from yzlabot import i18n_setup

i18n_setup()

CONFIRM_REACTION = "☑"


def user_embed(
        target: Union[
            discord.User,
            discord.Member
        ]) -> discord.Embed:
    embed = discord.Embed(
        title=i18n.t("cog.user_manage.embed.title"),
        description=i18n.t("cog.user_manage.embed.description",
                           user=str(target)),
        color=discord.Colour.blue()
    )
    embed.set_author(
        name=str(target),
        url=f"https://discord.com/users/{target.id}",
        icon_url=str(target.avatar_url)
    )
    embed.add_field(
        name=i18n.t("cog.user_manage.embed.user_id"),
        value=str(target.id),
        inline=True
    )
    embed.add_field(
        name=i18n.t("cog.user_manage.embed.name"),
        value=str(target.name),
        inline=True
    )
    embed.add_field(
        name=i18n.t("cog.user_manage.embed.discriminator"),
        value=str(target.discriminator),
        inline=True
    )
    embed.add_field(
        name=i18n.t("cog.user_manage.embed.registered"),
        value=target.created_at.strftime("%Y/%m/%d %H:%M:%S %A"),
        inline=True
    )
    embed.add_field(
        name=i18n.t("cog.user_manage.embed.bot"),
        value="✅" if target.bot else "❎",
        inline=True
    )
    if isinstance(target, discord.Member):
        embed.add_field(
            name=i18n.t("cog.user_manage.embed.joined_at"),
            value=target.joined_at.strftime("%Y/%m/%d %H:%M:%S %A"),
            inline=True
        )
        if target.nick is not None:
            embed.add_field(
                name=i18n.t("cog.user_manage.embed.nickname"),
                value=target.nick
            )
    return embed


class UserManageCog(commands.Cog, name=i18n.t("cog.user_manage.name")):
    __doc__ = i18n.t("cog.user_manage.description")

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
                        i18n.t("error.unknown_user",
                               mention=ctx.message.author.mention)
                    )
                    return

            embed = user_embed(target)

            await ctx.send(embed=embed)

    @commands.command(
        brief=i18n.t("command.ban.brief"),
        description=i18n.t("command.ban.description")
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(
            self,
            ctx: commands.Context,
            target: Union[
                discord.User,
                discord.Member,
                int
            ],
            *,
            reason: Optional[str] = None):
        async with ctx.typing():
            if isinstance(target, int):
                try:
                    target = await self.bot.fetch_user(target)
                except discord.NotFound:
                    await ctx.send(
                        i18n.t("error.unknown_user",
                               mention=ctx.message.author.mention)
                    )
                    return

        embed = user_embed(target)
        confirm_message = await ctx.send(
            i18n.t("command.ban.confirm_message",
                   mention=ctx.message.author.mention,
                   confirm_reaction=CONFIRM_REACTION),
            embed=embed
        )
        await confirm_message.add_reaction(CONFIRM_REACTION)

        def confirm_check(reaction, user):
            is_same = reaction.message.channel == confirm_message.channel and\
                    reaction.message.id == confirm_message.id
            return user == ctx.message.author and \
                str(reaction.emoji) == CONFIRM_REACTION and is_same

        try:
            await self.bot.wait_for(
                "reaction_add",
                timeout=10.0,
                check=confirm_check
            )
        except asyncio.TimeoutError:
            await ctx.send(
                i18n.t("command.ban.cancelled")
            )
        else:
            await ctx.guild.ban(
                target,
                reason=reason
            )
            await ctx.send(
                i18n.t("command.ban.banned"),
                embed=embed
            )
        finally:
            await confirm_message.delete()
