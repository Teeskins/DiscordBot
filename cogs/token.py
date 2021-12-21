#!/usr/bin/env python3

from typing import *

import discord, asyncio, uuid
from discord.ext import commands

from utils.utilities import bmessage

secure_msg: str = """Secure channel, only you and administrators can see this channel\n \
This channel will be deleted automatically in 60 seconds"""

class Token(commands.Cog):
    """Security to enter your token"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self._id: List[str] = []

    async def delete(self, key: str, _id: int):
        """Delete tmp channel"""
        await asyncio.sleep(60)
        self._id.remove(key)
        await self.bot.get_channel(_id).delete()

    @commands.command()
    async def login(self, ctx: commands.Context):
        """Create tmp channel"""
        await ctx.message.delete()
        key: str = str(ctx.guild.id) + str(ctx.author.id)
        if (key in self._id): return
        overwrites: Dict[object, object] = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages = False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages = True),
            ctx.author: discord.PermissionOverwrite(read_messages = True)
        }
        channel: object = await ctx.guild.create_text_channel(
            str(uuid.uuid1()), overwrites = overwrites)
        await bmessage(channel, secure_msg, "Common usage of this channel: !t role <token>")
        await channel.send(ctx.author.mention)
        await bmessage(ctx, f"🔐 Secret channel {channel.mention}")
        self._id.append(key)
        asyncio.create_task(self.delete(key, channel.id))

def setup(bot: commands.Bot):
    bot.add_cog(Token(bot))