"""resolve cog"""

import pandas as pd

from discord.ext import commands

from utils.config import DockerConfig
from utils.page import Pages
from utils.utilities import basic_message, make_groups
from typing import List
from cogs.apis.teeskins import TeeskinsAPI

config = DockerConfig("config.ini")

def is_list_in_list(l1: list, l2: list) -> bool:
    """
        Check if a list contains another list
    """

    return all(x in l1 for x in l2)

def format_search(data: List[dict], *columns: List[str]) -> dict:
    """
        Parsing and formatting the search
    
        data[0] because we suppose its a list where
         every element has the same pattern
    """

    if not is_list_in_list(list(data[0].keys()), columns):
        return {"Didnt": ["found"]}

    ret = {k: [] for k in columns}

    for x in columns:
        for d in data:
            if len(str(d[x])) <= 10:
                ret[x] += [d[x]]
            else:
                ret[x] += [f"{str(d[x])[:10]}..."]

    return ret

class Resolve(commands.Cog, Pages):
    """
        It resolves asset
    """

    def __init__(self, bot: commands.Bot):
        Pages.__init__(self)
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if not reaction.message.author.bot or user.bot:
            return

        try:
            await self.handler(reaction, user)
            await reaction.remove(user)
        except:
            return

    @commands.command()
    async def find(self, ctx: commands.Context, name: str = None):
        """
            Displays asset found with the name
        """

        if not name:
            return

        res = TeeskinsAPI.search(name)
        
        if not res:
            return await basic_message(
                ctx,
                f"❌ cannot find assets with the name `{name}`"
            )

        search = format_search(res, "id", "name", "type", "author")
        frame = pd.DataFrame(search).to_string(index=False)
        pages = make_groups(frame.split("\n"), 10)
        await self.create_pages(ctx, pages)
        
def setup(bot: commands.Bot):
    bot.add_cog(Resolve(bot))
