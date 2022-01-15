#!/usr/bin/env python3

from turtle import color, title
from typing import *

import discord, json, uuid, os
from discord.ext import commands
from configparser import ConfigParser

from utils.utilities import bmessage, read_json
from cogs.api import Api
from cogs.resolve import get_api

ROLE: json = read_json("data/json/role.json")
config: ConfigParser = ConfigParser()
config.read("config.ini")

class Renderer(commands.Cog, Api):
    """Manage role add and update"""


    def __init__(self):
        Api().__init__()
        
    def _url_to_name(self, url: str) -> str:
        name = url.split("/")[-1]
        name = name.split(".")[0]
        return (name)

    def _is_attachs_valid(self, attachs: List[discord.Attachment]) -> Any:
        if (len(attachs) != 1):
            return (False)
        attach = attachs[0]
        if (not ".png" in attach.filename):
            return (False)
        return (True)

    def _save_tmp_img(self, content: Any) -> str:
        filename = str(uuid.uuid1()) + ".png"
        with open(filename, "wb") as f:
            f.write(content)
        return (filename)

    async def _send_img(self, message: discord.Message, name: str, filename: str):
        embed = discord.Embed(title=name, color=0x000000)

        file = discord.File(filename, filename=filename)
        embed.set_image(url=f'attachment://{filename}')
        await message.channel.send(embed=embed, file=file)
        os.remove(filename)

    async def _send_render(self, message: discord.message, url: str, name: str=None):
        res = self.render({"skin": url})

        if (res.status_code != 200):
            await bmessage(message.channel, "❌ invalid skin")
        else :
            name = name or self._url_to_name(url)
            filename = self._save_tmp_img(res.content)
            await self._send_img(message, name, filename)
    
    async def _upload_manager(self, message: discord.Message):
        attachs = message.attachments
        if (self._is_attachs_valid(attachs) == False):
            return

        url = attachs[0].url

        await self._send_render(message, url)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.channel.name != "skin-rendering"):
            return
        await self._upload_manager(message)

    @commands.command(aliases=["r"])
    async def skinrender(self, ctx: commands.Context, skin_id: str):
        """Render a skin from skins.tw with an id"""
        base_url = config.get('API', 'DATA_API')
        res = get_api(base_url, f"api/asset/{skin_id}")

        if (not res):
            await bmessage(ctx, "❌ invalid id")
        elif (res["type"] != "skin"):
            await bmessage(ctx, "❌ this asset is not a skin")
        else:
            url = f"{base_url}/{res['path']}"
            await self._send_render(ctx, url, res["name"])

def setup(bot: commands.Bot):
    bot.add_cog(Renderer())