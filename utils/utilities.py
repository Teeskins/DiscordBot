#!/usr/bin/env python3

import json, datetime, discord

def read_json(path: str) -> list:
    f = open(path, "r")
    data = json.load(f)
    f.close() 
    return data

def get_date() -> str:
    return str(datetime.datetime.now())[:-7]

async def bmessage(ctx: object, msg: str, footer: str = None) -> object:
    embed: object = discord.Embed(color=0x000000, description=msg)
    if (footer):
        embed.set_footer(text=footer)
    return await ctx.send(embed=embed)

# a: List[object]
get_name: callable = lambda a: [x.name for x in a]