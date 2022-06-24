"""renderer cog"""

import discord
import json
import uuid
import os

from discord.ext import commands
from utils.config import DockerConfig
from typing import Any

from utils.utilities import basic_message
from cogs.apis.teeskins import TeeskinsAPI
from cogs.apis.twutils import TwUtilsAPI

config = DockerConfig("config.ini")

def url_to_name(url: str) -> str:
    """
        Takes the word after the last / (delimitor)
    """

    name = url.split("/")[-1]
    name = name.split(".")[0]

    return name

async def send_img(
    message: discord.Message,
    name: str,
    filename: str,
    url: str=None
    ):
    """
        Saving a temp image and send it to a Discord channel
    """

    kwargs = {
        "title": name, 
        "color": 0x000000
    }

    if url:
        kwargs["url"] = url
        
    embed = discord.Embed(**kwargs)
    file = discord.File(filename, filename=filename)

    embed.set_image(url="attachment://" +filename)
    await message.channel.send(embed=embed, file=file)

    os.remove(filename)

async def send_render(
    message: discord.message,
    call: callable,
    data: json,
    name: str=None
    ):
    """
        It will send the rendered skin to a Discord channel
    """

    img = call(data)
    url = data["skin"]

    if not img:
        return await basic_message(
            message.channel,
            "❌ Error, invalid skin or invalid command format"
        )
    name = name or url_to_name(url)
    filename = str(uuid.uuid1()) + ".png"

    with open(filename, "wb") as f:
        f.write(img)
    
    await send_img(message, name, filename, url)

async def get_skin(ctx: commands.Context, skin_id: str) -> Any:
    """
        Returns JSON information and an url
    """

    res = TeeskinsAPI.asset(skin_id)
    ret = None, None

    if not res:
        await basic_message(ctx, "❌ invalid id")
    elif res["type"] != "skin":
        await basic_message(ctx, "❌ this asset is not a skin")
    else:
        url = TeeskinsAPI.HOST + "/" + res["path"]
        ret = res, url

    return ret

class Renderer(commands.Cog):
    """
        Rendering Teeworlds skins
        (via upload or commands)
    """
    
    async def upload_handler(self, message: discord.Message):
        """
            Rendering uploaded valid skins
        """

        attachs = message.attachments

        if len(attachs) != 1:
            return

        attach = attachs[0]

        if (not ".png" in attach.filename):
            return

        url = attachs[0].url
        data = {"skin": url}

        await send_render(message, TwUtilsAPI.render, data)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
            Listening for skin upload
        """

        if message.channel.name != "skin-rendering":
            return

        await self.upload_handler(message)

    @commands.command(aliases=["render"])
    async def r(self, ctx: commands.Context, skin_id: str=None, eye: str=None):
        """
            Render a skin from skins.tw with an id
        """

        if not skin_id:
            return

        res, url = await get_skin(ctx, skin_id)
        data = {
            "skin": url,
            "eye": eye or "default_eye"
        }

        await send_render(ctx, TwUtilsAPI.render, data, res["name"])
    
    @commands.command(aliases=["rendercolor"])
    async def rc(
        self,
        ctx: commands.Context,
        skin_id: str=None,
        bcolor: str=None,
        fcolor: str=None,
        mode: str=None,
        eye: str=None
    ):
        """
            Render a skin with color from skins.tw with an id
        """

        if not skin_id or not bcolor or not fcolor or not mode:
            return

        res, url = await get_skin(ctx, skin_id)
        data = {
            "skin": url,
            "bcolor": bcolor,
            "fcolor": fcolor,
            "mode": mode,
            "eye": eye or "default_eye"
        }

        await send_render(ctx, TwUtilsAPI.render_color, data, res["name"])

def setup(bot: commands.Bot):
    bot.add_cog(Renderer())
