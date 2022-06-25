"""utilities module"""

import discord
import os
import pandas as pd

from discord.ext import commands
from typing import Tuple, Any

from cogs.apis.teeskins import TeeskinsAPI

async def basic_message(ctx: object, msg: str, footer: str = None) -> object:
    """
        Sending a simple message    
    """
    
    embed: object = discord.Embed(color=0x000000, description=msg)

    if footer:
        embed.set_footer(text=footer)

    return await ctx.send(embed=embed)

get_name = lambda a: [x.name for x in a]

def basic_frame(data: dict) -> str:
    """
        Return a basic frame (name, value)
    """

    data = data or {"--": "--"}

    data = {
        "Name": data.keys(),
        "Value": data.values()
    }

    return pd.DataFrame(data=data).to_string(index=False)

def signature_check(data: bytes, sig: bytes) -> bool:
    """
        Check file signature
    """

    return data[:len(sig)] == sig

def fill_min(*args: Tuple[list]) -> list:
    """
        Set every list with the same length
    """

    length = len(max(*args, key=len))
    args = list(args)
    
    for i in range(len(args)):
        args[i] += (length - len(args[i])) * [" "]

    return args

def make_groups(arr: Any, size: int) -> list:
    """
        Makes list of iterable with a costant size
    """

    return [arr[i:i + size] for i in range(0, len(arr), size)]

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
