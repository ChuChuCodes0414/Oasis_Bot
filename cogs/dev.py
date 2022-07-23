import discord
from discord.ext import commands, tasks
import datetime
import firebase_admin
from firebase_admin import db
import asyncio
from utils import timing

class Dev(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.commands = {}
        self.users = {}
        self.guilds = {}
        self.post_recap.start()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Dev Cog Loaded.')

    @tasks.loop(hours=24,reconnect = True)
    async def post_recap(self):
        sortedcomm = sorted(self.commands, key=self.commands.get, reverse=True)
        commres = ""
        x = min(len(self.commands),10)
        for command in sortedcomm[:x]:
            commres += f"**{command}:** {self.commands[command]} uses\n"
        sortedusers = sorted(self.users, key=self.users.get, reverse=True)
        userres = ""
        x = min(len(self.users),10)
        for user in sortedusers[:x]:
            userres += f"**{user}:** {self.users[user]} commands\n"
        sortedguilds = sorted(self.guilds,key = self.guilds.get,reverse = True)
        guildsres = ""
        x = min(len(self.guilds),10)
        for guild in sortedguilds[:x]:
            guildsres += f"**{guild.name}** {self.guilds[guild]} commands\n"
        now = discord.utils.utcnow()
        unix = int(now.replace(tzinfo=datetime.timezone.utc).timestamp())
        embed = discord.Embed(title = "Daily Command Recap",description = f"<t:{unix}:F>\nUnique Commands: {len(self.commands)} | Total Users: {len(self.users)} | Total Guilds: {len(self.guilds)}")
        embed.add_field(name = "Commands",value = commres or "None")
        embed.add_field(name = "Users",value = userres or "None")
        embed.add_field(name = "Guilds",value = guildsres or "None")
        channel = self.client.get_channel(int(977037266172137505))
        await channel.send(embed = embed)
        self.commands,self.users,self.guilds = {},{},{}
    
    @post_recap.before_loop
    async def before_recap(self):
        await self.client.wait_until_ready()

    def cog_unload(self):
        self.some_task.cancel()

    async def log_blacklist(self,user,reason,mod = None,until = None):
        if until:
            embed = discord.Embed(title = "Logging User Blacklist",description = f"Blacklisted until <t:{until}:f> (<t:{until}:R>)")
            embed.add_field(name = "User",value = f"<@{user}> (`{user}`)",inline = False)
            embed.add_field(name = "Reason",value = reason,inline = False)
            embed.add_field(name = "Action Taken By",value = f"<@{mod}> (`{mod}`)")
            embed.timestamp = datetime.datetime.now()
        else:
            embed = discord.Embed(title = "Logging User Unblacklist")
            embed.add_field(name = "User",value = f"<@{user}> (`{user}`)",inline = False)
            embed.add_field(name = "Reason",value = reason,inline = False)
            if mod:
                embed.add_field(name = "Action Taken By",value = f"<@{mod}> (`{mod}`)")
            else:
                embed.add_field(name = "Action Taken By",value = f"Automatically")
            embed.timestamp = datetime.datetime.now()
        channel = self.client.get_channel(int(978029124243292210))
        await channel.send(embed = embed)
    
    @commands.Cog.listener()
    async def on_command_completion(self,ctx):
        self.commands[ctx.command.name] = self.commands.get(ctx.command.name,0) + 1
        self.users[ctx.author] = self.users.get(ctx.author,0) + 1
        self.guilds[ctx.guild] = self.guilds.get(ctx.guild,0) + 1
    
    @commands.Cog.listener()
    async def on_command(self,ctx):
        if self.client.maintenance and ctx.author.id != 570013288977530880:
            embed = discord.Embed(title = "⚠ The bot is currently in maintenance!",description = f"Please refrain from running commands at this time. Information can be found in the [support server](https://discord.com/invite/9pmGDc8pqQ).",color = discord.Color.yellow())
            embed.timestamp = discord.utils.utcnow()
            await ctx.reply(embed = embed)
        ref1 = db.reference("/",app = firebase_admin._apps['profile'])
        bl = ref1.child(str(ctx.author.id)).child("blacklist").get()
        if bl:
            now = int(discord.utils.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()) 
            if now < bl['until']:
                embed = discord.Embed(title = "⚠ You are currently bot blacklisted!",description = f"You have been blacklisted until <t:{bl['until']}:f> (<t:{bl['until']}:R>)",color = discord.Color.red())
                embed.add_field(name = "Reason",value = bl.get("reason","None given"),inline = False)
                embed.add_field(name = "Appealing",value = "You can appeal this blacklist in the support channel in the [support server](https://discord.com/invite/9pmGDc8pqQ)")
                await ctx.reply(embed = embed)
            else:
                ref1.child(str(ctx.author.id)).child("blacklist").delete()
                embed = discord.Embed(title = "Your bot blacklist is now over!",description = f"You have been automatically unblacklisted. Please be sure to follow the rules carefully! Repeated blacklists may result in your permanent ban from the bot.",color = discord.Color.green())
                await ctx.reply(embed = embed)
                await self.log_blacklist(ctx.author.id,reason = "Automatic Unblacklist")
    
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author == self.client.user:
            return
        if message.guild: # message is not DM
            mention = f'<@{self.client.user.id}>'
            if mention == message.content:
                if self.client.beta:
                    prefix = ","
                else:
                    ref = db.reference("/",app = firebase_admin._apps['settings'])
                    prefix = (ref.child(str(message.guild.id)).child('prefix').get())
                if prefix:
                    embed = discord.Embed(title="Hello!",description=f"The prefix in this server is: `{prefix}`", color=discord.Color.green())
                else:
                    embed = discord.Embed(title="Hello!",description=f"It seems like this server is not set up! Run `@Oasis Bot setup` to get started.", color=discord.Color.green())
                await message.reply(embed =embed)
            elif message.content == mention + " setup":
                ref = db.reference("/",app = firebase_admin._apps['settings'])
                if not ref.child(str(message.guild.id)).get():
                    serverconf = {'dj': None, 'event': None, 'giveaway': None, 'mod': [None], 'modtrack': [None], 'pchannels': [None], 'prefix': 'o!','sprefix':'s!'}
                    ref.child(str(message.guild.id)).set(serverconf)
                    embed = discord.Embed(title="All set up!",description=f"You are all set up! The default prefix is `o!` for Oasis Bot.", color=discord.Color.green())
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

    @commands.command(hidden = True)
    @commands.is_owner()
    async def recap(self,ctx):
        sortedcomm = sorted(self.commands, key=self.commands.get, reverse=True)
        commres = ""
        x = min(len(self.commands),10)
        for command in sortedcomm[:x]:
            commres += f"**{command}:** {self.commands[command]} uses\n"
        sortedusers = sorted(self.users, key=self.users.get, reverse=True)
        userres = ""
        x = min(len(self.users),10)
        for user in sortedusers[:x]:
            userres += f"**{user}:** {self.users[user]} commands\n"
        sortedguilds = sorted(self.guilds,key = self.guilds.get,reverse = True)
        guildsres = ""
        x = min(len(self.guilds),10)
        for guild in sortedguilds[:x]:
            guildsres += f"**{guild.name}** {self.guilds[guild]} commands\n"
        now = discord.utils.utcnow()
        unix = int(now.replace(tzinfo=datetime.timezone.utc).timestamp())
        embed = discord.Embed(title = "Daily Command Recap",description = f"<t:{unix}:F>\nUnique Commands: {len(self.commands)} | Total Users: {len(self.users)} | Total Guilds: {len(self.guilds)}")
        embed.add_field(name = "Commands",value = commres or "None")
        embed.add_field(name = "Users",value = userres or "None")
        embed.add_field(name = "Guilds",value = guildsres or "None")
        await ctx.reply(embed = embed)

    @commands.command(hidden = True)
    @commands.is_owner()
    async def blacklist(self,ctx,time:str,user:discord.User,*,reason = None):
        time = timing.timeparse(time)
        if isinstance(time,str):
            return await ctx.reply(embed = discord.Embed(description  = time,color = discord.Color.red()))
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        if ref.child(str(user.id)).child("blacklist").get():
            return await ctx.reply(embed = discord.Embed(description = "This user is already blacklisted!",color = discord.Color.red()))
        until = discord.utils.utcnow() + time
        unix = int(until.replace(tzinfo=datetime.timezone.utc).timestamp())
        ref.child(str(user.id)).child("blacklist").set({"until":unix,"reason":reason or "None"})
        try:
            dm = user.dm_channel
            if dm == None:
                dm = await user.create_dm()
            embed = discord.Embed(title = "You have been bot blacklisted!",description = f"You have been blacklisted until <t:{unix}:f> (<t:{unix}:R>)")
            embed.add_field(name = "Reason",value = reason or "None",inline = False)
            embed.add_field(name = "Appealing",value = "You can appeal this blacklist in the support channel in the [support server](https://discord.com/invite/9pmGDc8pqQ)")
            await dm.send(embed = embed)
            embed = discord.Embed(title = "User Blacklisted!",description = f"Blacklisted {user.mention} (`{user.id}`) until <t:{unix}:f> (<t:{unix}:R>)\n\nReason: {reason}")
            await ctx.reply(embed = embed)
        except:
            await ctx.reply(title = "User Blacklisted!",description = f"Blacklisted {user.mention} (`{user.id}`) until <t:{unix}:f> (<t:{unix}:R>)\n\nReason: {reason}\n\nI could not dm the user!")
        await self.log_blacklist(user.id,reason or "None Given",ctx.author.id,unix)
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def unblacklist(self,ctx,user:discord.User,*,reason = None):
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        if not ref.child(str(user.id)).child("blacklist").get():
            return await ctx.reply(embed = discord.Embed(description = "This user is not blacklisted!",color = discord.Color.red()))
        ref.child(str(user.id)).child("blacklist").delete()
        try:
            dm = user.dm_channel
            if dm == None:
                dm = await user.create_dm()
            embed = discord.Embed(title = "You have been bot unblacklisted!",description = f"You have been unblacklisted! Please be sure to take careful note of bot rules.")
            embed.add_field(name = "Reason",value = reason or "None",inline = False)
            await dm.send(embed = embed)
            embed = discord.Embed(title = "User Unblacklisted!",description = f"Unlacklisted {user.mention} (`{user.id}`)\n\nReason: {reason}")
            await ctx.reply(embed = embed)
        except:
            await ctx.reply(title = "User Blacklisted!",description = f"Unblacklisted {user.mention} (`{user.id}`)\n\nReason: {reason}\n\nI could not dm the user!")
        await self.log_blacklist(user.id,reason or "None Given",ctx.author.id)
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def sync(self,ctx):
        response = await self.client.tree.sync()
        await ctx.reply("Synced")
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def syncguild(self,ctx):
        guild = self.client.get_guild(870125583886065674)
        response = await self.client.tree.sync(guild = guild)
        await ctx.reply("Synced")

    @commands.command(hidden = True)
    @commands.is_owner()
    async def maintenance(self,ctx,option:str):
        if option == "on":
            self.client.maintenance = True
            await ctx.reply("maintenance on!")
        else:
            self.client.maintenance = False
            await ctx.reply("maintenance off!")

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