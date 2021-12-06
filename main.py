from typing import *
from discord.ext import commands
import discord, json

from utils.utilities import read_json

extensions: Tuple[str] = (
    "cogs.resolve",
    "cogs.download",
    "cogs.role",
    "cogs.token",
    "cogs.moderator",
    "cogs.upload",
    "cogs.profile"
)

ENV: json = read_json("json/env.json")
bot = commands.Bot(command_prefix = ['!t '], help_command=commands.MinimalHelpCommand())

@bot.event
async def on_ready() -> None:
    await bot.change_presence(activity=discord.Game(name="skins.tw"))

def load_extensions(bot: Any, extensions: List[str]) -> None:
    for extension in extensions:
        bot.load_extension(extension)

if __name__ == "__main__":
    load_extensions(bot, extensions)
    bot.run(ENV["token"])