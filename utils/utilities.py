"""utilities module"""

import discord
import pandas as pd

from typing import Tuple, Any

async def basic_message(ctx: object, msg: str, footer: str = None) -> object:
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
