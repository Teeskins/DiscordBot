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
    name: str
    _type: str
    author: str

def gen_key(ctx: commands.Context) -> str:
        return (str(ctx.guild.id) + str(ctx.author.id))

def find_duplicate(md5: str) -> json:
    """Check for duplicate asset"""
    res: List[dict] = get_api(f"{ENV['api']}/checkDuplicate", md5)
    return (res)

def post_asset(url: str, ) -> bool:
    """POST an asset to the REST API"""
    pass

class Upload(commands.Cog):
    """It manages the uploads from Discord to db throught a REST API"""

    def __init__(self) -> None:
        self.waiting: Dict[str, WaitingUpload] = {}

    async def asset_attach(self, message: object) -> None:
        """It manages Discord attachments for assets"""
        attachs: object = message.attachments
        key: str = gen_key(message)
    
        if (len(attachs) != 1): return
        if (message.author.bot or not key in self.waiting.keys()): return
    
        res: object = requests.get(attachs[0])
        checksum: str = hashlib.md5(res.content).hexdigest()
        duplicate: json = find_duplicate(checksum)
        if (duplicate):
            return await bmessage(message.channel, f"❌ already exists ```id: {duplicate['id']}```")
        
        await message.delete()
        del self.waiting[key]

    @commands.Cog.listener()
    async def on_message(self, message: object):
        #if (not isinstance(message.channel, discord.DMChannel)): 
        #    if (message.channel.name == "channel_name"):
        #         pass
        await self.asset_attach(message)

    @commands.command()
    async def upload(self, ctx: commands.Context, 
                    name: str = None, _type: str = None, 
                    author: str = None):
        """Upload a an asset"""
        key: str = gen_key(ctx)
        if (not name or not _type or not author): return
        if (key in self.waiting.keys()):
            return await bmessage(ctx, "📬 you already have an upload in progress")
        
        self.waiting[key] = WaitingUpload(ctx, name, _type, author)

        await bmessage(ctx, f"📭 {ctx.author.mention} upload your asset",
        "Your next attachment will be considered your asset")

def setup(bot: commands.Bot):
    bot.add_cog(Upload())