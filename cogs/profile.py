from typing import *

import discord, json, uuid, os
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from utils.utilities import bmessage, read_json, get_name
from cogs.resolve import get_api

ROLE: json = read_json("json/role.json")
ENV: json = read_json("json/env.json")

class CardStyle:
    """Some style information for the card image"""
    font_path: str = "./fonts/font.ttf"
    margin: int = 10
    username_size: int = 20
    bg_rect_color: Tuple = (0, 0, 0, 224)
    user_rect_color: Tuple = (0, 0, 0, 48)
    user_text_color: Tuple = (217, 217, 217, 255)
    main_text_color: Tuple = (255, 255, 255, 255)
    subtext_color: Tuple = (255, 255, 255, 165)

class UserProfile(CardStyle):
    """Manage user profile, generate cards"""

    def __init__(self, username: str, detailed: bool):
        # Card properties
        self.username: str = username
        self.detailed: bool = detailed
        self.img_name: str = str(uuid.uuid1()) + ".png"
        self.data: json = get_api(f"{ENV['api']}/api/profile", self.username)
        self.valid: bool = not "error" in self.data.keys()

        if (not self.valid):
            return

        # Image objects
        self.size: Tuple(int, int) = [(470, 190), (470, 420)][detailed]
        self.img: Image = Image.new('RGBA', self.size, (127, 127, 127, 20))
        self.draw: ImageDraw = ImageDraw.Draw(self.img)

    def draw_background(self):
        """Add the informations to the image"""
        x1, y1 = self.margin, self.margin
        x2, y2 = self.size[0] - self.margin, self.size[1] - self.margin
        self.draw.rounded_rectangle(((x1, y1), (x2, y2)), 10, fill=self.bg_rect_color)

    def draw_rank(self):
        # taille username -> ranks
        pass

    def draw_stats(self):
        # draw total en permier
        # si pas detailde, return
        # chercher la key la plus grande -> espacement -> < 15 char
        pass

    def draw_categories(self):
        # text +white separator
        pass

    def draw_username(self):
        font: object = ImageFont.truetype(self.font_path, size=self.username_size)

    
    def process(self):
        """Execute every previous steps"""
        self.draw_background()
        self.draw_username()
        self.img.save(self.img_name)        

class Profile(commands.Cog):
    """Manage profiles"""

    async def card(self, ctx: commands.Context, username: str, detailed: bool = False):
        username: str = username or ctx.author.display_name
        u: UserProfile = UserProfile(username, detailed)

        if (not u.valid):
            return (await bmessage(ctx, "❌ Invalid username"))
        u.process()
        await ctx.send(file=discord.File(u.img_name))
        os.remove(u.img_name)

    @commands.command(aliases=["profile"])
    async def p(self, ctx: commands.Context, username: str = None):
        """Display a card (image) with your public informations"""
        await self.card(ctx, username, False)

    @commands.command()
    async def dprofile(self, ctx: commands.Context, username: str = None):
        """Display a card (image) with your public informations (more details version"""
        await self.card(ctx, username, True)

def setup(bot: commands.Bot):
    bot.add_cog(Profile())