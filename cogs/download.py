from os import read
from typing import *

import discord, uuid, json, requests, os
import pandas as pd
from discord.ext import commands
from dataclasses import dataclass

from cogs.resolve import get_api
from utils.utilities import read_json, bmessage

ENV: json = read_json("json/env.json")

class Download(commands.Cog):
    """It manages download"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def load(self, ctx: commands.Context, _id: str = None):
        if (not _id): return
        if (not (res := get_api(f"{ENV['api']}/api/asset", _id))):
            return await bmessage(ctx, f"❌ cannot find assets with the id `{_id}`")
        
        tmp: str = str(uuid.uuid1()) + ".png"
        r: object = requests.get(f"{ENV['api']}{res['path']}")

        if (res["type"] == "skin"):
            open(tmp, "wb").write(r.content)
            await ctx.send(file=discord.File(tmp))
            return (os.remove(tmp))

        embed = discord.Embed(color=0x000000, title=res["name"])
        embed.set_image(url=f"{ENV['api']}{res['path']}")
        embed.set_footer(text=f"Uploaded by {res['uploaded_by']['name']}")
        embed.set_thumbnail(url=res["uploaded_by"]["profile_photo_url"])
        await ctx.send(embed=embed)
        
def setup(bot: commands.Bot):
    bot.add_cog(Download(bot))