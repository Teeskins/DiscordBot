#!/usr/bin/env python3

from typing import *

import discord, requests, json
import pandas as pd
from discord.ext import commands
from dataclasses import dataclass
from configparser import ConfigParser

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

@dataclass
class Page:
    """Structure used to store clients"""

    msg: commands.Context
    author_id: int
    data: List[List[str]]
    page: int

class Pages:
    """Manage Page objects"""

    def __init__(self):
        self.pages: Dict[int, Page] = {}
    
    def __add_page(self, msg: discord.Message, author_id: str, pages: List[List[str]]):
        """Add a page to self.pages"""

        self.pages[msg.id] = Page(msg, author_id, pages, 0)

    async def send_first_page(self, ctx: commands.Context, pages: List[List[str]]):
        """Create and send the first page"""

        embed = discord.Embed(
            color       = 0x000000,
            description = "```" + '\n'.join(pages[0]) + "```"
        )
        embed.set_footer(text=f"page 1 / {len(pages)}")

        msg = await ctx.send(embed=embed)
        for _, v in REACTION["pages"].items():
            await msg.add_reaction(v)

        self.__add_page(msg, ctx.author.id, pages)

    def __get_obj(self, r_dst: object, msg_id: str, r_src: str, user: object) -> bool:
        """If the user click on the right emoji + the message id exists,
        then it will return the associated object"""

        if (str(r_dst) != r_src):
            return (None)

        if (not msg_id in list(self.pages.keys())):
            return (None)

        obj: Page = self.pages[msg_id]
        if (obj.author_id != user.id):
            return (None)

        return (obj)

    async def __change_page(self, r_dst: object, msg_id: str, r_src: str, move: int, user: object):
        """Go to previous or next page"""

        obj = self.__get_obj(r_dst, msg_id, r_src, user)
        if (not obj):
            return

        if (obj.page + move < 0 or obj.page + move > len(obj.data) - 1):
            return

        obj.page += move

        display = "```" + '\n'.join(obj.data[obj.page]) + "```"
        embed = discord.Embed(color=0x000000, description=display)
        embed.set_footer(text=f"page {obj.page + 1} / {len(obj.data)}")
        await obj.msg.edit(embed=embed)

    async def __delete(self, r_dst: object, msg_id: str, r_src: str, user: object):
        """Delete the author message"""

        obj = self.__get_obj(r_dst, msg_id, r_src, user)
        if (not obj):
            return
        
        await obj.msg.delete()
        del self.pages[msg_id]

    async def check_for_pages(self, reaction: object, user: object):
        """Check reactions"""

        _id = reaction.message.id
        page = REACTION["pages"]
    
        await self.__change_page(reaction, _id, page["previous"], -1, user)
        await self.__change_page(reaction, _id, page["next"], 1, user)
        await self.__delete(reaction, _id, page["delete"], user)

class Resolve(commands.Cog, Pages):
    """It resolves names <-> ids"""

    def __init__(self, bot: commands.Bot):
        Pages.__init__(self)
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if (not reaction.message.author.bot or user.bot):
            return
        await reaction.remove(user)
        await self.check_for_pages(reaction, user)

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