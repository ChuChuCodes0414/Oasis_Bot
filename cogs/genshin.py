import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import db
import asyncio
import genshin
import sensitive

class Genshin(commands.Cog):
    """
        Genshin.py api commands
    """
    def __init__(self,client):
        self.client = client
        self.short = "<:genshinicon:976949476784750612> | Genshin Impact"
        self.genshinclient = genshin.Client()
        self.genshinclient.set_cookies(ltuid=sensitive.LTUID, ltoken= sensitive.LTTOKEN)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Genshin Cog Loaded.')
    


async def setup(client):
    await client.add_cog(Genshin(client))

