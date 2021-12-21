#!/usr/bin/env python3

from typing import *

import discord, requests, os, random
from discord.ext import commands
from configparser import ConfigParser

from cogs.resolve import get_api
from utils.utilities import bmessage

config: ConfigParser = ConfigParser()
config.read("config.ini")

class Download(commands.Cog):
    """It manages download"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def load(self, ctx: commands.Context, _id: str = None):
        """Displays an asset
        
        example:
                    `!t load 1337`"""
        if (not _id): return
        res: List[dict] = get_api(f"{config.get('API', 'HOST')}/api/asset", _id)
        if (not res):
            return await bmessage(ctx, f"❌ Cannot find assets with the id `{_id}`")
        
        tmp: str = res["name"] + ".png"
        r: object = requests.get(f"{config.get('API', 'HOST')}{res['path']}")

        if (res["type"] == "skin"):
            open(tmp, "wb").write(r.content)
            await ctx.send(file=discord.File(tmp))
            return (os.remove(tmp))

        embed = discord.Embed(color=0x000000, title=res["name"])
        embed.set_image(url=f"{config.get('API', 'HOST')}{res['path']}")
        embed.set_footer(text=f"Uploaded by {res['uploaded_by']['name']} and made by {res['author']}")
        embed.set_thumbnail(url=res["uploaded_by"]["profile_photo_url"])
        await ctx.send(embed=embed)
        
    @commands.command()
    async def random(self, ctx: commands.Context, category: str = None):
        """Displays a random asset
        
        Allowed categories: `skin` | `mapres` | `gameskin` | `emoticon` | `entity` | `cursor` | `particle` | `font` | `gridTemplate`
        
        example:
                    `!t random skin`
                    `!t random mapres`"""
        if (not category): return
        res: List[dict] = get_api(f"{config.get('API', 'HOST')}/api/assets/{category}", 0)
        if (not res):
            return await bmessage(ctx, f"❌ category `{category}` doesn't exist")
        await self.load(ctx, random.choice(res)["id"])

def setup(bot: commands.Bot):
    bot.add_cog(Download(bot))