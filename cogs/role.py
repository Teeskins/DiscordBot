"""roles cog"""

import discord

from discord.ext import commands

from utils.utilities import basic_message
from utils.config import DockerConfig
from cogs.apis.teeskins import TeeskinsAPI

config = DockerConfig("config.ini")

ROLES = {
    "Contributor": {
        "value": 1,
        "color": 0xffcdb2
    },
    "Supporter": {
        "value": 10,
        "color": 0xffb4a2
    },
    "Legend": {
        "value": 50,
        "color": 0xe5989b
    },
    "Master": {
        "value": 100,
        "color": 0xb5838d
    }
}

class Roles(commands.Cog):
    """
        This class manages the Teeskins roles
    """

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def init_roles(self, ctx: commands.Context):
        """
            Creates roles if needed
        """

        names = [role.name for role in ctx.guild.roles]

        if all(x in names for x in ROLES.keys()):
            return await basic_message(
                ctx,
                "❌ Roles have already been created"
            )

        for k, v in ROLES.items():
            colour = discord.Colour(v["color"])
            await ctx.guild.create_role(name=k, colour=colour)

        await basic_message(ctx, "✅ Roles have been created")

    @commands.command()
    async def role(self, ctx: commands.Context, token: str = None):
        """
            Give role in function of your upload_count on skins.tw
            Its recommended to run this command in a secure channel.
            You can create one with the command `!t login`
        """

        if not token:
            return

        await ctx.message.delete()

        res = TeeskinsAPI.user_role(token)

        if not res:
            return await basic_message(
                ctx,
                f"❌ Cannot find the user with the token `{token}`"
            )

        guild_role_names = [x.name for x in ctx.guild.roles]
        author_role_names = [x.name for x in ctx.author.roles]

        for k in list(ROLES.keys())[::-1]:
            if res["count_uploads"] < ROLES[k]["value"] and not k in guild_role_names:
                continue

            # Check if ctx.author has already updated his roles
            if k in author_role_names:
                return await basic_message(
                    ctx,
                    "❌ Your roles are already updated"
                )

            # Remove ctx.author roles in role.json
            for name in ROLES.keys():
                role = discord.utils.get(ctx.guild.roles, name=name)
                await ctx.message.author.remove_roles(role)

            role = discord.utils.get(ctx.guild.roles, name=k)

            # Apply role to ctx.author
            await basic_message(
                ctx,
                f"🔓 You have unlocked the role `{k}`"
            )
            return await ctx.message.author.add_roles(role)

        await basic_message(
            ctx,
            "❌ You have uploaded 0 assets in the database",
            "You can upload them to skins.tw"
        )

def setup(bot: commands.Bot):
    bot.add_cog(Roles())
