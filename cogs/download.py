"""download cog"""

import discord
import requests
import os

from discord.ext import commands

from utils.config import DockerConfig
from cogs.apis.teeskins import TeeskinsAPI
from utils.utilities import basic_message

config = DockerConfig("config.ini")

class Download(commands.Cog):
    """
        It manages download
    """

    @commands.command()
    async def load(self, ctx: commands.Context, _id: str = None):
        """
            Displays an asset
        
            Example:
                `!t load 1337`
        """

        if not _id:
            return

        asset = TeeskinsAPI.asset(_id)

        if not asset:
            return await basic_message(
                ctx,
                f"❌ Cannot find assets with the id `{_id}`"
            )
        
        tmp = asset["name"] + ".png"
        url = TeeskinsAPI.HOST + asset["path"]
        img = requests.get(url)

        if (asset["type"] == "skin"):
            open(tmp, "wb").write(img.content)
            await ctx.send(file=discord.File(tmp))
            return os.remove(tmp)

        embed = discord.Embed(color=0x000000, title=asset["name"])

        embed.set_image(url=url)
        embed.set_footer(text=f"Uploaded by {asset['uploaded_by']['name']} and made by {asset['author']}")
        embed.set_thumbnail(url=asset["uploaded_by"]["profile_photo_url"])

        await ctx.send(embed=embed)
        
    @commands.command()
    async def random(self, ctx: commands.Context, category: str = None):
        """
            Displays a random asset
        
            Allowed categories:
                `skin`
                `mapres`
                `gameskin`
                `emoticon`
                `entity`
                `cursor`
                `particle`
                `font`
                `gridTemplate`
        
            Examples:
                `!t random skin`
                `!t random mapres`
        """

        if not category:
            return
    
        res = TeeskinsAPI.random_asset(category)

        if not res:
            return await basic_message(
                ctx,
                f"❌ category `{category}` doesn't exist"
            )

        await self.load(ctx, str(res["id"]))

def setup(bot: commands.Bot):
    bot.add_cog(Download())
