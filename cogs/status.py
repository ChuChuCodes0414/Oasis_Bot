import discord
from discord.ext import commands
import json
import sys
import traceback
import math
import datetime

class Status(commands.Cog):
    """
        Bot status, pings, updates.
    """
    def __init__(self,client):
        self.client = client

    def get_prefix(self,client,guild):
        with open('prefixes.json','r') as f:
            prefixes = json.load(f)

        return prefixes[str(guild.id)]
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot Status Cog Loaded.')

    @commands.command(description = "Returns a message.",help = "ping")
    async def ping(self,ctx):
        embed = discord.Embed(title = "Pong 🏓",color = discord.Color.random())
        embed.set_footer(text = "For more detailed information, use pingmore.")
        await ctx.reply(embed = embed)
    
    @commands.command(description = "Get the bot's ping.",help = "pingmore")
    async def pingmore(self,ctx):
        apiping = round(self.client.latency*1000)
        embed = discord.Embed(title = "Pong 🏓",description = f"API Ping: `{apiping}ms`",color = discord.Color.random())
        embed.set_footer(text = "Note: This message can be misleading.")
        message = await ctx.reply(embed = embed)
        latency = ctx.message.created_at - message.created_at
        embed = discord.Embed(title = "Pong 🏓",description = f"API Ping: `{apiping}ms`\nYour Ping: `{latency.microseconds*0.001}ms`",color = discord.Color.random())
        embed.set_footer(text = "Note: This message can be misleading.")
        await message.edit(embed = embed)

    @commands.command(description = "Quick information about the bot.",help = "botinfo")
    async def botinfo(self,ctx):
        guild = ctx.guild
        embed = discord.Embed(title="Oasis Bot",description=f"Bot Information", color=discord.Color.green())
        embed.add_field(name="Name", value=f"Oasis Bot", inline=True) 
        embed.add_field(name="Creator", value=f"ChuGames#0001", inline=True)
        embed.add_field(name="Description", value=f"A helpful bot with a variety of features, from private channels to mod logging. Ping the bot to find out the prefix!", inline=False)
        embed.add_field(name="Server Count", value=f"{len(self.client.guilds)} servers", inline=False)
        embed.add_field(name="Found any Bugs?", value=f"Join the [support server](https://discord.com/invite/9pmGDc8pqQ)", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)

    @commands.command(description = "The most recent updates to the main bot will go here.",help = "botupdates")
    async def botupdates(self,ctx):
        embed = discord.Embed(title="Oasis Bot",description=f"Bot Updates have been moved to the [support server](https://discord.com/invite/9pmGDc8pqQ)", color=discord.Color.green())
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)

    @commands.command(description = "Invite the bot or join the support server.",help = "invite")
    async def invite(self,ctx):
        embed = discord.Embed(title = "Invite links",description = "Invite the bot",color = discord.Color.green())
        embed.add_field(name = 'Bot Invite',value = '[Bot Invite](https://discord.com/api/oauth2/authorize?client_id=830817370762248242&permissions=8&scope=bot)',inline = False)
        embed.add_field(name = 'Support Server',value = '[Server Invite](https://discord.com/invite/9pmGDc8pqQ)',inline = False)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)

def setup(client):
    client.add_cog(Status(client))

