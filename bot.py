#!/usr/bin/env python3

from typing import *
from discord.ext import commands
import discord, logging

log: logging.Logger = logging.getLogger(__name__)

extensions: Tuple[str] = (
    "cogs.resolve",
    "cogs.download",
    "cogs.role",
    "cogs.token",
    "cogs.moderator",
    "cogs.upload",
    "cogs.profile"
)

class Teeskins(commands.Bot):
    """Pirmary class that contains the bot object to run"""

    def __init__(self):
        super().__init__(command_prefix = ["!t "], help_command=commands.MinimalHelpCommand())

        for extension in extensions:
            try:
                self.load_extension(extension)
                log.info(f"Loaded the extension {extension}")
            except:
                log.warning(f"Failed to load the extension {extension}")
    
    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity = discord.Game(name = "skins.tw"))

    async def close(self):
        log.info("Closing")
        await super().close()

    async def on_command(self, ctx: commands.Context):
        destination: str = [f"#{ctx.channel} ({ctx.guild})", "DM"][not ctx.guild]
        log.info(f"{ctx.author} used command in {destination}: {ctx.message.content}")