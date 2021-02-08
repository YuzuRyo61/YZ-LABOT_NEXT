from typing import List

import i18n
import discord
from discord.ext import commands

from yzlabot import i18n_setup
from yzlabot.database import YBDatabase
from yzlabot.models import VoiceRoom
from yzlabot.cogs import CONFIG_VOICE_ROOM_TABLE

i18n_setup()


class VoiceRoomCog(commands.Cog):
    @commands.Cog.listener()
    async def on_voice_state_update(
            self,
            member: discord.Member,
            before: discord.VoiceState,
            after: discord.VoiceState):
        # Ignore same channel state
        if before.channel is after.channel:
            return

        with YBDatabase(member.guild.id) as db:
            vrt = db.table(CONFIG_VOICE_ROOM_TABLE)
            vr_list: List[VoiceRoom] = []
            for vrr in vrt.all():
                vr_list.append(VoiceRoom(**vrr))

        # purge message in channel if no members (other than bot)
        # in voice channel
        if before.channel is not None and after.channel is None:
            before_normal_members = 0
            for voice_member in before.channel.members:
                if not voice_member.bot:
                    before_normal_members += 1

            if before_normal_members == 0:
                # kick all bot members from voice channel
                for before_member in before.channel.members:
                    if before_member.bot:
                        await before_member.move_to(
                            None,
                            reason=i18n.t("cog.voice_room.dc_bot")
                        )

            for cfg in vr_list:
                if before.channel.id == cfg.voice_channel_id:
                    if cfg.text_channel_id is None:
                        continue
                    channel = member.guild.get_channel(cfg.text_channel_id)
                    if channel is not None:
                        channel_length = len(
                            await channel.history(limit=None).flatten())
                        await channel.purge(limit=channel_length)
                    break

        # Ignore bot
        if member.bot:
            return

        # remove before channel
        for role in member.roles:
            for cfg in vr_list:
                if role.id == cfg.assign_role_id:
                    await member.remove_roles(
                        member.guild.get_role(cfg.assign_role_id),
                        reason=i18n.t("cog.voice_room.audit.dc_or_changed")
                    )
                    break

        # assign role
        if not member.bot and after.channel is not None:
            for cfg in vr_list:
                if after.channel.id == cfg.voice_channel_id:
                    await member.add_roles(
                        member.guild.get_role(cfg.assign_role_id),
                        reason=i18n.t("cog.voice_room.audit.con_or_changed")
                    )
                    break
