#!/usr/bin/env python3

from typing import *

import discord, requests, json
import pandas as pd
from discord.ext import commands
from configparser import ConfigParser

from cogs.page import Pages
from utils.utilities import read_json, bmessage

config: ConfigParser = ConfigParser()
config.read("config.ini")

REACTION: json = read_json("data/json/reaction.json")

def get_api(endpoint: str, value: str) -> List[dict]:
    r: object = requests.get(url=f"{endpoint}/{value}")
    if (r.status_code != 200 or not r.text):
        return []
    return (r.json())
 
def is_list_in_list(l1: list, l2: list) -> bool:
    return (all(x in l1 for x in l2))

def format_search(data: List[dict], *columns: List[str]) -> dict:
    # data[0] because we suppose its a list where every element has the same pattern
    if (not is_list_in_list(list(data[0].keys()), columns)):
        return ({"Didnt": ["found"]})
    ret: dict = {k: [] for k in columns}
    for x in columns:
        for d in data:
            ret[x] += [d[x]] if (len(str(d[x])) <= 10) else [f"{str(d[x])[:10]}..."]
    return (ret)

def group_list(arr: list, size: int) -> list:
    return [arr[i:i + size] for i in range(0, len(arr), size)]

class Resolve(commands.Cog, Pages):
    """It resolves names <-> ids"""

    def __init__(self, bot: commands.Bot):
        Pages.__init__(self)
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if (not reaction.message.author.bot or user.bot):
            return
        try:
            await self.check_for_pages(reaction, user)
            await reaction.remove(user)
        except:
            pass

    @commands.command()
    async def find(self, ctx: commands.Context, name: str = None):
        """Displays asset found with the keyword 'name'"""
        if (not name): return
        res: List[dict] = get_api(f"{config.get('API', 'HOST')}/search", name)
        if (not res):
            return await bmessage(ctx, f"❌ cannot find assets with the name `{name}`")

        frame: str = pd.DataFrame(format_search(res, "id", "name", "type", "author")).to_string(index=False)
        pages: List[List[str]] = group_list(frame.split('\n'), 10)
        await self.send_first_page(ctx, pages)
        
def setup(bot: commands.Bot):
    bot.add_cog(Resolve(bot))