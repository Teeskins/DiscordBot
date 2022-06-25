"""scene cog"""

import uuid

from discord.ext import commands

from cogs.apis.twutils import TwUtilsAPI
from utils.page import Pages
from utils.utilities import get_skin, send_img, basic_message, make_groups

from typing import List, Dict

def args_to_dict(names: List[str], *args: List[str]) -> Dict[str, str]:
    """
        Convert two lists into a dict
    """

    ret = {}


    for name, arg in zip(names, args):
        ret[name] = arg
    
    return ret

class Scene(commands.Cog, Pages):
    """
        Managing the scenes system
    """

    def __init__(self):
        Pages.__init__(self)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if not reaction.message.author.bot or user.bot:
            return

        await reaction.remove(user)
        await self.handler(reaction, user)

    @commands.command()
    async def scene(
        self,
        ctx: commands.Context,
        name: str=None,
        skin_id: str=None
        ):
        """
            Displays a Teeskins scene, with an optional tee
        """

        if not name or not skin_id:
            return

        res, url = await get_skin(ctx, skin_id)

        if not res:
            return

        data = {
            "name": name,
            "skin": url
        }
        img = TwUtilsAPI.scene(data)

        if not img:
            return await basic_message(
                ctx,
                "❌ Error, Invalid scene"
            )
        filename = str(uuid.uuid1()) + ".png"

        with open(filename, "wb") as f:
            f.write(img)
    
        await send_img(ctx, name, filename)

    @commands.command()
    async def scenes(self, ctx: commands.Context):
        """
            List the availables scene
        """

        scenes = TwUtilsAPI.scene_list()

        if not scenes:
            return

        page_content = make_groups(scenes, 10)

        await self.create_pages(ctx, page_content)

def setup(bot: commands.Bot):
    bot.add_cog(Scene())
