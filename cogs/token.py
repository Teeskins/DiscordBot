"""token cog"""

import discord
import asyncio
import uuid

from discord.ext import commands

from utils.utilities import basic_message

SECURE_MSG: str = """Secure channel, only you and administrators can see this channel\n \
This channel will be deleted automatically in 60 seconds"""

class Token(commands.Cog):
    """
        Security to enter your token
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.ids = []

    async def delete(self, key: str, _id: int, n: int = 60):
        """
            Delete temp Discord channel after n seconds
        """

        await asyncio.sleep(n)
        self.ids.remove(key)
        await self.bot.get_channel(_id).delete()

    @commands.command()
    async def login(self, ctx: commands.Context):
        """
            Creates a temp Discord channel,
            only administrators and the user can see this channel
        """

        await ctx.message.delete()
        key = str(ctx.guild.id) + str(ctx.author.id)

        if key in self.ids:
            return

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await ctx.guild.create_text_channel(
            str(uuid.uuid1()), overwrites=overwrites
        )

        await basic_message(
            channel,
            SECURE_MSG,
            "Common usage of this channel: !t role <token>"
        )
        await channel.send(ctx.author.mention)
        await basic_message(
            ctx,
            f"🔐 Secret channel {channel.mention}"
        )

        self.ids.append(key)
        asyncio.create_task(self.delete(key, channel.id))

def setup(bot: commands.Bot):
    bot.add_cog(Token(bot))
