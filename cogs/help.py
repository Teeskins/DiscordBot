from typing import *

from discord.ext import commands
from utils.utilities import display_panel

class Help(commands.Cog):
    """Stuff that help to understand how works the bot"""

    @commands.command()
    async def help(self, ctx: commands.Context):
        """Displays the help panel"""
        await display_panel(ctx, "json/panel.json", "help")

def setup(bot: commands.Bot):
    bot.add_cog(Help())