#!/usr/bin/env python3

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

    async def _send_img(self, message: discord.Message, name: str, filename: str, url: str=None):
        embed_kwargs = {
            "title": name, 
            "color": 0x000000
        }
        if (url):
            embed_kwargs["url"] = url
        embed = discord.Embed(**embed_kwargs)
            
        file = discord.File(filename, filename=filename)
        embed.set_image(url=f'attachment://{filename}')
        await message.channel.send(embed=embed, file=file)
        os.remove(filename)

    async def _send_render(self, message: discord.message, data: json, call: callable, name: str=None):
        res = call(data)
        url = data["skin"]

        if (res.status_code == 500):
            await bmessage(message.channel, "❌ Error, invalid skin or invalid command format")
        elif (res.status_code == 422):
            return
        else:
            name = name or self._url_to_name(url)
            filename = self._save_tmp_img(res.content)
            await self._send_img(message, name, filename, url)
    
    async def _upload_manager(self, message: discord.Message):
        attachs = message.attachments
        if (self._is_attachs_valid(attachs) == False):
            return

        url = attachs[0].url
        data = {"skin": url}

        await self._send_render(message, data, self.render)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.channel.name != "skin-rendering"):
            return
        await self._upload_manager(message)

    async def _get_skin_url(self, ctx: commands.Context, skin_id: str) -> Any:
        """Get skin url with an id"""

        base_url = config.get('API', 'DATA_API')
        res = get_api(base_url, f"api/asset/{skin_id}")
        ret = None, None

        if (not res):
            await bmessage(ctx, "❌ invalid id")
        elif (res["type"] != "skin"):
            await bmessage(ctx, "❌ this asset is not a skin")
        else:
            url = f"{base_url}/{res['path']}"
            ret = res, url
        return (ret)

    @commands.command(aliases=["render"])
    async def r(self, ctx: commands.Context, skin_id: str=None, eye: str=None):
        """Render a skin from skins.tw with an id"""

        if (not skin_id):
            return

        res, url = await self._get_skin_url(ctx, skin_id)
        data = {
            "skin": url,
            "eye": eye or "default_eye"
        }
        await self._send_render(ctx, data, self.render, res['name'])
    
    @commands.command(aliases=["rendercolor"])
    async def rc(self, ctx: commands.Context, skin_id: str=None, bcolor: str=None, fcolor: str=None, mode: str=None, eye: str=None):
        """Render a skin with color from skins.tw with an id"""

        if (not skin_id or not bcolor or not fcolor or not mode):
            return

        res, url = await self._get_skin_url(ctx, skin_id)
        data = {
            "skin": url,
            "bcolor": bcolor,
            "fcolor": fcolor,
            "mode": mode,
            "eye": eye or 'default_eye'
        }
        await self._send_render(ctx, data, self.renderColor, res['name'])

def setup(bot: commands.Bot):
    bot.add_cog(Renderer())