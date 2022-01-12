import discord
from discord.embeds import EmptyEmbed
from discord.ext import commands
import datetime
import firebase_admin
from firebase_admin import db
import asyncio

class BetaReload(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Beta Reload Cog Loaded.')

    @commands.command(name = "reload")
    @commands.is_owner()
    async def reload(self,ctx,extention):
        self.client.unload_extension(f'betacogs.{extention}')
        self.client.load_extension(f'betacogs.{extention}')
        await ctx.reply(f'Reloaded {extention} sucessfully')
    @reload.error
    async def reload_error(self,ctx, error):
        await ctx.reply(f'There was an error running this command: \n`{error}`')

        # Loading Cogs
    @commands.command(name = "load",hidden=True)
    @commands.is_owner()
    async def load(self,ctx,extention):
        self.client.load_extension(f'betacogs.{extention}')
        await ctx.reply(f'Loaded {extention} sucessfully')
    @load.error
    async def load_error(self,ctx, error):
        await ctx.reply(f'There was an error running this command: \n`{error}`')        

    @commands.command(name = "unload",hidden=True)
    @commands.is_owner()
    async def unload(self,ctx,extention):
        self.client.unload_extension(f'betacogs.{extention}')
        await ctx.reply(f'Unloaded {extention} sucessfully')
    @unload.error
    async def unload_error(self,ctx, error):
        await ctx.reply(f'There was an error running this command: \n`{error}`')    


def setup(client):
    client.add_cog(BetaReload(client))