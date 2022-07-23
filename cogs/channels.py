import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import db
import asyncio
import datetime
from utils import timing
class Channels(commands.Cog):
    """
        Channel management, with various commands. Most of these commands require manage permissions perms.
    """
    def __init__(self,client):
        self.client = client
        self.short = "💬 | Channel Management"
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Channels Cog Loaded.')
    
    @commands.command(aliases = ['ld'],help = "Lockdown the server based on the channels that you have added.")
    @commands.has_guild_permissions(manage_permissions = True)
    @commands.cooldown(1, 20,commands.BucketType.user)
    async def lockdown(self,ctx,*,text:str = None):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        if ref.child(str(ctx.guild.id)).child("lockdown").get():
            return await ctx.reply(embed = discord.Embed(description = "This server is already locked!",color = discord.Color.red()))
        channels = roleid = ref.child(str(ctx.guild.id)).child("lchannels").get()
        if not channels:
            return await ctx.reply(embed = discord.Embed(description = "You have no lockdown channels setup!",color = discord.Color.red()))
        roleid = ref.child(str(ctx.guild.id)).child("drole").get() or None
        if roleid:
            try:
                role = await commands.converter.RoleConverter().convert(ctx,str(roleid))
            except:
                return await ctx.reply(embed = discord.Embed(description = "I could not find the role you setup!"))
        else:
            role = ctx.guild.default_role
        error = []
        view = ConfirmationView(ctx)
        message = await ctx.reply(embed = discord.Embed(description = f"Are you sure you want to lockdown {len(channels)} channels for {role.mention}?",color = discord.Color.random()),view = view)
        view.message = message
        result = await view.wait()
        for child in view.children:
            child.disabled = True
        await message.edit(view = view)
        if result:
            return await message.reply(embed = discord.Embed(description = "Request timed out! Cancelling lockdown...",color = discord.Color.red()))
        if not view.value:
            return await message.reply(embed = discord.Embed(description = "Alright then, as you wish. Cancelling lockdown...",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = f"Locking {len(channels)} channels for {role.mention}\nETA: `{len(channels)*0.3}` seconds",color = discord.Color.yellow()))
        text = text or ref.child(str(ctx.guild.id)).child("lmessage").get() or "This server has been locked down!"
        async with ctx.typing():
            embed = discord.Embed(title = "Server Lockdown",description = text,color = discord.Color.red())
            embed.timestamp = discord.utils.utcnow()
            for channel in channels:
                try:
                    channel = await commands.converter.TextChannelConverter().convert(ctx,str(channel))
                    overwrite = channel.overwrites_for(role)
                    overwrite.send_messages = False
                    await channel.set_permissions(role, overwrite=overwrite)
                    await channel.send(embed = embed)
                    await asyncio.sleep(0.3)
                except:
                    error.append(channel)
        if len(error) >= 1:
            des = "\n".join([x for x in error])
            embed = discord.Embed(title = "Server Locked Down",description = f"Could not lock:\n{error}",color = discord.Color.green())
        else:
            embed = discord.Embed(title = "Server Locked Down",description = f"All channels successfully locked!",color = discord.Color.green())
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text = "Run [prefix]unlockdown to unlock!")
        ref.child(str(ctx.guild.id)).child("lockdown").set(True)
        await message.reply(embed = embed)
    
    @commands.command(aliases = ['uld'],help = "End the lockdown on the server based on the channels that you have added.")
    @commands.has_guild_permissions(manage_permissions = True)
    @commands.cooldown(1, 20,commands.BucketType.user)
    async def unlockdown(self,ctx,*,text:str = None):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        if not ref.child(str(ctx.guild.id)).child("lockdown").get():
            return await ctx.reply(embed = discord.Embed(description = "This server is not locked down!",color = discord.Color.red()))
        channels = roleid = ref.child(str(ctx.guild.id)).child("lchannels").get()
        if not channels:
            return await ctx.reply(embed = discord.Embed(description = "You have no lockdown channels setup!",color = discord.Color.red()))
        roleid = ref.child(str(ctx.guild.id)).child("drole").get() or None
        if roleid:
            try:
                role = await commands.converter.RoleConverter().convert(ctx,str(roleid))
            except:
                return await ctx.reply(embed = discord.Embed(description = "I could not find the role you setup!"))
        else:
            role = ctx.guild.default_role
        error = []
        view = ConfirmationView(ctx)
        message = await ctx.reply(embed = discord.Embed(description = f"Are you sure you want to unlockdown {len(channels)} channels for {role.mention}?",color = discord.Color.random()),view = view)
        view.message = message
        result = await view.wait()
        for child in view.children:
            child.disabled = True
        await message.edit(view = view)
        if result:
            return await message.reply(embed = discord.Embed(description = "Request timed out! Cancelling unlockdown...",color = discord.Color.red()))
        if not view.value:
            return await message.reply(embed = discord.Embed(description = "Alright then, as you wish. Cancelling unlockdown...",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = f"Unlocking {len(channels)} channels for {role.mention}\nETA: `{len(channels)*0.3}` seconds",color = discord.Color.yellow()))
        text = text or ref.child(str(ctx.guild.id)).child("ulmessage").get() or "This server has been unlocked!"
        async with ctx.typing():
            embed = discord.Embed(title = "Server Unlocked",description = text,color = discord.Color.green())
            embed.timestamp = discord.utils.utcnow()
            for channel in channels:
                try:
                    channel = await commands.converter.TextChannelConverter().convert(ctx,str(channel))
                    overwrite = channel.overwrites_for(role)
                    overwrite.send_messages = None
                    await channel.set_permissions(role, overwrite=overwrite)
                    await channel.send(embed = embed)
                    await asyncio.sleep(0.3)
                except:
                    error.append(channel)
        if len(error) >= 1:
            des = "\n".join([x for x in error])
            embed = discord.Embed(title = "Server Unlocked",description = f"Could not unlock:\n{error}",color = discord.Color.green())
        else:
            embed = discord.Embed(title = "Server Unlocked",description = f"All channels successfully unlocked!",color = discord.Color.green())
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text = "Run [prefix]unlockdown to unlock!")
        ref.child(str(ctx.guild.id)).child("lockdown").set(False)
        await message.reply(embed = embed)
    
    @commands.command(aliases = ['vld'],help = "View lockdown the server based on the channels that you have added.",brief = "Removes view access to channels for the role you setup.")
    @commands.has_guild_permissions(manage_permissions = True)
    @commands.cooldown(1, 20,commands.BucketType.user)
    async def viewlockdown(self,ctx,*,text:str = None):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        if ref.child(str(ctx.guild.id)).child("vlockdown").get():
            return await ctx.reply(embed = discord.Embed(description = "This server is already view locked!",color = discord.Color.red()))
        channels = roleid = ref.child(str(ctx.guild.id)).child("lchannels").get()
        if not channels:
            return await ctx.reply(embed = discord.Embed(description = "You have no lockdown channels setup!",color = discord.Color.red()))
        roleid = ref.child(str(ctx.guild.id)).child("drole").get() or None
        if roleid:
            try:
                role = await commands.converter.RoleConverter().convert(ctx,str(roleid))
            except:
                return await ctx.reply(embed = discord.Embed(description = "I could not find the role you setup!"))
        else:
            role = ctx.guild.default_role
        error = []
        view = ConfirmationView(ctx)
        message = await ctx.reply(embed = discord.Embed(description = f"Are you sure you want to view lockdown {len(channels)} channels for {role.mention}?",color = discord.Color.random()),view = view)
        view.message = message
        result = await view.wait()
        for child in view.children:
            child.disabled = True
        await message.edit(view = view)
        if result:
            return await message.reply(embed = discord.Embed(description = "Request timed out! Cancelling view lockdown...",color = discord.Color.red()))
        if not view.value:
            return await message.reply(embed = discord.Embed(description = "Alright then, as you wish. Cancelling view lockdown...",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = f"Locking {len(channels)} channels for {role.mention}\nETA: `{len(channels)*0.5}` seconds",color = discord.Color.yellow()))
        text = text or ref.child(str(ctx.guild.id)).child("lmessage").get() or "This server has been locked down!"
        async with ctx.typing():
            embed = discord.Embed(title = "View Server Lockdown",description = text,color = discord.Color.red())
            embed.timestamp = discord.utils.utcnow()
            for channel in channels:
                try:
                    channel = await commands.converter.TextChannelConverter().convert(ctx,str(channel))
                    overwrite = channel.overwrites_for(role)
                    overwrite.view_channel = False
                    await channel.set_permissions(role, overwrite=overwrite)
                    await channel.send(embed = embed)
                    await asyncio.sleep(0.5)
                except:
                    error.append(channel)
        if len(error) >= 1:
            des = "\n".join([x.mention for x in error])
            embed = discord.Embed(title = "Server View Locked Down",description = f"Could not lock:\n{error}",color = discord.Color.green())
        else:
            embed = discord.Embed(title = "Server View Locked Down",description = f"All channels successfully locked!",color = discord.Color.green())
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text = "Run [prefix]viewunlockdown to unlock!")
        ref.child(str(ctx.guild.id)).child("vlockdown").set(True)
        await message.reply(embed = embed)
    
    @commands.command(aliases = ['vuld'],help = "Remove the view lockdown the server based on the channels that you have added.",brief = "Allows view access to channels for the role you setup.")
    @commands.has_guild_permissions(manage_permissions = True)
    @commands.cooldown(1, 20,commands.BucketType.user)
    async def viewunlockdown(self,ctx,*,text:str = None):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        if not ref.child(str(ctx.guild.id)).child("vlockdown").get():
            return await ctx.reply(embed = discord.Embed(description = "This server is not view locked!",color = discord.Color.red()))
        channels = roleid = ref.child(str(ctx.guild.id)).child("lchannels").get()
        if not channels:
            return await ctx.reply(embed = discord.Embed(description = "You have no lockdown channels setup!",color = discord.Color.red()))
        roleid = ref.child(str(ctx.guild.id)).child("drole").get() or None
        if roleid:
            try:
                role = await commands.converter.RoleConverter().convert(ctx,str(roleid))
            except:
                return await ctx.reply(embed = discord.Embed(description = "I could not find the role you setup!"))
        else:
            role = ctx.guild.default_role
        error = []
        view = ConfirmationView(ctx)
        message = await ctx.reply(embed = discord.Embed(description = f"Are you sure you want to view unlockdown {len(channels)} channels for {role.mention}?",color = discord.Color.random()),view = view)
        view.message = message
        result = await view.wait()
        for child in view.children:
            child.disabled = True
        await message.edit(view = view)
        if result:
            return await message.reply(embed = discord.Embed(description = "Request timed out! Cancelling view unlockdown...",color = discord.Color.red()))
        if not view.value:
            return await message.reply(embed = discord.Embed(description = "Alright then, as you wish. Cancelling view unlockdown...",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = f"Unlocking {len(channels)} channels for {role.mention}\nETA: `{len(channels)*0.5}` seconds",color = discord.Color.yellow()))
        text = text or ref.child(str(ctx.guild.id)).child("ulmessage").get() or "This server has been view unlocked!"
        async with ctx.typing():
            embed = discord.Embed(title = "View Server Unlockdown",description = text,color = discord.Color.green())
            embed.timestamp = discord.utils.utcnow()
            for channel in channels:
                try:
                    channel = await commands.converter.TextChannelConverter().convert(ctx,str(channel))
                    overwrite = channel.overwrites_for(role)
                    overwrite.view_channel = None
                    await channel.set_permissions(role, overwrite=overwrite)
                    await channel.send(embed = embed)
                    await asyncio.sleep(0.5)
                except:
                    error.append(channel)
        if len(error) >= 1:
            des = "\n".join([x.mention for x in error])
            embed = discord.Embed(title = "Server View Unlocked",description = f"Could not view unlock:\n{error}",color = discord.Color.green())
        else:
            embed = discord.Embed(title = "Server View Unlocked",description = f"All channels successfully view unlocked!",color = discord.Color.green())
        embed.set_footer(text = "Run [prefix]viewunlockdown to unlock!")
        embed.timestamp = discord.utils.utcnow()
        ref.child(str(ctx.guild.id)).child("vlockdown").set(False)
        await message.reply(embed = embed)

    @commands.command(aliases = ['l'],help ="Lock a specified channel for everyone, or only a certain role.")
    @commands.has_guild_permissions(manage_permissions= True)
    async def lock(self,ctx, role : discord.Role = "all",channel : discord.TextChannel=None):
        channel = channel or ctx.channel
        if role == "all":
            role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        if overwrite.send_messages == False:
            return await ctx.send(embed = discord.Embed(description = f"Channel {channel.mention} is already locked for {role.mention}!",color = discord.Color.red()))
        overwrite.send_messages = False
        await channel.set_permissions(role, overwrite=overwrite)
        embed = discord.Embed(description = f"🔒 Channel {channel.mention} locked for {role.mention}",color = discord.Color.green())
        embed.set_footer(text = "Run [prefix]unlock [role] [channel] to unlock it again!")
        await ctx.reply(embed = embed)

    @commands.command(aliases = ['nu'],help ="Set speaking perms for a role in a channel to neutral.")
    @commands.has_guild_permissions(manage_permissions= True)
    async def neutral(self,ctx, role : discord.Role = "all",channel : discord.TextChannel=None):
        channel = channel or ctx.channel
        if role == "all":
            role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        if overwrite.send_messages == None:
            return await ctx.send(embed = discord.Embed(description = f"Channel {channel.mention} is already set to neutral for {role.mention}!",color = discord.Color.red()))
        overwrite.send_messages = None
        await channel.set_permissions(role, overwrite=overwrite)
        embed = discord.Embed(description = f"🔒 Channel {channel.mention} set to neutral {role.mention}",color = discord.Color.green())
        embed.set_footer(text = "Run [prefix]lock [role] [channel] to lock it again!")
        await ctx.reply(embed = embed)
    
    @commands.command(aliases = ['ul'],help ="Unlock a specified channel for everyone, or only a certain role.")
    @commands.has_guild_permissions(manage_permissions= True)
    async def unlock(self,ctx, role : discord.Role = "all",channel : discord.TextChannel=None):
        channel = channel or ctx.channel
        if role == "all":
            role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        if overwrite.send_messages == True:
            return await ctx.send(embed = discord.Embed(description = f"Channel {channel.mention} is already unlocked for {role.mention}!",color = discord.Color.red()))
        overwrite.send_messages = True
        await channel.set_permissions(role, overwrite=overwrite)
        embed = discord.Embed(description = f"🔓 Channel {channel.mention} unlocked for {role.mention}",color = discord.Color.green())
        embed.set_footer(text = "Run [prefix]lock [role] [channel] to lock it again!")
        await ctx.reply(embed = embed)

    @commands.command(help ="Lock the view of a specified channel for everyone, or only a certain role.",brief = "This is the same as setting \"View Channel\" perms to false/red in a channel.")
    @commands.has_permissions(manage_permissions= True)
    async def viewlock(self,ctx, role : discord.Role = "all",channel : discord.TextChannel=None):
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

    @commands.command(help ="Set the view of a specified channel to neutral for everyone, or only a certain role.",brief = "This is the same as setting \"View Channel\" perms to neutral/gray in a channel.")
    @commands.has_permissions(manage_permissions= True)
    async def viewneutral(self,ctx, role : discord.Role = "all",channel : discord.TextChannel=None):
        channel = channel or ctx.channel
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

    @commands.command(help ="Unlock the view of a specified channel for everyone, or only a certain role.",brief = "This is the same as setting \"View Channel\" perms to true/green in a channel.")
    @commands.has_permissions(manage_permissions= True)
    async def viewunlock(self,ctx, role : discord.Role = "all",channel : discord.TextChannel=None):
        channel = channel or ctx.channel
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

    @commands.command(help ="Start a dank member bot heist that has a requirement with channel management."
    ,brief = "This command will lock the view of the channel for the default role (can be set up in settings) and allow the specified role requirement to view the channel. You can specify if the heist is long (over 10mil) or short (under 10mil), if you do not specify default is short. At the end of heist, channel will be visible to default role you specify again.")
    @commands.has_permissions(manage_permissions= True)
    async def dankheist(self,ctx,role:discord.Role,length = "short"):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        if length == "short":
            length = 1.5
        elif length == "long":
            length = 4
        else:
            return await ctx.reply("Hey, the heist is either 'short' or 'long'. Gotta pick one.")

        embed=discord.Embed(title = f"{ctx.author.name} is starting a heist!",description=f"**Heist Checklist**\n> Make sure to have **2000** in your wallet to join!\n> Passive must be off to join the heist (`pls settings passive false`)\n> Have a lifesaver in your inventory in case of your untimely demise" + 
        f"\n**Heist Information**\n> Heist will be started by {ctx.author.mention}\n> You must have the {role.mention} role to join\n> You will have **{length}** minutes to join!")
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)


        restrictrole = ref.child(str(ctx.guild.id)).child('dheistdrole').get() 
        if restrictrole:
            try:
                restrictrole = ctx.guild.get_role(int(restrictrole))
            except:
                return await ctx.reply("Something went wrong getting a role you set up. Did you perhaps delete the default role you set up?")
        else:
            restrictrole = ctx.guild.default_role
        overwrite = ctx.channel.overwrites_for(restrictrole)
        overwrite.view_channel = False
        await ctx.channel.set_permissions(restrictrole, overwrite=overwrite)

        overwrite = ctx.channel.overwrites_for(role)
        overwrite.view_channel = True
        await ctx.channel.set_permissions(role, overwrite=overwrite)

        await ctx.message.delete()
        await ctx.send(embed = embed)

        def check(message: discord.Message):
            if message.author.id == 270904126974590976:
                if message.embeds:
                    heist_embed = message.embeds[0]
                    title = heist_embed.title
                    try:
                        if "starting a bank robbery" in title:
                            return True
                        else:
                            return False
                    except:
                        return False
                else:
                    return False
            else:
                return False

        try:
            msg = await self.client.wait_for("message",timeout = 60.0,check=check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long start the heist, try again lmao.")
            overwrite = ctx.channel.overwrites_for(restrictrole)
            overwrite.view_channel = True
            await ctx.channel.set_permissions(restrictrole, overwrite=overwrite)

            overwrite = ctx.channel.overwrites_for(role)
            overwrite.view_channel = None
            await ctx.channel.set_permissions(role, overwrite=overwrite)
            return

        time = length * 60
        await asyncio.sleep(time)

        overwrite = ctx.channel.overwrites_for(restrictrole)
        overwrite.view_channel = True
        await ctx.channel.set_permissions(restrictrole, overwrite=overwrite)

        overwrite = ctx.channel.overwrites_for(role)
        overwrite.view_channel = None
        await ctx.channel.set_permissions(role, overwrite=overwrite)

        await ctx.send(f"The heist is now over, and channel is visible to everyone again.")

    @commands.command(aliases = ['mtc'],help ="Make a text channel in a certain or the current category.")
    @commands.has_guild_permissions(manage_channels= True)
    async def maketextchannel(self,ctx,name, category: discord.CategoryChannel=None):
        channel = await ctx.guild.create_text_channel(name,overwrites=None, category=category, reason=None)
        await ctx.reply(embed = discord.Embed(description = f'Channel Created {channel.mention}',color = discord.Color.green()))
    
    @commands.command(aliases = ['mvc'],help ="Make a voice channel in a certain or the current category.")
    @commands.has_guild_permissions(manage_channels= True)
    async def makevoicechannel(self,ctx,name, category: discord.CategoryChannel=None):
        channel = await ctx.guild.create_voice_channel(name,overwrites=None, category=category, reason=None)
        await ctx.reply(embed = discord.Embed(description = f'Voice Channel Created {channel.mention}',color = discord.Color.green()))

    @commands.command(aliases = ['sm'],help ="Change the slowmode of the current channel to the specified amount of seconds.")
    @commands.has_guild_permissions(manage_channels= True)
    async def slowmode(self,ctx,time):
        time = timing.timeparse(str(time),0,21600)
        if isinstance(time,str):
            return await ctx.reply(embed = discord.Embed(description = time,color = discord.Color.red()))
        await ctx.channel.edit(slowmode_delay=time.seconds)
        await ctx.reply(f"Set the slowmode delay in this channel to `{time}` seconds!")

    @commands.command(help ="Purge messages in the channel.")
    @commands.has_permissions(manage_messages= True)
    async def purge(self,ctx, amount:int):
        await ctx.channel.purge(limit= amount+1)
        await ctx.send(f'Purged {amount} messages!', delete_after = 3)

class ConfirmationView(discord.ui.View):
    def __init__(self,ctx):
        super().__init__(timeout = 60)
        self.ctx = ctx
        self.value = None
        self.message = None

    
    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False

    @discord.ui.button(emoji = "✅",style = discord.ButtonStyle.green)
    async def confirm(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = True
        self.stop()
    
    @discord.ui.button(emoji = "✖",style = discord.ButtonStyle.red)
    async def deny(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = False
        self.stop()

async def setup(client):
    await client.add_cog(Channels(client))