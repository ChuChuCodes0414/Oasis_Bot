import discord
from discord.ext import commands
import random
import datetime
import uuid

class Utility(commands.Cog):
    """
        Utility commands, includes information and other things like whois and roleinfo.
    """

    def __init__(self,client):
        self.client = client
        self.client.poll_data = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print('Util Cog Loaded.')

    @commands.command(aliases = ['i'],description = "Some basic information about a user.",help = 'whois [member]')
    async def whois(self,ctx,member = None):
        if member:
            if str(member).isnumeric():
                guild = ctx.guild
                member = guild.get_member(int(member))
            else:
                member = await commands.converter.MemberConverter().convert(ctx,member)
        else:
            member = ctx.message.author

        embed = discord.Embed(title = f'Information about {member}',color = discord.Color.green())
        embed.set_thumbnail(url = member.avatar_url)

        embed.add_field(name = "User ID",value = member.id,inline = True)
        embed.add_field(name = "User Name",value = member.name,inline = True)
        embed.add_field(name = "User Nickname",value = member.nick,inline = True)

        embed.add_field(name = "Join Date",value = member.joined_at.strftime("%Y-%m-%d %H:%M"),inline = True)
        embed.add_field(name = "Account Creation",value = member.created_at.strftime("%Y-%m-%d %H:%M"),inline = True)

        if member.premium_since:
            embed.add_field(name = "Server Boosting Since",value = member.premium_since.strftime("%Y-%m-%d %H:%M"),inline = True)
        else:
            embed.add_field(name = "Server Boosting Since",value = "Not Boosting",inline = True)

        if len(member.roles) >= 10:
            embed.add_field(name = "Roles",value = f'Too many to list.',inline = True)
        else:
            build = ""
            for role in reversed(member.roles[1:]):
                build += role.mention + ","

            build = build[:-1]

            if build == "":
                build = "None"
            
            embed.add_field(name = "Roles",value = f'{build}',inline = True)

        embed.add_field(name = "Top Role",value = f'{member.top_role.mention}',inline = True)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)

    @commands.command(aliases = ['si'],description = "Some basic information about the current server.",help = 'serverinfo')
    async def serverinfo(self,ctx):
        guild = ctx.guild

        embed = discord.Embed(title = f'Information about {guild.name}',description = f'ID: {guild.id}',color = discord.Color.green())
        embed.set_thumbnail(url = ctx.guild.icon)

        embed.add_field(name = "Sever Region",value = guild.region,inline = True)
        embed.add_field(name = "Creation Date",value = guild.created_at.strftime("%Y-%m-%d %H:%M"),inline = True)
        embed.add_field(name = "Server Owner",value = guild.owner,inline = True)

        humans = len([m for m in ctx.guild.members if not m.bot])
        bots = guild.member_count-humans
        embed.add_field(name = "Member Count",value = f'Total Members: {guild.member_count}\nHuman Members: {humans}\nBots: {bots}',inline = True)
        embed.add_field(name = "Channel Count",value = f'Text Channels: {len(guild.text_channels)}\nVoice Channels: {len(guild.voice_channels)}')
        embed.add_field(name = "Booster Count",value = f'Boost Level: {guild.premium_tier}\nBoost Count: {guild.premium_subscription_count}')

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)
    
    @commands.command(aliases = ["ri"],description = "View some information about a role.",help = "roleinfo <role>")
    async def roleinfo(self,ctx,role:discord.Role):
        membercount = len(role.members)
        color = role.color
        created_at = role.created_at.strftime("%b %d %Y %H:%M:%S")
        position = role.position

        build = f"{role.mention}\nCreated At: {created_at}\nRole Color: {color}\nMember Count: {membercount}\nRole Position: {position}"
        emb = discord.Embed(title = f"Role Info for {role.name}",description = build,color = color)

        await ctx.send(embed = emb)



def setup(client):
    client.add_cog(Utility(client))