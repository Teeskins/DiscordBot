"""upload cog"""

import hashlib
import requests
import discord

from discord.ext import commands
from typing import Dict

from cogs.apis.teeskins import TeeskinsAPI
from utils.config import DockerConfig
from utils.utilities import basic_message, signature_check

config = DockerConfig("config.ini")

unique_key = lambda ctx: str(ctx.guild.id) + str(ctx.author.id)

TEESKINS_EMOJI = "<:logo:881279804635234405>"

class UserPreUpload:
    """
        Represents upload informations before its uploaded (only PNGs)
    """

    def __init__(
        self,
        ctx: commands.Context,
        bot_msg: commands.Context,
        **data: Dict[str, str]
        ):

        self.ctx = ctx
        self.bot_msg = bot_msg
        self.data = data
    
    def __getitem__(self, __name: str) -> str:
        """
            Returns an attr in self.data
        """

        if not __name in self.data.keys():
            return ""
        
        return self.data[__name]
    
    def fancy_footer(self) -> str:
        """
            Returns a fancy string about the upload provider
        """

        ret = TEESKINS_EMOJI + " Uploaded the %s `%s` by `%s`" % \
            (
                self["type"],
                self["name"],
                self["author"]
            )

        return ret

class UserPreUploads:
    """
        This class manages multiple UserUpload
    """

    def __init__(self):
        self.pre_uploads = {}

    def __getitem__(self, key: str) -> UserPreUpload:
        if not key in self.pre_uploads.keys():
            return None
        
        return self.pre_uploads[key]

    def add(self, ctx: commands.Context,
        bot_msg: commands.Context,
        **data: Dict[str, str]
        ) -> bool:
        """
            Add a UserPreUpload object to the pre_uploads dict
        """

        key = unique_key(ctx)

        if self[key]:
            return False

        self.pre_uploads[key] = UserPreUpload(ctx, bot_msg, **data)

        return True
    
    def remove(self, key: str):
        """
            Removes an UserPreUpload from self.pre_uploads
        """

        del self.pre_uploads[key]

class Upload(commands.Cog):
    """
        It manages the uploads from Discord to db throught a REST API
    """

    CANCEL_MSG: str = "To reset your upload details: !t cancel"

    def __init__(self) -> None:
        self.users_pre_upload = UserPreUploads()

    async def upload_asset(
        self,
        key: str,
        message: object,
        asset: object,
        pre_upload: UserPreUpload
        ):
        """
            Uploading asset to the Teeskins waiting queue
            (where administrators have to accept the skins)
        """

        res = TeeskinsAPI.upload_asset(
            asset.content,
            type=pre_upload["type"],
            name=pre_upload["name"],
            author=pre_upload["author"]
        )

        await message.delete()
        await pre_upload.bot_msg.delete()

        if not res:
            return await basic_message(
                message.channel,
                "❌ Your asset has not been uploaded",
                "Your upload details has not been reset"
            )

        await basic_message(
            message.channel,
            pre_upload.fancy_footer(),
            message.author
        )

        self.users_pre_upload.remove(key)

    async def upload_handler(self, message: object):
        """
            It manages Discord attachments for assets
        """
    
        # 1. Checking if the attachment is valid
        attachs = message.attachments

        if len(attachs) != 1:
            return
        
        key = unique_key(message)

        pre_upload = self.users_pre_upload[key]

        if message.author.bot or not pre_upload:
            return

        if not pre_upload.ctx.channel.id == message.channel.id:
            return

        # 2. Download the asset and check if it is a PNG
        asset = requests.get(attachs[0])
        print(asset)
        if not signature_check(
            asset.content,
            b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
        ):
            return await basic_message(
                message.channel,
                "❌ Only PNGs are supported"
            )
        
        # 3. Check if it already exists in the database
        checksum = hashlib.md5(asset.content).hexdigest()
        duplicate = TeeskinsAPI.duplicate(checksum)

        if duplicate:
            return await basic_message(
                message.channel,
                f"❌ already exists ```id: {duplicate['id']}```",
                self.CANCEL_MSG
            )
        
        # 4. Try to upload it
        await self.upload_asset(key, message, asset, pre_upload)

    @commands.Cog.listener()
    async def on_message(self, message: object):
        """
            Waiting for users upload
        """

        await self.upload_handler(message)

    @commands.command()
    async def upload(
        self,
        ctx: commands.Context,
        name: str = None,
        _type: str = None,
        author: str = None
        ):
        """
            Upload an asset
            Allowed types:
                `skin`
                `mapres`
                `gameskin`
                `emoticon`
                `entity`
                `cursor`
                `particle`
                `font`
                `gridTemplate`

            example:
                `!t upload twinbop skin Nagi`
                If you want to use spaces :
                    `!t upload "honk honk" mapres "Nagi01 {LAN}"`
        """

        if not name or not _type or not author:
            return
        if isinstance(ctx.channel, discord.DMChannel):
            return
        if ctx.channel.name != "upload":
            return

        key = unique_key(ctx)
    
        await ctx.message.delete()

        if self.users_pre_upload[key]:
            return await basic_message(
                ctx,
                "🔒 you already have an upload in progress",
                self.CANCEL_MSG
            )
        
        msg = await basic_message(
            ctx, 
            f"📌 Your next attachment in this channel will be considered your asset",
            self.CANCEL_MSG
        )

        self.users_pre_upload.add(
            ctx,
            msg,
            name=name, type=_type, author=author
        )

    @commands.command()
    async def cancel(self, ctx: commands.Context):
        """
            Cancel the user upload in progress
        """

        key = unique_key(ctx)

        if not self.users_pre_upload[key]:
            return

        self.users_pre_upload.remove(key)
        await basic_message(
            ctx,
            "🔓 Your current upload has been canceled"
        )

def setup(bot: commands.Bot):
    bot.add_cog(Upload())
