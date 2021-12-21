#!/usr/bin/env python3

from typing import *

import discord, json, uuid, os, random
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from configparser import ConfigParser

from utils.utilities import bmessage
from cogs.resolve import get_api

config: ConfigParser = ConfigParser()
config.read("config.ini")

class CardStyle:
    """Style information for the card image"""

    font_path: str = "./data/fonts/font.ttf"
    img_path: str = "./data/img"
    bg: str = "./data/profile_bg"
    margin: int = 10
    sub_margin: int = 30 + margin
    name_size: int = 20
    details_size: int = 15
    bg_rect_color: Tuple = (10, 10, 10, 224)
    user_text_color: Tuple = (217, 217, 217, 255)
    main_text_color: Tuple = (255, 255, 255, 255)
    name_rect: Tuple = (255, 255, 255, 50)
    subtext_color: Tuple = (255, 255, 255, 165)
    categories: Dict[str, int] = {
        "Assets": 100,
        "Uploads": 50,
        "Downloads": 50,
        "Total": 50
        }

def round_rectangle(size: Tuple[int, int], radius: int, *, color: Tuple) -> Image.Image:
    width, height = size

    radius = min(width, height, radius * 2)
    width *= 2
    height *= 2

    corner = Image.new('RGBA', (radius, radius))
    draw = ImageDraw.Draw(corner)
    xy = (0, 0, radius * 2, radius * 2)
    draw.pieslice(xy, 180, 270, fill=color)

    rect = Image.new('RGBA', (width, height), color=color)
    rect.paste(corner, (0, 0))
    rect.paste(corner.rotate(90), (0, height - radius))
    rect.paste(corner.rotate(180), (width - radius, height - radius))
    rect.paste(corner.rotate(270), (width - radius, 0))

    return rect.resize(size, resample=Image.LANCZOS, reducing_gap=1.0)

class UserProfile(CardStyle):
    """Manage user profile, generate cards"""

    def __init__(self, name: str, detailed: bool):
        # Card properties
        self.username: str = [f"{name[:20]}...", name][len(name) <= 20] 
        self.detailed: bool = detailed
        self.img_name: str = str(uuid.uuid1()) + ".png"
        self.data: json = get_api(f"{config.get('API', 'HOST')}/api/profile", name)
        self.valid: bool = not "error" in self.data.keys()

        if (not self.valid):
            return

        # Image objects
        self.text_w: int = len(self.username) * self.name_size // 2
        self.size: Tuple(int, int) = [(470, 190), (470, 420)][detailed]
        self.img: Image = Image.new('RGBA', self.size, "white")
        self.draw: ImageDraw = ImageDraw.Draw(self.img)

    def __draw_background(self):
        x, y = self.margin, self.margin
        img_path: str = f"{self.bg}/{random.choice(os.listdir(self.bg))}"
        bg: Image = Image.open(img_path)

        self.img.paste(bg.resize(self.size))
        w, h = self.size[0] - (self.margin * 2), self.size[1] - (self.margin * 2)
        rr: Image = round_rectangle((w, h), 10, color=self.bg_rect_color)
        self.img.alpha_composite(rr, dest=(x, y))

    def __draw_total(self, offsets: List[int]):
        font: object = ImageFont.truetype(self.font_path, size=self.name_size)
        y: int = self.size[1] - self.sub_margin - 10
        data: List[int] = [self.data["uploadData"]["totalCount"], self.data["downloadData"]["totalCount"]]
        data += [sum(data)]

        self.draw.text((offsets[0], y), "Total", font=font, fill=self.main_text_color)
        for offset, value in zip(offsets[1:], data):
            self.draw.text((offset, y), str(value), font=font, fill=self.main_text_color)

    def __draw_stats(self, y: int, offsets: List[int]):
        font: object = ImageFont.truetype(self.font_path, size=self.details_size)
        keys: Dict[str, int] = self.data["uploadData"]["assetsCount"].keys()
        stats: List[int, int] = list(zip(
            self.data["uploadData"]["assetsCount"].values(),
            self.data["downloadData"]["assetsCount"].values()
            )
        )
        stats = map(list, stats)
        self.__draw_total(offsets)

        if (not self.detailed):
            return

        for k, v in zip(keys, stats):
            self.draw.text((self.sub_margin, y), k.title(), font=font, fill=self.subtext_color)
            for offset, value in zip(offsets[1:], v + [sum(v)]):
                self.draw.text((offset, y), str(value), font=font, fill=self.subtext_color)
            y += self.details_size + 11

    def __draw_categories(self, y: int):
        font: object = ImageFont.truetype(self.font_path, size=self.details_size)
        x: int = self.sub_margin
        separator_y: int = y + self.details_size + 5
        offsets: List[int] = [x]

        # Categories
        for k, v in self.categories.items():
            self.draw.text((x, y), k, font=font, fill=self.main_text_color)
            x += len(k) * (self.details_size // 2) + v
            offsets.append(x)

        # Separator
        self.draw.rectangle((self.sub_margin - 10, separator_y,
        self.size[0] - self.sub_margin + 10, separator_y + 1), fill=self.main_text_color)

        # Categories details
        self.__draw_stats(separator_y + 10, offsets)

    def __draw_rank(self, offset: int, y: int, category: str) -> int:
        font: object = ImageFont.truetype(self.font_path, size=self.name_size)
        rank_img: Image = Image.open(f"{self.img_path}/{category}.png")
        w, _ = rank_img.size

        self.img.alpha_composite(rank_img, dest=(offset, y))
        offset += w + 5

        self.draw.text((offset, y), "#", font=font, fill=self.subtext_color)
        offset += self.name_size // 2 + 5

        rank: str = str(self.data[f"{category}Data"]["rank"])
        rank = ["-", rank][rank != "None"]
        self.draw.text((offset, y), rank, font=font, fill=self.main_text_color)
        return (offset + (len(rank) * (self.name_size // 2)) + 10)

    def __draw_header(self):
        font: object = ImageFont.truetype(self.font_path, size=self.name_size)
        x, y = self.sub_margin, self.sub_margin - 5
        w, h = self.text_w + 20, int(self.name_size * 2)

        # White rectangle
        rr: Image = round_rectangle((w, h), 25, color=self.name_rect)
        self.img.alpha_composite(rr, dest=(x, y))

        # Username
        text_x: int = x + ((w - self.text_w) // 2)
        text_y: int = y + ((h - self.name_size) // 2)
        self.draw.text((text_x, text_y), self.username, font=font, fill=self.user_text_color)

        # Ranks
        offset: int = self.__draw_rank(x + w + 15, text_y, "upload")
        self.__draw_rank(offset, text_y, "download")
        
    def process(self):
        """Execute every previous steps"""
        self.__draw_background()
        self.__draw_header()
        self.__draw_categories(100)
        self.img.save(self.img_name)        

class Profile(commands.Cog):
    """Manage profiles"""

    async def card(self, ctx: commands.Context, username: str, detailed: bool = False):
        """Send a Discord message that contain the public card"""
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