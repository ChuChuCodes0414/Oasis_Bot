import discord
from discord.ext import commands
import datetime
import firebase_admin
from firebase_admin import db
import asyncio

class Dev(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Dev Cog Loaded.')
    
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author == self.client.user:
            return
        if message.guild: # message is not DM
            mention = f'<@{self.client.user.id}>'
            if mention == message.content:
                if self.client.serenity:
                    ref = db.reference("/",app = firebase_admin._apps['settings'])
                    prefix = (ref.child(str(message.guild.id)).child('sprefix').get())
                else:
                    ref = db.reference("/",app = firebase_admin._apps['settings'])
                    prefix = (ref.child(str(message.guild.id)).child('prefix').get())
                if prefix:
                    embed = discord.Embed(title="Hello!",description=f"The prefix in this server is: `{prefix}`", color=discord.Color.green())
                else:
                    embed = discord.Embed(title="Hello!",description=f"It seems like this server is not set up! Run `@Oasis Bot setup` or `@Serenity Bot setup` to get started.", color=discord.Color.green())
                await message.reply(embed =embed)
            elif message.content == mention + " setup":
                ref = db.reference("/",app = firebase_admin._apps['settings'])
                if not ref.child(str(message.guild.id)).get():
                    serverconf = {'dj': None, 'event': None, 'giveaway': None, 'mod': [None], 'modtrack': [None], 'pchannels': [None], 'prefix': 'o!','sprefix':'s!'}
                    ref.child(str(message.guild.id)).set(serverconf)
                    embed = discord.Embed(title="All set up!",description=f"You are all set up! The default prefix is `o!` for Oasis Bot and `s!` for Serenity Bot!", color=discord.Color.green())
                else:
                    embed = discord.Embed(title="Uh oh",description=f"It looks like this server is already set up!", color=discord.Color.green())
                await message.reply(embed =embed)
        else:
            await message.reply("Commands are not allowed in dms!")

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        if ref.child(str(guild.id)).get():
            pass
        else:
            serverconf = {'prefix': 'o!','sprefix':'s!'}
            ref.child(str(guild.id)).set(serverconf)

        channel = self.client.get_channel(int(849761988628316191))

        embed = discord.Embed(title = f'Joined {guild.name}',description = f'ID: {guild.id}',color = discord.Color.green())
        embed.set_thumbnail(url = guild.icon)

        embed.add_field(name = "Server Owner",value = f'{guild.owner} (ID: {guild.owner.id})',inline = True)

        humans = len([m for m in guild.members if not m.bot])
        bots = guild.member_count-humans
        embed.add_field(name = "Member Count",value = f'Total Members: {guild.member_count}\nHuman Members: {humans}\nBots: {bots}\nPercentage: {round(bots/guild.member_count,1)}%',inline = True)

        embed.add_field(name = "Creation Date",value = guild.created_at.strftime("%Y-%m-%d %H:%M"),inline = True)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'Oasis Bot Dev Logging',icon_url = channel.guild.icon)
        await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        channel = self.client.get_channel(int(849761988628316191))

        embed = discord.Embed(title = f'Removed from {guild.name}',description = f'ID: {guild.id}',color = discord.Color.red())
        embed.set_thumbnail(url = guild.icon)

        embed.add_field(name = "Server Owner",value = f'{guild.owner} (ID: {guild.owner.id})',inline = True)

        humans = len([m for m in guild.members if not m.bot])
        bots = guild.member_count-humans
        embed.add_field(name = "Member Count",value = f'Total Members: {guild.member_count}\nHuman Members: {humans}\nBots: {bots}\nPercentage: {round(bots/guild.member_count,1)}%',inline = True)

        embed.add_field(name = "Creation Date",value = guild.created_at.strftime("%Y-%m-%d %H:%M"),inline = True)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'Oasis Bot Dev Logging',icon_url = channel.guild.icon)
        await channel.send(embed = embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self,ctx):
        print("shutdown")
        try:
            await ctx.reply(f'Shutting down')
            await self.client.logout()
        except:
            self.client.clear()
    @shutdown.error
    async def shutdown_error(self,ctx, error):
        await ctx.reply(f'There was an error running this command: \n`{error}`')    

    @commands.command(name = "reload",hidden=True)
    @commands.is_owner()
    async def reload(self,ctx,extention):
        await self.client.unload_extension(f'cogs.{extention}')
        await self.client.load_extension(f'cogs.{extention}')
        await ctx.reply(f'Reloaded {extention} sucessfully')
    @reload.error
    async def reload_error(self,ctx, error):
        await ctx.reply(f'There was an error running this command: \n`{error}`')

        # Loading Cogs
    @commands.command(name = "load",hidden=True)
    @commands.is_owner()
    async def load(self,ctx,extention):
        await self.client.load_extension(f'cogs.{extention}')
        await ctx.reply(f'Loaded {extention} sucessfully')
    @load.error
    async def load_error(self,ctx, error):
        await ctx.reply(f'There was an error running this command: \n`{error}`')        

    @commands.command(name = "unload",hidden=True)
    @commands.is_owner()
    async def unload(self,ctx,extention):
        await self.client.unload_extension(f'cogs.{extention}')
        await ctx.reply(f'Unloaded {extention} sucessfully')
    @unload.error
    async def unload_error(self,ctx, error):
        await ctx.reply(f'There was an error running this command: \n`{error}`')    

    @commands.command(name = "globaldisable",hidden = True)
    @commands.is_owner()
    async def ownerdisable(self,ctx,command):
        command = self.client.get_command(command) 

        if not command:
            return await ctx.reply("That does not seem like a valid command.")   
        
        if not command.enabled:
            return await ctx.reply("How are you planning to disable something that is disabled??")
        
        command.enabled = False

        await ctx.reply(f"Command `{command.name}` disabled!")
    
    @commands.command(name = "globalenable",hidden = True)
    @commands.is_owner()
    async def ownerenable(self,ctx,command):
        command = self.client.get_command(command) 

        if not command:
            return await ctx.reply("That does not seem like a valid command.")   
        
        if command.enabled:
            return await ctx.reply("How are you planning to enable something that is enabled??")
        
        command.enabled = True

        await ctx.reply(f"Command `{command.name}` enabled!")


    @commands.command(hidden = True)
    @commands.is_owner()
    async def botcheck(self,ctx):
        apiping = round(self.client.latency*1000)
        status = f"API Ping: `{apiping}ms`\n"
        embed = discord.Embed(title = "Checking Bot Status <a:OB_Loading:907101653692456991>",description = status,color = discord.Color.random())
        embed.set_footer(text = "Checking Real Ping...")
        message = await ctx.reply(embed = embed)
        latency = ctx.message.created_at - message.created_at
        status += f"Read Ping: `{latency.microseconds*0.001}ms`\n"
        embed = discord.Embed(title = "Checking Bot Status <a:OB_Loading:907101653692456991>",description = status,color = discord.Color.random())

        databases = {"elead":"Event","modlogs":"Mod Logs","pepegabot":"Private Channels","modtracking":"Mod Tracking","settings":"Settings","giveaways":"Giveaway Donation","glogging":"Giveaway Logging","freeloader":"Freeloader","profile":"Profile","invites":"Invites","lottery":"Lottery"}

        for database,name in databases.items():
            embed.add_field(name = f"{name} Database",value = f"Upload: <a:OB_Loading:907101653692456991>\nDownload: <a:OB_Loading:907101653692456991>\nDelete: <a:OB_Loading:907101653692456991>")
            embed.set_footer(text = f"Checking {name} Database...")
            await message.edit(embed = embed)

            ref = db.reference("/",app = firebase_admin._apps[database])
            try:
                ref.child("test").set("test")
                set1 = "<a:PB_greentick:865758752379240448>"
            except:
                set1 = "<a:PB_redtick:873384525202350090>"
            await asyncio.sleep(2)
            embed.remove_field(-1)
            embed.add_field(name = f"{name} Database",value = f"Upload: {set1}\nDownload: <a:OB_Loading:907101653692456991>\nDelete: <a:OB_Loading:907101653692456991>")
            await message.edit(embed = embed)
            try:
                value = ref.child("test").get()
                get1 = "<a:PB_greentick:865758752379240448>"
            except:
                get1 = "<a:PB_redtick:873384525202350090>"
            await asyncio.sleep(2)
            embed.remove_field(-1)
            embed.add_field(name = f"{name} Database",value = f"Upload: {set1}\nDownload: {get1}\nDelete: <a:OB_Loading:907101653692456991>")
            await message.edit(embed = embed)
            try:
                ref.child("test").delete()
                delete1 = "<a:PB_greentick:865758752379240448>"
            except:
                delete1 = "<a:PB_redtick:873384525202350090>"
            await asyncio.sleep(2)
            embed.remove_field(-1)
            embed.add_field(name = f"{name} Database",value = f"Upload: {set1}\nDownload: {get1}\nDelete: {delete1}")
            await message.edit(embed = embed)
        embed.title = "Check Complete!"
        embed.set_footer(text = None)
        await message.edit(embed = embed)
    


async def setup(client):
    await client.add_cog(Dev(client))