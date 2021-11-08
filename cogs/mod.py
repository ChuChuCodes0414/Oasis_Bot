import discord
from discord.ext import commands

import firebase_admin
from firebase_admin import db
import datetime
from datetime import datetime
import math
import asyncio

class Mod(commands.Cog):
    """
        Simple mod commands, like kick and ban.
        \n**Setup for this Category**
        Mod Role: `o!settings add mod <role>` 
    """
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Mod Cog Loaded.')

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
    
    async def pull_data(self,guild,member):
        ref = db.reference("/",app = firebase_admin._apps['modlogs'])
        modlogs = ref.child(str(guild)).child(str(member)).get()

        return modlogs

    async def set_data(self,guild,member,action,reason,mod):
        ref = db.reference("/",app = firebase_admin._apps['modlogs'])
        modlogs = ref.child(str(guild)).child(str(member)).get()

        if modlogs == None:
            modlogs = []

        now = datetime.now()
        formatnow = str(now.month) + "-" + str(now.day) + "-" + str(now.year) + " " + str(now.hour) + ":" + str(now.minute)

        modlogs.append([action,formatnow,reason,mod])

        ref.child(str(guild)).child(str(member)).set(modlogs)
    

    @commands.Cog.listener()
    async def on_member_join(self,member):
        if member.guild.id == 798822518571925575:
            date = member.created_at
            now = datetime.now()
            diff = now - date

            if diff.days < 30:
                embed=discord.Embed(title=f"⚠ Alert For {member}",description=f"`There is an account under 30 days old!`", color=discord.Color.red())
                embed.set_thumbnail(url = member.avatar_url)
                embed.add_field(name = "User Information",value = f'{member.id}\n{member.mention}',inline = True)
                embed.add_field(name = "Account Created On",value= f'{date}',inline = True)
                embed.timestamp = datetime.utcnow()
                embed.set_footer(text = f'{member.guild.name}',icon_url = member.guild.icon_url)
                channel = self.client.get_channel(825882336594886687)
                await channel.send(embed=embed)\


    @commands.command(description = "Change a member's nickname.",help = "setnick <member> <nickname>")
    @commands.has_permissions(manage_nicknames = True) 
    async def setnick(self,ctx, member,*,nickname = None):
        guild = ctx.guild
        if str(member).isnumeric():
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)

        bot_top = ctx.guild.get_member(self.client.user.id)
        bot_top_ob = bot_top.top_role
        if member.top_role >= ctx.author.top_role:
            await ctx.reply("You cannot change the nickname of people who have a higher role than you.")
        elif bot_top_ob <= member.top_role:
            await ctx.reply("Does not seem like I can change that person's nickname, since their top role is higher than my top role.")
        else:
            await member.edit(nick=nickname)
            await ctx.reply("Edited member's nickname.")

    @commands.command(description = "Give/remove a role to someone else.",help = "role <member> <role>")
    @commands.has_permissions(manage_roles = True) 
    async def role(self,ctx, member:discord.Member,role:discord.Role):
        bot_top = ctx.guild.get_member(self.client.user.id)
        bot_top_ob = bot_top.top_role
        if role >= bot_top_ob:
            return await ctx.reply(f"That role position ({role.position}) is higher or equal to my top role ({bot_top_ob.position}). Try changing my role position to something higher than the role you want to add.")
        elif ctx.author.top_role <= role:
            return await ctx.reply(f"That role position ({role.position}) is higher or equal to your top role ({ctx.author.top_role.position}). Ain't letting you exploit today.")

        if role in member.roles:
            await member.remove_roles((role))
            await ctx.send(f"Removed **{role.name}** from **{member}**")
        else:
            await member.add_roles((role))
            await ctx.send(f"Added **{role.name}** to **{member}**")

    @commands.command(aliases = ['k'],description = "Kick a member from the server.",help = "kick <member>")
    @commands.has_permissions(kick_members = True) 
    async def kick(self,ctx, member,*,reason = None):
        guild = ctx.guild
        if str(member).isnumeric():
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)
        
        if not member:
            return await ctx.reply("Hey, does not seem like that person is in the server.")

        if member.top_role >= ctx.author.top_role:
            await ctx.reply("You cannot kick people who have a higher role than you.")
        else:
            try:
                dm = member.dm_channel
                if dm == None:
                    dm = await member.create_dm()
                await dm.send(f'You were kicked from {guild} for the following reason:\n{reason}')
            except:
                pass
            await self.set_data(guild.id, member.id, 'Kick', reason, str(ctx.message.author))
            await member.kick(reason=reason)
            await ctx.reply(f'**{member}** was kicked out of the server.')

    @commands.command(aliases = ['b'],description = "Ban a member from the server",help = "ban <member>")
    @commands.has_permissions(ban_members = True) 
    async def ban(self,ctx,member, *,reason = None):
        guild = ctx.guild
        if str(member).isnumeric():
            id = int(member)
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)

        if not member:
            user = await self.client.fetch_user(int(id))
            await ctx.guild.ban(user,reason = reason,delete_message_days=0)
            return await ctx.reply(f'**{user.name}#{user.discriminator}** was banned from the server.')

        if member.top_role >= ctx.author.top_role:
            await ctx.reply("You cannot ban people who have a higher role than you.")
        else:
            try:
                dm = member.dm_channel
                if dm == None:
                    dm = await member.create_dm()
                await dm.send(f'You were banned from {guild} for the following reason:\n{reason}')
            except:
                pass
            await self.set_data(guild.id, member.id, 'Ban', reason, str(ctx.message.author))
            await member.ban(reason=reason)
            await ctx.reply(f'**{member}** was banned from the server.')

    @commands.command(aliases = ['mb'],description = "Mass ban members from the server",help = "massban <members>")
    @commands.has_permissions(ban_members = True) 
    async def massban(self,ctx,*,members,):
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
                    await self.set_data(guild.id, user.id, 'Ban', f"Massban Taken by **{ctx.author}**", str(ctx.message.author))
                    count += 1
                else:
                    if member.top_role >= ctx.author.top_role:
                        continue
                    await member.ban(reason=f"Massban Taken by **{ctx.author}**",delete_message_days=0)
                    await self.set_data(guild.id, member.id, 'Ban', f"Massban Taken by **{ctx.author}**", str(ctx.message.author))
                    count += 1
            await asyncio.sleep(1)

        try:
            await ctx.reply(f"Banned **{count}** members")
        except:
            await ctx.send(f"Banned **{count}** members")

    @commands.command(description = "Unban a member from the server.",help = "unban <member>")
    @commands.has_permissions(ban_members = True) 
    async def unban(self,ctx,member,*,reason=None):
        banned_users = await ctx.guild.bans()
        member = int(member)

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.id == member):
                await ctx.guild.unban(user,reason = reason)
                await self.set_data(ctx.guild.id, user.id, 'Unban', reason, str(ctx.message.author))
                await ctx.reply(f'Unbanned **{user.name}#{user.discriminator}** for {reason}')
                return
        await ctx.reply("I cannot find this person on the bans list!")

    @commands.command(description = "Warn a member.",help = "warn <member> <reason>")
    @mod_role_check()
    async def warn(self,ctx,member,*, reason):
        guild = ctx.guild
        if str(member).isnumeric():
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)

        await self.set_data(guild.id, member.id, 'Warn', reason, str(ctx.message.author))

        await ctx.reply(f'Warned **{member}** for {reason}')

        
    @commands.command(description = "Check modlogs of a member.",help = "modlogs <member>")
    @mod_role_check()
    async def modlogs(self,ctx,member,index = 1):
        guild = ctx.guild
        store = member

        if member.isnumeric():
            member = await self.client.fetch_user(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)


        logs = await self.pull_data(guild.id, member.id)

        if not logs:
            logs = []

        logs.reverse()
        embed=discord.Embed(title=f"Mod Logs for {member.name}",description=f"{len(logs)} items found for {member.mention}", color=discord.Color.green())

        index = int(index)
        logamount = len(logs)
        if index > 1:
            if (index - 1) * 9 < logamount:
                if int(index) * 9 > logamount:
                    end = logamount 
                else:
                    end = (index)*9
                
                start = (index-1) * 9
            else:
                return await ctx.reply(f"There are not {index} pages.")
        else:
            start = 0
            if logamount > 9:
                end = 9
            else:
                end = logamount 
        for log in range(start,end):
            embed.add_field(name=f'Action {log+1}',value = f'**Action:** {logs[log][0]}\n{logs[log][1]}\n**Reason:** {logs[log][2]}\n**Moderator:** {logs[log][3]}',inline = True)

        embed.set_footer(text=f"Showing page {index} out of {math.ceil(logamount/9)}")

        await ctx.reply(embed = embed)

        

def setup(client):
    client.add_cog(Mod(client))