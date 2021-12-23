import discord
from discord.ext import commands
import json

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


    def pchannel_category_check():
        async def predicate(ctx):
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            categories = ref.child(str(ctx.message.guild.id)).child('pchannels').get()
            
            if categories == None:
                return False
            elif ctx.message.channel.category.id in categories:
                return True
            else:
                return False
        return commands.check(predicate)
    
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
            await ctx.reply("Does not look like this channel is set up.")
            return False

        if member in channels:
            await ctx.reply("Looks like this member is already in this channel.")
            return False
        elif len(channels) >= int(channels[0]) + 1:
            await ctx.reply("It seems you are at the limit for members in this channel.")
            return False
        else:
            channels.append(member)
            ref.child(str(ctx.message.guild.id)).child(str(channel)).set(channels)
            return True

    async def remove_channel(self,ctx,channel,member):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            return False

        for s in range(2,len(channels)):
            #await ctx.reply(channels[s])
            if member == channels[s]:
                del channels[s]
                break
        ref.child(str(ctx.message.guild.id)).child(str(channel)).set(channels)
        return True

    async def change_owner(self,ctx,channel,owner):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        channels = ref.child(str(ctx.message.guild.id)).child(str(channel)).get()
        if channels == None:
            return False
        old = channels[1]

        if int(owner) in channels and channels[1] != int(owner):
            channels.remove(int(owner))

        channels[1] = int(owner)
        ref.child(str(ctx.message.guild.id)).child(str(channel)).set(channels)

        return old

    async def reset_channels(self):
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        ref.set({

        })

    @commands.command(aliases= ['ac'],description = "Add a member to the current channel.",help = "addchannel <member>")
    @pchannel_category_check()
    @commands.has_permissions(manage_channels= True)
    async def addchannel(self,ctx, member:discord.Member):
        if member.bot:
            embed = discord.Embed(description = "Come on, you can't add a bot to this channel. Find a member instead.",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        channel = ctx.channel
        output = await self.add_channel(ctx,channel.id,member.id)
        if output:
            overwrite = channel.overwrites_for(member)
            overwrite.read_messages = True
            await channel.set_permissions(member, overwrite=overwrite)
            embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully added {member.name} to {channel.mention}.",color = discord.Color.green())
            await ctx.reply(embed = embed)

    @commands.command(aliases= ['rc'],description = "Remove a member from the current channel.",help = "removechannel <member>")
    @pchannel_category_check()
    @commands.has_permissions(manage_channels= True)
    async def removechannel(self,ctx, member:discord.Member):
        channel = ctx.channel
        limit = await self.get_channel_limit(ctx,ctx.channel.id)
        if not limit:
            embed = discord.Embed(description = "This channel is not setup as a private channel.",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        if (member.id == await self.get_channel_owner(ctx,channel.id)):
            embed = discord.Embed(description = "You cannot remove the owner of this channel!",color = discord.Color.red())
            await ctx.reply(embed = embed)
        else:
            channel = channel or ctx.channel
            await self.remove_channel(ctx,channel.id,member.id)
            overwrite = channel.overwrites_for(member)
            #overwrite.send_messages = False
            overwrite.read_messages = False
            await channel.set_permissions(member, overwrite=None)
            embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully removed {member.name} from {channel.mention}.",color = discord.Color.green())
            await ctx.reply(embed = embed)

    @commands.command(aliases = ['abused'],description = "Got abused? Left the server? Well you probably want back into your private channels. This command will help you out with that.",help = "fixchannel <member>")
    @commands.has_permissions(administrator= True)
    async def fixchannel(self,ctx,member):
        if str(member).isnumeric():
            guild = ctx.guild
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)

        if not member:
            return await ctx.send("That does not look like a valid member!")

        userid = member.id
        ref = db.reference("/",app = firebase_admin._apps['pepegabot'])
        allchannels = channels = ref.child(str(ctx.message.guild.id)).get()

        build = "**Added to:**\n"
        ownerbuild = "**Was set the owner of:**\n"
        error = "**Could not add to:**"
        for channel in allchannels:
            if userid in allchannels[channel]:
                channel_object = ctx.guild.get_channel(int(channel))
                if channel_object:
                    if channel_object.overwrites_for(member).is_empty():
                        if allchannels[channel][1] == int(userid):
                            overwrite = channel_object.overwrites_for(member)
                            overwrite.manage_channels = True
                            overwrite.read_messages = True
                            overwrite.manage_messages = True
                            await channel_object.set_permissions(member, overwrite=overwrite)
                            embed = discord.Embed(description = f"<@{userid}> was set as the owner of this channel. Believe this was a mistake? Contact an Admin.",color = discord.Color.random())
                            await channel_object.send(embed = embed)
                            ownerbuild += f"<#{channel}>\n"
                        else:
                            overwrite = channel_object.overwrites_for(member)
                            overwrite.read_messages = True
                            await channel_object.set_permissions(member, overwrite=overwrite)
                            embed = discord.Embed(description = f"<@{userid}> was added to this channel. Believe this was a mistake? Use `[prefix]rc <user>` to remove them!",color = discord.Color.random())
                            await channel_object.send(embed = embed)
                            build += f"<#{channel}>\n"
                else:
                    error += f"{channel}\n"
        
        embed = discord.Embed(title = f"Private Channels that were Fixed for {member.name}",description = ownerbuild + build + error,color = discord.Color.random())
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.send(embed = embed)


    @commands.command(aliases= ['sc'],description = "Set the channel owner.",help = "setchannel <member> [channel] [limit]")
    @pchannel_category_check()
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
            embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully set {channel.mention} as a private channel with {owner.mention} as the owner. The channel has a limit of {limit} people",color = discord.Color.green())
            await ctx.reply(embed = embed)
        else:
            embed = discord.Embed(description = f"{channel.mention} is already a private channel!",color = discord.Color.red())
            await ctx.reply(embed = embed)

    @commands.command(aliases = ['ci'],description = "Show the information for the current channel.",help = "channelinfo [channel]")
    @pchannel_category_check()
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
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Channel Owner:",value=f'<@{owner}>',inline=True)
        embed.add_field(name="Channel Limit:",value=f'{len(members)}/{limit}',inline=True)
        embed.add_field(name="Members:",value=buildmembers,inline=False)

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)

        await ctx.reply(embed=embed)

    @commands.command(aliases=['cl'],description = "Change the member limit of the current channel.",help = "changelimit <limit> [channel]")
    @pchannel_category_check()
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

    @commands.command(aliases = ["co"],description = "Change the current channel owner.",help = "changeowner <owner>")
    @pchannel_category_check()
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
            

def setup(client):
    client.add_cog(PrivateChannels(client))
