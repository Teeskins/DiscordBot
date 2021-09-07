from typing import *

import json
from discord.ext import commands

from utils.utilities import read_json

REACTION: json = read_json("json/reaction.json")

class Moderator(commands.Cog):
    """Commands for the moderators"""

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def clear(self, ctx: commands.Context, n: int = 1):
        """Removes n message"""
        await ctx.message.delete()
        await ctx.send(f"[{REACTION['loading']}]")
        await ctx.channel.purge(limit = n + 1)

def setup(bot: commands.Bot):
    bot.add_cog(Moderator(bot))