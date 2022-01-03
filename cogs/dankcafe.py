import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button
import datetime
import math
import firebase_admin
from firebase_admin import db
import random
import asyncio

class DankCafe(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('DankCafe Cog Loaded.')

    async def cog_check(self, ctx):
        if ctx.guild.id == 798822518571925575 or ctx.guild.id == 870125583886065674:
            return True
        else:
            return False

    def mod_role_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            modroles = ref.child(str(ctx.message.guild.id)).child('mod').get()

            if modroles == None:
                return False
            for role in modroles:
                role_ob = ctx.message.guild.get_role(role)
                if role_ob in ctx.message.author.roles:
                    return True
            else:
                return False
        return commands.check(predicate)

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

    @commands.command(description = "Lock the view of a specified channel for everyone, or only a certain role.",help = "eviewlock <role>")
    @commands.has_role(825824551920467968)
    async def eviewlock(self,ctx, role : discord.Role = "all"):
        #await ctx.send('Attemping to unlock channel...')
        channel = ctx.channel

        if channel.id == 820538118360662037 or channel.id == 847886025006907482 or channel.id == 820538471977844757:
            if role == "all":
                role = ctx.guild.default_role
                
            serveraccess = ctx.guild.get_role(826841382973997127)
            overwrite = ctx.channel.overwrites_for(serveraccess)
            overwrite.view_channel = False
            await ctx.channel.set_permissions(serveraccess, overwrite=overwrite)

            overwrite = channel.overwrites_for(role)
            overwrite.view_channel = True
            await channel.set_permissions(role, overwrite=overwrite)
            embed=discord.Embed(description=f"**Channel View Locked**\nChannel View Locked for {role.mention} in {channel.mention}")
            await ctx.reply(embed = embed)
        else:
            await ctx.send("You can't use that command here")

    @commands.command(description = "Unlock the view of a specified channel for everyone, or only a certain role.",help = "eviewunlock <role>")
    @commands.has_role(825824551920467968)
    async def eviewunlock(self,ctx, role : discord.Role = "all"):
        #await ctx.send('Attemping to unlock channel...')
        channel = ctx.channel
        if channel.id == 820538118360662037 or channel.id == 847886025006907482 or channel.id == 820538471977844757:
            if role == "all":
                role = ctx.guild.default_role

            serveraccess = ctx.guild.get_role(826841382973997127)
            overwrite = ctx.channel.overwrites_for(serveraccess)
            overwrite.view_channel = True
            await ctx.channel.set_permissions(serveraccess, overwrite=overwrite)

            overwrite = channel.overwrites_for(role)
            overwrite.view_channel = None
            await channel.set_permissions(role, overwrite=overwrite)

            embed=discord.Embed(description=f"**Channel View Unlocked**\nChannel View Unlocked for {role.mention} in {channel.mention}")
            await ctx.reply(embed = embed)
        else:
            await ctx.send("You can't use that command here")

    @commands.command(aliases = ["dha"],description = "Add certain amount to someone dank hunt profile.",help = "dankhuntadd <count> <member>")
    @mod_role_check()
    async def dankhuntadd(self,ctx,count:int,member:discord.Member):
        if count <= 0:
            return await ctx.reply("How you planning to add negative entries you big brain.")
        ref = db.reference("/",app = firebase_admin._apps['lottery'])

        current = ref.child(str(ctx.guild.id)).child("dankhunt").child(str(member.id)).get() or 0

        ref.child(str(ctx.guild.id)).child("dankhunt").child(str(member.id)).set(int(current) + count)

        embed = discord.Embed(title = f"Entries Added!",description = f"Added `{count}` entries for {member}. They now have `{int(current) + count}` total entries in this dank hunt!", color = discord.Color.random())

        await ctx.reply(embed = embed)

    @commands.command(aliases = ["dhr"],description = "Remove certain amount to someone dank hunt profile.",help = "dankhuntremove <count> <member>")
    @mod_role_check()
    async def dankhuntremove(self,ctx,count:int,member:discord.Member):
        if count <= 0:
            return await ctx.reply("How you planning to remove negative entries you big brain.")
        ref = db.reference("/",app = firebase_admin._apps['lottery'])

        current = ref.child(str(ctx.guild.id)).child("dankhunt").child(str(member.id)).get() or 0

        ref.child(str(ctx.guild.id)).child("dankhunt").child(str(member.id)).set(int(current) - count)

        embed = discord.Embed(title = f"Entries Removed!",description = f"Removed `{count}` entries for {member}. They now have `{int(current) - count}` total entries in this dank hunt!", color = discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Dank Hunt',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)

    @commands.command(aliases = ["dhv"],description = "View yours or another member dank hunt current count.",help = "dankhuntview [member]")
    async def dankhuntview(self,ctx,member:discord.Member = None):
        member = member or ctx.author

        ref = db.reference("/",app = firebase_admin._apps['lottery'])

        current = ref.child(str(ctx.guild.id)).child("dankhunt").child(str(member.id)).get() or 0

        embed = discord.Embed(description = f"{member} dank hunt count: `{current}`", color = discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Dank Hunt',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)

    @commands.command(aliases = ["dhlb"],description = "View the top 10 on dank hunt leaderboard.",help = "dankhuntleaderboard")
    async def dankhuntleaderboard(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        log = ref.child(str(ctx.message.guild.id)).child("dankhunt").get()

        if log:
            users,log =  sorted(log, key=log.get, reverse=True) , log
        else:
            users,log = {},{}

        build = ""
        count = 1
        for user in users:
            amount = log[user]
            build += f"{count}. <@{user}>: `{amount}` finds\n"
            count += 1

            if count >= 11:
                break

        embed = discord.Embed(title = f"Leaderboard for {ctx.guild.name} dank hunt",description = build,color = discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Dank Hunt',icon_url = ctx.message.channel.guild.icon)

        await ctx.reply(embed = embed)

    
    @commands.command(description = "Add something to leaderboard",help = "lloga <user> <event>")
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

    @commands.command(description = "Remove something from leaderboard",help = "llogr <user> <event>")
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

    @commands.command(description = "Set someone log amount",help = "llogs <user> <event> <amount>")
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


    @commands.command(description = "Show event leaderboard for both event, mod only.",help = "llogl")
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


def setup(client):
    client.add_cog(DankCafe(client))