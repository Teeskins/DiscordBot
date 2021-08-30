# await guild.create_role(name="role name")

from typing import *

import discord, json
from discord.ext import commands

from utils.utilities import bmessage, read_json
from cogs.resolve import get_api

ROLE: json = read_json("json/role.json")
ENV: json = read_json("json/env.json")

class Roles(commands.Cog):
    """Manage role add and update"""

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def init(self, ctx: commands.Context):
        """Creates role if needed"""
        roles_names: List[str] = [a.name for a in ctx.guild.roles]
        if (all(x in roles_names for x in ROLE.keys())):
            return await bmessage(ctx, "❌ Roles have already been created")
        for k in ROLE.keys():
            await ctx.guild.create_role(name=k)
        await bmessage(ctx, "✅ Roles have been created")

    @commands.command()
    async def role(self, ctx: commands.Context, token: str = None):
        """Give role in function of upload_count"""
        if (not token): return
        await ctx.message.delete()
        res: List[dict] = get_api(f"{ENV['api']}/api/discord", token)
        if (not res):
            return await bmessage(ctx, f"❌ cannot find the user with the token `{token}`")
        for k in list(ROLE.keys())[::-1]:
            if (res["count_uploads"] >= ROLE[k]["value"] and k in [x.name for x in ctx.guild.roles]):
                return await ctx.message.author.add_roles(discord.utils.get(ctx.guild.roles, name = k))

def setup(bot: commands.Bot):
    bot.add_cog(Roles())