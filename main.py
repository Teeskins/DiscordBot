from typing import *
from discord.ext import commands
import discord, asyncio, json

from utils.utilities import read_json

extensions: Tuple[str] = (
    "cogs.resolve",
    "cogs.download",
    "cogs.role",
    "cogs.help"
)

ENV: json = read_json("json/env.json")
bot = commands.Bot(command_prefix = ['!t '])
bot.remove_command("help")

@bot.event
async def on_ready() -> None:
    await bot.change_presence(activity=discord.Game(name="skins.tw"))

def load_extensions(bot: Any, extensions: List[str]) -> None:
    for extension in extensions:
        bot.load_extension(extension)

if __name__ == "__main__":
    load_extensions(bot, extensions)
    bot.run(ENV["token"])