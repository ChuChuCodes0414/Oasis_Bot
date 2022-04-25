import discord
from discord.ext import commands
import datetime
import math
import firebase_admin
from firebase_admin import db
import random
import asyncio

class DankCafe(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.short = "<a:cafe:936457917400494141> | Custom for Cafe"
    @commands.Cog.listener()
    async def on_ready(self):
        print('DankCafe Cog Loaded.')

    async def cog_check(self, ctx):
        if ctx.guild.id == 798822518571925575 or ctx.guild.id == 870125583886065674:
            return True
        else:
            return False

    def eman_role_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            emanrole = ref.child(str(ctx.message.guild.id)).child('event').get()
            emanrole_ob = ctx.message.guild.get_role(emanrole)
            if emanrole_ob in ctx.message.author.roles:
                return True
            else:
                return False
        return commands.check(predicate)

    @commands.command(help ="Lock the view of a specified channel for everyone, or only a certain role.",brief = "This is the same as setting \"View Channel\" perms to false/red in a channel.")
    @commands.has_role(825824551920467968)
    async def eviewlock(self,ctx, role : discord.Role = "all"):
        channel = ctx.channel
        if channel.id == 820538118360662037 or channel.id == 847886025006907482 or channel.id == 820538471977844757:
            channel = channel or ctx.channel
            if role == "all":
                role = ctx.guild.default_role
            overwrite = channel.overwrites_for(role)
            if overwrite.view_channel == False:
                return await ctx.send(embed = discord.Embed(description = f"Channel {channel.mention} is already viewlocked for {role.mention}!\n\nNote: If someone with this role can still see the channel, it is likely they have another role/override that allows them to see the channel.",color = discord.Color.red()))
            overwrite.view_channel = False
            await channel.set_permissions(role, overwrite=overwrite)
            embed=discord.Embed(description=f"🔒 Channel {channel.mention} viewlocked for {role.mention}",color = discord.Color.green())
            embed.set_footer(text = "Run [prefix]viewunlock [role] [channel] to unlock it again!")
            await ctx.reply(embed = embed)
        else:
            await ctx.send("You can't use that command here!")
    
    @commands.command(help ="Set the view of a specified channel to neutral for everyone, or only a certain role.",brief = "This is the same as setting \"View Channel\" perms to neutral/gray in a channel.")
    @commands.has_role(825824551920467968)
    async def eviewneutral(self,ctx, role : discord.Role = "all"):
        channel = ctx.channel
        if channel.id == 820538118360662037 or channel.id == 847886025006907482 or channel.id == 820538471977844757:
            if role == "all":
                role = ctx.guild.default_role
            overwrite = channel.overwrites_for(role)
            if overwrite.view_channel == None:
                return await ctx.send(embed = discord.Embed(description = f"Channel {channel.mention} is already view set to neutral for {role.mention}!\n\nNote: If someone with this role cannot see the channel, it is likely they have another role/override that is set to red/deny.",color = discord.Color.red()))
            overwrite.view_channel = None
            await channel.set_permissions(role, overwrite=overwrite)
            embed=discord.Embed(description=f"Channel {channel.mention} view set to neutral for {role.mention}",color = discord.Color.green())
            embed.set_footer(text = "Run [prefix]viewlock [role] [channel] to lock it again!")
            await ctx.reply(embed = embed)
        else:
            await ctx.send("You can't use that command here!")

    @commands.command(help ="Unlock the view of a specified channel for everyone, or only a certain role.",brief = "This is the same as setting \"View Channel\" perms to true/green in a channel.")
    @commands.has_role(825824551920467968)
    async def eviewunlock(self,ctx, role : discord.Role = "all"):
        channel = ctx.channel
        if channel.id == 820538118360662037 or channel.id == 847886025006907482 or channel.id == 820538471977844757:
            if role == "all":
                role = ctx.guild.default_role
            overwrite = channel.overwrites_for(role)
            if overwrite.view_channel == True:
                return await ctx.send(embed = discord.Embed(description = f"Channel {channel.mention} is already viewunlocked for {role.mention}!",color = discord.Color.red()))
            overwrite.view_channel = True
            await channel.set_permissions(role, overwrite=overwrite)
            embed=discord.Embed(description=f"🔓 Channel {channel.mention} viewunocked for {role.mention}",color = discord.Color.red())
            embed.set_footer(text = "Run [prefix]viewlock [role] [channel] to lock it again!")
            await ctx.reply(embed = embed)
        else:
            await ctx.send("You can't use that command here!")
    
    @commands.command(help = "Add a win for someone to leaderboard")
    @eman_role_check()
    async def lloga(self,ctx,member:discord.Member,*,event):
        event = event.lower()

        if event not in ["rumble","tea"]:
            return await ctx.reply("Listen here, you got 2 options for events: `rumble` or `tea`.")
        
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child("dankcafe").child(event).child(str(member.id)).get() or 0

        ref.child("dankcafe").child(event).child(str(member.id)).set(int(log)+1)

        embed = discord.Embed(title = f"Wins Added!",description = f"Added win entry for {member} in {event}. They now have `{int(log) + 1}` wins logged for this event!", color = discord.Color.random())

        await ctx.reply(embed = embed)

    @commands.command(help = "Remove a win for someone from leaderboard")
    @eman_role_check()
    async def llogr(self,ctx,member:discord.Member,*,event):
        event = event.lower()

        if event not in ["rumble","tea"]:
            return await ctx.reply("Listen here, you got 2 options for events: `rumble` or `tea`.")
        
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child("dankcafe").child(event).child(str(member.id)).get() or 0

        if log == 0:
            return await ctx.reply("How you planning on removing something that does not exsist?")

        ref.child("dankcafe").child(event).child(str(member.id)).set(int(log)-1)

        embed = discord.Embed(title = f"Wins Removed!",description = f"Removed win entry for {member} in {event}. They now have `{int(log) - 1}` wins logged for this event!", color = discord.Color.random())

        await ctx.reply(embed = embed)

    @commands.command(help = "Set someone's win log amount")
    @eman_role_check()
    async def llogs(self,ctx,member:discord.Member,event,amount:int):
        event = event.lower()

        if event not in ["rumble","tea"]:
            return await ctx.reply("Listen here, you got 2 options for events: `rumble` or `tea`.")
        elif amount <= 0:
            return await ctx.reply("You need to set it to a positive amount of wins lol.")

        ref = db.reference("/",app = firebase_admin._apps['elead'])
        ref.child("dankcafe").child(event).child(str(member.id)).set(amount)

        embed = discord.Embed(title = f"Wins Set!",description = f"Set win entries for {member} in {event}. They now have `{amount}` wins logged for this event!", color = discord.Color.random())
        await ctx.reply(embed = embed)

    @commands.command(help = "Show event leaderboard for both events, mod only.")
    @eman_role_check()
    async def llogl(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child("dankcafe").child("rumble").get()

        if log:
            users,log =  sorted(log, key=log.get, reverse=True) , log
        else:
            users,log = {},{}

        build = ""
        count = 1
        page = 1
        pages = len(users)//30 
        if pages*30 != len(users):
            pages += 1
        place = 1
        for user in users[:30]:
            amount = log[user]
            build += f"{place}. <@{user}>: `{amount}` wins\n"
            count += 1
            place += 1

            
        embed = discord.Embed(title = f"Leaderboard for Rumble Royale",description = build,color = discord.Color.gold())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Leaderboard Logging | Page 1 of {pages}',icon_url = ctx.message.channel.guild.icon)
        await ctx.send(embed = embed)
        await asyncio.sleep(5)

        log = ref.child("dankcafe").child("tea").get()

        if log:
            users,log =  sorted(log, key=log.get, reverse=True) , log
        else:
            users,log = {},{}

        build = ""
        count = 1
        page = 1
        pages = len(users)//30 
        if pages*30 != len(users):
            pages += 1
        place = 1
        for user in users[:30]:
            amount = log[user]
            build += f"{place}. <@{user}>: `{amount}` wins\n"
            count += 1
            place += 1

        embed = discord.Embed(title = f"Leaderboard for Mudae Tea",description = build,color = discord.Color.gold())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Leaderboard Logging | Page 1 of {pages}',icon_url = ctx.message.channel.guild.icon)
        await ctx.send(embed = embed)
        await asyncio.sleep(1)
        page += 1
        count = 1
        build = ""

        await ctx.message.delete()


async def setup(client):
    await client.add_cog(DankCafe(client))