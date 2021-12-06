from typing import *

import discord, json
from discord.ext import commands

from utils.utilities import bmessage, read_json, get_name
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
        """Give role in function of your upload_count on skins.tw
        Its recommended to run this command in a secure channel.
        You can create one with the command `!t login`"""
        if (not token): return
        await ctx.message.delete()
    
        res: List[dict] = get_api(f"{ENV['api']}/api/discord", token)
        if (not res):
            return await bmessage(ctx, f"❌ Cannot find the user with the token `{token}`")

        for k in list(ROLE.keys())[::-1]:
            if (res["count_uploads"] >= ROLE[k]["value"] and k in get_name(ctx.guild.roles)):

                # Check if ctx.author has already updated his roles
                if (k in get_name(ctx.author.roles)):
                    return await bmessage(ctx, "❌ Your roles are already updated")
    
                # Remove ctx.author roles in role.json
                for role in list(ROLE.keys()):
                    await ctx.message.author.remove_roles(discord.utils.get(ctx.guild.roles, name = role))

                # Apply role to ctx.author
                await bmessage(ctx, f"🔓 You have unlocked the role `{k}`")
                return await ctx.message.author.add_roles(discord.utils.get(ctx.guild.roles, name = k))
        await bmessage(ctx, "❌ You have uploaded 0 assets in the database", "You can upload them to skins.tw")

def setup(bot: commands.Bot):
    bot.add_cog(Roles())