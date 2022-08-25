import discord
from discord.ext import commands
import asyncio
import firebase_admin
from firebase_admin import db
import datetime

class PrivateChannels(commands.Cog):
    """
        Private channel management, with different commands to keep them organized. You must setup private channel categories for this to work.
        \n**Setup for this Category**
        Private Channel Category: `o!settings add pchannel <category>` 
    """

    def __init__(self,client):
        self.client = client
        self.short = "🔐 | Private Channels for Members"
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('PChannels Cog Loaded.')

    async def get_channel_members(self,ctx,channel):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            return False
        return channels[1:]

    async def get_channel_limit(self,ctx,channel):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            return False
        return channels[0]

    async def get_channel_owner(self,ctx,channel):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            return False
        return channels[1]

    async def change_limit(self,ctx,channel,limit):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            return False
        else:
            channels[0] = limit
            ref.child(str(ctx.message.guild.id)).child(str(channel)).set(channels)
            return True

    async def make_channel(self,ctx,channel,limit,owner):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            channels = [int(limit),owner]
            ref.child(str(ctx.message.guild.id)).child(str(channel)).set(channels)
            return True
        else:
            return False

    async def add_channel(self,ctx,channel,member):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            return "Does not look like this channel is set up."
        if member in channels:
            return "Looks like this member is already in this channel."
        elif len(channels) >= int(channels[0]) + 1:
            return "It seems you are at the limit for members in this channel."
        else:
            channels.append(member)
            ref.child(str(ctx.message.guild.id)).child(str(channel)).set(channels)
            return True

    async def remove_channel(self,ctx,channel,member):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            return "Does not look like this channel is set up."
        if member == channels[1]:
            return "You cannot remove the owner from this channel!"
        if member in channels:
            channels.remove(member)
            ref.child(str(ctx.message.guild.id)).child(str(channel)).set(channels)
            return True
        return "This member is not in this channel!"

    async def change_owner(self,ctx,channel,owner):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            return "Does not look like this channel is set up."
        old = channels[1]
        if int(owner) in channels and channels[1] != int(owner):
            channels.remove(int(owner))
        channels[1] = int(owner)
        ref.child(str(ctx.message.guild.id)).child(str(channel)).set(channels)
        return old

    @commands.command(aliases= ['ac'],help = "Add a member to the current channel.")
    @commands.has_permissions(manage_channels= True)
    async def addchannel(self,ctx, member:discord.Member):
        if member.bot:
            embed = discord.Embed(description = "Come on, you can't add a bot to this channel. I know you are lonely...don't worry we've all been there. Try adding a cool person to talk to instead!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        output = await self.add_channel(ctx,ctx.channel.id,member.id)
        if output == True:
            overwrite = ctx.channel.overwrites_for(member)
            overwrite.read_messages = True
            await ctx.channel.set_permissions(member, overwrite=overwrite)
            embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully added **{member}** to {ctx.channel.mention}.",color = discord.Color.green())
            await ctx.reply(embed = embed)
        else:
            embed = discord.Embed(description = output,color = discord.Color.red())
            await ctx.reply(embed = embed)

    @commands.command(aliases= ['rc'],help = "Remove a member from the current channel.")
    @commands.has_permissions(manage_channels= True)
    async def removechannel(self,ctx, user:discord.User):
        output = await self.remove_channel(ctx,ctx.channel.id,user.id)
        if output == True:
            try:
                member = await commands.converter.MemberConverter().convert(ctx,str(user.id))
            except:
                return await ctx.reply(embed = discord.Embed(description = f"**{user}** is no longer in the server! I have removed them from the channel.",color = discord.Color.green()))
            overwrite = ctx.channel.overwrites_for(member)
            await ctx.channel.set_permissions(member, overwrite=None)
            embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully removed override for **{member}** from {ctx.channel.mention}.",color = discord.Color.green())
            await ctx.reply(embed = embed)
        else:
            embed = discord.Embed(description = output,color = discord.Color.red())
            await ctx.reply(embed = embed)

    @commands.command(aliases = ['abused'],help = "Adds a member back to their channels.",brief = "Got abused? Left the server? Well you probably want back into your private channels. This command will help you out with that.")
    @commands.has_permissions(administrator= True)
    async def fixchannel(self,ctx,member:discord.Member):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        allchannels = ref.child(str(ctx.message.guild.id)).get()
        embed = discord.Embed(title = "Fixing Channels!",description = f"Fixing private channels for **{member}**, this might take a bit. Please wait.",color = discord.Color.yellow())
        await ctx.reply(embed = embed)
        build = "**Added to:**\n"
        ownerbuild = "**Was set the owner of:**\n"
        error = "**Could not add to:**"
        for channel in allchannels:
            if member.id in allchannels[channel]:
                channel_object = ctx.guild.get_channel(int(channel))
                if channel_object:
                    if channel_object.overwrites_for(member).is_empty():
                        if allchannels[channel][1] == int(member.id):
                            overwrite = channel_object.overwrites_for(member)
                            overwrite.manage_channels = True
                            overwrite.read_messages = True
                            overwrite.manage_messages = True
                            await channel_object.set_permissions(member, overwrite=overwrite)
                            embed = discord.Embed(description = f"**{member}** was set as the owner of this channel. Believe this was a mistake? Contact an Admin.",color = discord.Color.random())
                            await channel_object.send(embed = embed)
                            ownerbuild += f"<#{channel}>\n"
                        else:
                            overwrite = channel_object.overwrites_for(member)
                            overwrite.read_messages = True
                            await channel_object.set_permissions(member, overwrite=overwrite)
                            embed = discord.Embed(description = f"**{member}** was added to this channel. Believe this was a mistake? Use `[prefix]rc <user>` to remove them!",color = discord.Color.random())
                            await channel_object.send(embed = embed)
                            build += f"<#{channel}>\n"
                else:
                    error += f"\n{channel}"
                await asyncio.sleep(0.5)
        embed = discord.Embed(title = f"Private Channels that were Fixed for {member.name}",description = ownerbuild + build + error,color = discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        await ctx.send(embed = embed)

    @commands.command(aliases= ['sc'],help = "Setup a channel with an owner and limit.",brief = "This command requires you to already have the channel made and set to private in discord. You need to complete this command first before using the other ones.")
    @commands.has_permissions(administrator= True)
    async def setchannel(self,ctx,owner:discord.Member,channel:discord.TextChannel=None,limit = 5):
        channel = channel or ctx.channel
        output = await self.make_channel(ctx,channel.id,int(limit),owner.id)
        if output:
            overwrite = channel.overwrites_for(owner)
            overwrite.manage_channels = True
            overwrite.read_messages = True
            overwrite.manage_messages = True
            await channel.set_permissions(owner, overwrite=overwrite)
            embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully set {channel.mention} as a private channel with **{owner}** as the owner. The channel has a limit of `{limit}` people",color = discord.Color.green())
            await ctx.reply(embed = embed)
        else:
            embed = discord.Embed(description = f"{channel.mention} is already a private channel! Use `[prefix]channelinfo` for information.",color = discord.Color.red())
            await ctx.reply(embed = embed)

    @commands.command(aliases = ['ci'],description = "Show the information for the current or specified channel.")
    async def channelinfo(self,ctx,channel:discord.TextChannel=None):
        channel = channel or ctx.channel
        embed=discord.Embed(title="Channel Info",description=f"Channel info for {channel.mention}", color=discord.Color.random())
        try:
            limit = await self.get_channel_limit(ctx,channel.id)
            members = await self.get_channel_members(ctx,channel.id)
            owner = await self.get_channel_owner(ctx,channel.id)
        except:
            embed = discord.Embed(description = "It does not seem like this channel has been set up!",color = discord.Color.red())
            return await ctx.reply(embed = embed)

        if not(limit and members and owner):
            embed = discord.Embed(description = "It does not seem like this channel has been set up!",color = discord.Color.red())
            return await ctx.reply(embed = embed)

        buildmembers = '<@'+str(members[0])+'>'
        if len(members) >= 2:
            for member in members[1:]:
                buildmembers+= (', <@'+str(member)+'>')
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.add_field(name="Channel Owner:",value=f'<@{owner}>',inline=True)
        embed.add_field(name="Channel Limit:",value=f'{len(members)}/{limit}',inline=True)
        embed.add_field(name="Members:",value=buildmembers,inline=False)

        embed.timestamp = datetime.datetime.now()
        await ctx.reply(embed=embed)

    @commands.command(aliases=['cl'],help = "Change the member limit of the current channel.")
    @commands.has_permissions(administrator= True)
    async def changelimit(self,ctx,limit,channel:discord.TextChannel=None):
        channel = channel or ctx.channel
        output = await self.change_limit(ctx,channel.id,limit)
        if output:
            embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully changed limit of {channel.mention} to {limit}.',color = discord.Color.green())
            await ctx.reply(embed = embed)
        else:
            embed = discord.Embed(description = "It does not seem like this channel has been set up!",color = discord.Color.red())
            return await ctx.reply(embed = embed)

    @commands.command(aliases = ["co"],help = "Change the current channel owner.")
    @commands.has_permissions(administrator= True)
    async def changeowner(self,ctx,owner:discord.Member):
        channel = ctx.channel
        output = await self.change_owner(ctx,channel.id,owner.id)
        if output:
            old = ctx.guild.get_member(int(output))
            if old:
                await channel.set_permissions(old, overwrite=None)
            overwrite = channel.overwrites_for(owner)
            overwrite.manage_channels = True
            overwrite.read_messages = True
            overwrite.manage_messages = True
            await channel.set_permissions(owner, overwrite=overwrite)
            embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully set {channel.mention} as a private channel with {owner.mention} as the owner. The previous owner has been removed.",color = discord.Color.green())
            await ctx.reply(embed = embed)
        else:
            embed = discord.Embed(description = "It does not seem like this channel has been set up!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
    
    @commands.command(help = "Remove private channel data.")
    @commands.has_permissions(administrator= True)
    async def deletechannel(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channeldata = ref.child(str(ctx.message.guild.id)).child(str(channel.id)).get()

        if not channeldata:
            return await ctx.reply(embed = discord.Embed(description = "This channel does not exsist in my database!",color = discord.Color.red()))
        
        ref.child(str(ctx.message.guild.id)).child(str(channel.id)).delete()
        await ctx.reply(embed = discord.Embed(description = f"Removed all data I have stored for {channel.mention}\nThis does not remove any exsisting overrides!",color = discord.Color.green()))


async def setup(client):
    await client.add_cog(PrivateChannels(client))
