"""Overriding commands.Bot"""

import discord, logging

from typing import *
from discord.ext import commands

from utils.database import CursorDB
from utils.config import DockerConfig

log = logging.getLogger(__name__)
config = DockerConfig("config.ini")

EXTENSIONS = (
    "cogs.resolve",
    "cogs.download",
    "cogs.role",
    "cogs.token",
    # "cogs.moderator",
    "cogs.upload",
    # "cogs.profile",
    "cogs.renderer",
    # "cogs.log"
)

commands.MinimalHelpCommand()
class Bot(commands.Bot, CursorDB):
    """
        Primary class that contains the bot object to run
    """

    def __init__(self):
        self.bot_options = {}

        self._get_options()
        super().__init__(**self.bot_options)
        CursorDB.__init__(self)

        for extension in EXTENSIONS:
            # try:
            self.load_extension(extension)
            log.info(f"Loaded the extension {extension}")
            # except:
                # log.warning(f"Failed to load the extension {extension}")

    def _get_options(self):
        for k, v in config.items("BOT"):
            k = k.lower()
            if (v):
                self.bot_options[k] = eval(v)

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Game(name = "skins.tw"))

    async def close(self):
        log.critical("Closing")
        await self.close()

    async def on_command(self, ctx: commands.Context):
        dest = [f"#{ctx.channel} ({ctx.guild})", "DM"][not ctx.guild]
        log.info(f"{ctx.author} used command in {dest}: {ctx.message.content}")

        name = ctx.command.name
        self.execute(f"""INSERT INTO command_stat (guild_id, name)
                VALUES({ctx.guild.id}, '{name}')
                ON DUPLICATE KEY
                UPDATE count = count + 1""")

    async def on_guild_join(self, guild: discord.Guild):
        log.warning(f"{self.user} (ID: {self.user.id}) has joined {guild.name} (ID: {guild.id})")

        self.execute(f"""INSERT INTO guild_log_permission (guild_id) VALUES({guild.id})""")
        self.execute(f"""INSERT INTO guild_log_channel (guild_id) VALUES({guild.id})""")

    async def on_guild_remove(self, guild: discord.Guild):
        log.warning(f"{self.user} (ID: {self.user.id}) has left {guild.name} (ID: {guild.id})")

        self.execute(f"""DELETE FROM guild_log_permission WHERE guild_id={guild.id}""")
