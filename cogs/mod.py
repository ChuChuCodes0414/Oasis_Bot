import re
import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import db
import datetime
import math
import asyncio
from utils import timing

class Mod(commands.Cog):
    """
        Simple mod commands, like kick and ban.
        \n**Setup for this Category**
        Mod Role: `o!settings add mod <role>` 
    """
    def __init__(self,client):
        self.client = client
        self.short = "<:bantime:930623021180387328> | Mod commands!"

    @commands.Cog.listener()
    async def on_ready(self):
        print('Mod Cog Loaded.')

    @commands.Cog.listener()
    async def on_member_join(self,member):
        if member.guild.id == 798822518571925575:
            date = member.created_at
            now = datetime.datetime.now()
            diff = now - date

            if diff.days < 30 and diff.days > 3:
                embed=discord.Embed(title=f"⚠ Alert For {member}",description=f"`There is an account under 30 days old!`", color=discord.Color.red())
                embed.set_thumbnail(url = member.avatar_url)
                embed.add_field(name = "User Information",value = f'{member.id}\n{member.mention}',inline = True)
                embed.add_field(name = "Account Created On",value= f'{date}',inline = True)
                embed.timestamp = datetime.now()
                embed.set_footer(text = f'{member.guild.name}',icon_url = member.guild.icon)
                channel = self.client.get_channel(825882336594886687)
                await channel.send(embed=embed)\

    @commands.command(help = "Change a member's nickname.")
    @commands.has_permissions(manage_nicknames = True) 
    async def setnick(self,ctx, member:discord.Member,*,nickname = None):
        bot_top = ctx.guild.get_member(self.client.user.id)
        bot_top_ob = bot_top.top_role
        if member.top_role >= ctx.author.top_role:
            await ctx.reply(embed = discord.Embed(description = "You cannot change the nickname of people who have a higher or euqal role as you.",color = discord.Color.red()))
        elif bot_top_ob <= member.top_role:
            await ctx.reply(embed = discord.Embed(description = "Does not seem like I can change that person's nickname, since their top role is higher than my top role.",color = discord.Color.red()))
        else:
            await member.edit(nick=nickname)
            await ctx.reply(embed = discord.Embed(description = f"Edited {member}'s nickname to: `{nickname}`",color = discord.Color.green()))

    @commands.command(help = "Give/remove a role to someone else.")
    @commands.has_permissions(manage_roles = True) 
    async def role(self,ctx, member:discord.Member,role:discord.Role):
        bot_top = ctx.guild.get_member(self.client.user.id)
        bot_top_ob = bot_top.top_role
        if role >= bot_top_ob:
            return await ctx.reply(embed = discord.Embed(description = f"That role position `({role.position})` is higher or equal to my top role `({bot_top_ob.position})`. Try changing my role position to something higher than the role you want to add.",color = discord.Color.red()))
        elif ctx.author.top_role <= role:
            return await ctx.reply(embed = discord.Embed(description = f"That role position `({role.position})` is higher or equal to your top role `({ctx.author.top_role.position})`. Ain't letting you exploit today.",color = discord.Color.red()))

        if role in member.roles:
            await member.remove_roles((role))
            await ctx.reply(embed = discord.Embed(description = f"Removed **{role.name}** from **{member}**",color = discord.Color.green()))
        else:
            await member.add_roles((role))
            await ctx.reply(embed = discord.Embed(description = f"Added **{role.name}** to **{member}**",color = discord.Color.green()))
    
    @commands.command(aliases = ['to'],help = "Timeout a user through the timeout function")
    @commands.has_permissions(moderate_members = True)
    async def timeout(self,ctx,member:discord.Member,duration,*,reason = None):
        bot_top = ctx.guild.get_member(self.client.user.id)
        bot_top_ob = bot_top.top_role
        if bot_top_ob <= member.top_role:
            return await ctx.reply(embed = discord.Embed(description = f"That member has a role position `({member.top_role.position})` that is higher or equal to my top role `({bot_top_ob.position})`.",color = discord.Color.red()))
        if member.top_role >= ctx.author.top_role:
            return await ctx.reply(embed = discord.Embed(description = "You cannot timeout people who have a higher role than you.",color = discord.Color.red()))
        success = True
        c = ""
        hours = 0
        seconds = 0
        for letter in duration:
            if letter.isalpha():
                letter = letter.lower()
                try: c = int(c) 
                except: 
                    success = False  
                    break
                if letter == 'w': hours += c*168 
                elif letter == 'd': hours += c*24
                elif letter == 'h': hours += c
                elif letter == 'm': seconds += c*60
                elif letter == 's': seconds += c
                else: 
                    success = False
                    break
                c = ""
            else:
                c += letter
        if c != "" or not success:
            return await ctx.reply(embed = discord.Embed(description = f'I could not parse your timing input!\n\nValid Time Inputs:\n`w` - weeks\n`d` - days\n`h` - hours\n`m` - minutes\n`s` - seconds\n\nExamples: `2w`, `2h30m`, `10s`',color = discord.Color.red()))
        added = datetime.timedelta(hours = hours,seconds = seconds)
        if added.days >= 28:
            return await ctx.reply(embed = discord.Embed(description = f"You cannot timeout a member for more than `4 weeks`!",color = discord.Color.red()))
        until = discord.utils.utcnow() + added
        await member.edit(timed_out_until = until,reason = reason)
        unix = int(until.replace(tzinfo=datetime.timezone.utc).timestamp())
        await ctx.reply(embed = discord.Embed(description = f"Timed out **{member}** until <t:{unix}:f> (<t:{unix}:R>)",color = discord.Color.green()))

    @commands.command(aliases = ['uto'])
    @commands.has_permissions(moderate_members = True)
    async def untimeout(self,ctx,member:discord.Member,*,reason = None):
        bot_top = ctx.guild.get_member(self.client.user.id)
        bot_top_ob = bot_top.top_role
        if bot_top_ob <= member.top_role:
            return await ctx.reply(embed = discord.Embed(description = f"That member has a role position `({member.top_role.position})` that is higher or equal to my top role `({bot_top_ob.position})`.",color = discord.Color.red()))
        if member.top_role >= ctx.author.top_role:
           return await ctx.reply(embed = discord.Embed(description = "You cannot manage timeout for people who have a higher role than you.",color = discord.Color.red()))
        await member.edit(timed_out_until = None,reason = reason)
        await ctx.reply(embed = discord.Embed(description = f"Removed timeout from **{member}**",color = discord.Color.green()))
    
    @commands.command(aliases = ['k'],help = "Kick a member from the server.")
    @commands.has_permissions(kick_members = True) 
    async def kick(self,ctx, member:discord.Member,*,reason = None):
        bot_top = ctx.guild.get_member(self.client.user.id)
        bot_top_ob = bot_top.top_role
        if bot_top_ob <= member.top_role:
            return await ctx.reply(embed = discord.Embed(description = f"That member has a role position `({member.top_role.position})` that is higher or equal to my top role `({bot_top_ob.position})`.",color = discord.Color.red()))
        if member.top_role >= ctx.author.top_role:
            await ctx.reply(embed = discord.Embed(description = "You cannot kick people who have a higher role than you.",color = discord.Color.red()))
        else:
            res = ""
            try:
                dm = member.dm_channel
                if dm == None:
                    dm = await member.create_dm()
                await dm.send(f'**You were kicked from {ctx.guild} for the following reason:**\n{reason}')
                res += "Member DMed? <:greentick:930931553478008865>"
            except:
                res += "Member DMed? <:redtick:930931511685955604>"
            await member.kick(reason=reason)
            embed = discord.Embed(description = f"**{member}** was kicked from the server\n{res}",color = discord.Color.green())
            await ctx.reply(embed = embed)

    @commands.command(aliases = ['b'],help = "Ban a member from the server")
    @commands.has_permissions(ban_members = True) 
    async def ban(self,ctx,member, *,reason = None):
        try:
            member = await commands.converter.MemberConverter().convert(ctx,member)
            failed = False
        except:
            failed = True
            member = member
        if failed:
            try:
                user = await self.client.fetch_user(int(member))
            except:
                return await ctx.reply(embed = discord.Embed(description = "I could not find a user with that id! Try again with an actual id.",color = discord.Color.red()))
            if user:
                await ctx.guild.ban(user,reason = reason,delete_message_days=0)
                return await ctx.reply(embed = discord.Embed(description = f'**{user.name}#{user.discriminator}** was banned from the server.\nMember Originally in Server? <:redtick:930931511685955604>',color = discord.Color.green()))
        bot_top = ctx.guild.get_member(self.client.user.id)
        bot_top_ob = bot_top.top_role
        if bot_top_ob <= member.top_role:
            return await ctx.reply(embed = discord.Embed(description = f"That member has a role position `({member.top_role.position})` that is higher or equal to my top role `({bot_top_ob.position})`.",color = discord.Color.red()))
        if member.top_role >= ctx.author.top_role:
            await ctx.reply(embed = discord.Embed(description = "You cannot ban people who have a higher role than you.",color = discord.Color.red()))
        else:
            res = ""
            try:
                dm = member.dm_channel
                if dm == None:
                    dm = await member.create_dm()
                await dm.send(f'**You were banned from {ctx.guild} for the following reason:**\n{reason}')
                res += "Member DMed? <:greentick:930931553478008865>"
            except:
                res += "Member DMed? <:redtick:930931511685955604>"
            await member.ban(reason=reason,delete_message_days=0)
            embed = discord.Embed(description = f"**{member}** was banned from the server\n{res}",color = discord.Color.green())
            await ctx.reply(embed = embed)

    @commands.command(aliases = ['mb'],help = "Mass ban members from the server")
    @commands.has_permissions(ban_members = True) 
    async def massban(self,ctx,*,members):
        guild = ctx.guild
        members = members.split()
        count = 0
        async with ctx.typing():
            for member in members:
                if str(member).isnumeric():
                    id = int(member)
                    member = guild.get_member(int(member))
                else:
                    member = await commands.converter.MemberConverter().convert(ctx,member)

                if not member:
                    user = await self.client.fetch_user(int(id))
                    await ctx.guild.ban(user,reason = f"Massban Taken by **{ctx.author}**",delete_message_days=0)
                    count += 1
                else:
                    if member.top_role >= ctx.author.top_role:
                        continue
                    await member.ban(reason=f"Massban Taken by **{ctx.author}**",delete_message_days=0)
                    count += 1
            await asyncio.sleep(1)

        try:
            await ctx.reply(embed = discord.Embed(description = f"Banned **{count}** members",color = discord.Color.green()))
        except:
            await ctx.send(embed = discord.Embed(description = f"Banned **{count}** members",color = discord.Color.green()))

    @commands.command(help = "Unban a member from the server.")
    @commands.has_permissions(ban_members = True) 
    async def unban(self,ctx,user:discord.User,*,reason=None):
        try:
            await ctx.guild.unban(user,reason = reason)
            await ctx.reply(embed = discord.Embed(description = f"Unbanned **{user}**",color = discord.Color.green()))
        except:
            return await ctx.reply(embed = discord.Embed(description = "That user is not currently banned.",color = discord.Color.red()))

        
async def setup(client):
    await client.add_cog(Mod(client))