# await guild.create_role(name="role name")

from typing import *

import discord, json
from discord.ext import commands

from utils.utilities import bmessage, read_json

ROLE: json = read_json("json/role.json")

class Roles(commands.Cog):
    """Manage role add and update"""
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def init(self, ctx: commands.Context):
        roles_names: List[str] = [a.name for a in ctx.guild.roles]
        if (all(x in roles_names for x in ROLE.keys())):
            return await bmessage(ctx, "❌ Roles have already been created")
        for k in ROLE.keys():
            await ctx.guild.create_role(name=k)
        await bmessage(ctx, "✅ Roles have been created")

    @commands.command()
    async def role(self, ctx: commands.Context, token: str = None):
        if (not token): return
        pass

def setup(bot: commands.Bot):
    bot.add_cog(Roles())