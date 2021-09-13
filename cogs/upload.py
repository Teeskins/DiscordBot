from typing import *

import json, hashlib, requests, discord
from discord.ext import commands
from PIL import Image

from utils.utilities import bmessage, read_json
from cogs.resolve import get_api
from dataclasses import dataclass

ENV: json = read_json("json/env.json")
REACTION: json = read_json("json/reaction.json")

@dataclass
class WaitingUpload:
    """Object of an user before he uploads an asset (only PNGs)"""
    ctx: commands.Context
    bot_msg: commands.Context
    name: str
    _type: str
    author: str

def gen_key(ctx: commands.Context) -> str:
    """Generate an unique key"""
    return (str(ctx.guild.id) + str(ctx.author.id))

def signature_check(data: bytes, sig: bytes) -> bool:
    """Check file signature"""
    return (data[:len(sig)] == sig)

def post_asset(endpoint: str, value: str, **kwargs) -> bool:
    """POST an asset to the REST API"""
    file: str = kwargs.pop("file")
    r: object = requests.post(
        url=f"{endpoint}/{value}", 
        data=kwargs, 
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
        files={"file": file}
        )
    if (r.status_code != 200): return (False)
    return (r.json()["success"])

class Upload(commands.Cog):
    """It manages the uploads from Discord to db throught a REST API"""

    cancel_msg: str = "To reset your upload details: !t cancel"

    def __init__(self) -> None:
        self.waiting: Dict[str, WaitingUpload] = {}

    async def asset_attach(self, message: object) -> None:
        """It manages Discord attachments for assets"""
        attachs: object = message.attachments
        key: str = gen_key(message)
        if (len(attachs) != 1): return
        if (message.author.bot or not key in self.waiting.keys()): return
        obj: WaitingUpload = self.waiting[key]
        if (not obj.ctx.channel.id == message.channel.id): return

        # Check for the supported format (PNG)
        res: object = requests.get(attachs[0])
        if (not signature_check(res.content, b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")):
            return await bmessage(message.channel, "❌ Only PNGs are supported")
    
        # Check duplicate
        checksum: str = hashlib.md5(res.content).hexdigest()
        duplicate: json = get_api(f"{ENV['api']}/checkDuplicate", checksum)
        if (duplicate):
            return await bmessage(message.channel, f"❌ already exists ```id: {duplicate['id']}```", self.cancel_msg)
        
        if (not post_asset(ENV["api"], "api/storeAsset/discord", 
            file=res.content, type=obj._type, 
            name=obj.name, author=obj.author)):
            del self.waiting[key]
            await message.delete()
            await obj.bot_msg.delete()
            return await bmessage(message.channel, "❌ Your asset has not been uploaded", "Your upload details has been reset")

        await message.delete()
        await obj.bot_msg.delete()
        await bmessage(message.channel, f"<:logo:881279804635234405> Uploaded the {obj._type} `{obj.name}` by `{obj.author}`", message.author)
        del self.waiting[key]

    @commands.Cog.listener()
    async def on_message(self, message: object):
        await self.asset_attach(message)

    @commands.command()
    async def upload(self, ctx: commands.Context, name: str = None, _type: str = None, author: str = None):
        """
        Upload an asset
        Allowed types: `skin` | `mapres` | `gameskin` | `emoticon` | `entity` | `cursor` | `particle` | `font` | `gridTemplate`
        """
        key: str = gen_key(ctx)
        if (not name or not _type or not author): return
        if (isinstance(ctx.channel, discord.DMChannel)): return
        if (ctx.channel.name != "upload"): return

        await ctx.message.delete()
        if (key in self.waiting.keys()):
            return await bmessage(ctx, "🔒 you already have an upload in progress", self.cancel_msg)
        
        msg: object = await bmessage(ctx, f"📌 Your next attachment in this channel will be considered your asset", self.cancel_msg)
        self.waiting[key] = WaitingUpload(ctx, msg, name, _type, author)

    @commands.command()
    async def cancel(self, ctx: commands.Context):
        """Cancel the upload in progress"""
        key: str = gen_key(ctx)
        if (not key in self.waiting.keys()): return

        del self.waiting[key]
        await bmessage(ctx, "Your current upload has been canceled")

def setup(bot: commands.Bot):
    bot.add_cog(Upload())