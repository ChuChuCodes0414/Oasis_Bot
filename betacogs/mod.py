import discord
from discord.ext import commands
from discord.commands import slash_command
import firebase_admin
from firebase_admin import db
import datetime
from datetime import datetime
import math
import asyncio

class Mod(discord.ext.commands.Cog):
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

    @commands.Cog.listener()
    async def on_member_join(self,member):
        if member.guild.id == 798822518571925575:
            date = member.created_at
            now = datetime.now()
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
            await ctx.reply(embed = discord.Embed(description = "You cannot change the nickname of people who have a higher or euqal role as you.",color = discord.Color.red()),mention_author = False)
        elif bot_top_ob <= member.top_role:
            await ctx.reply(embed = discord.Embed(description = "Does not seem like I can change that person's nickname, since their top role is higher than my top role.",color = discord.Color.red()),mention_author = False)
        else:
            await member.edit(nick=nickname)
            await ctx.reply(embed = discord.Embed(description = f"Edited {member}'s nickname to: `{nickname}`",color = discord.Color.green()),mention_author = False)

    @commands.command(help = "Give/remove a role to someone else.")
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

    @commands.command(aliases = ['k'],help = "Kick a member from the server.")
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

    @commands.command(aliases = ['b'],help = "Ban a member from the server")
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

    @commands.command(aliases = ['mb'],help = "Mass ban members from the server")
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

    @commands.command(help = "Unban a member from the server.")
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

        
def setup(client):
    client.add_cog(Mod(client))