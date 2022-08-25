import discord
from discord.ext import commands
from discord import app_commands
import firebase_admin
from firebase_admin import db
from discord.errors import Forbidden
from discord import AuditLogAction
import datetime
from asyncio import sleep
import time

class InviteTracking(commands.Cog):
    '''
        Tracks invites for your server, and logs them too. Note this cannot track vanity invites.
        \n**Setup for this Category**
        Invite Log: `o!settings set invitelog <channel>` 
    '''
    def __init__(self, client):
        self.short = "<:invite:950957804544471080> | Invite Tracking"
        self.client = client
        self.tracker = InviteTracker(client)

    async def log_invite_join(self,member,inviter = None):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        channelid = ref.child(str(member.guild.id)).child("ilogging").get()    

        if not channelid:
            return
        channel = member.guild.get_channel(int(channelid))

        if not channel:
            return

        build = ""
        date = member.created_at
        now = datetime.datetime.now(datetime.timezone.utc)
        diff = now - date
        unix = time.mktime(date.timetuple())
        formatted = "<t:" + str(int(unix)) + ":F>"
        formatted2 = "<t:" + str(int(unix)) + ":R>"
        build += f"**Member Joining Information:** {member.mention} ( `{member.id}` )\n"
        if diff.days <= 30:
            build += f"**⚠ This Account is Under 30 days Old! ⚠**\n**Account Creation Date:** {formatted}\n**Account Age:** {formatted2}\n"
        else:
            build += f"**Account Creation Date:** {formatted}\n**Account Age:** {formatted2}\n"

        if inviter and inviter == "vanity":
            build += f"**Invited By:** Vanity Link"
        elif inviter:
            build += f"**Invited By:** {inviter.mention} ( `{inviter.id} `)"
        else:
            build += f"**I could not trace how this member joined! Perhaps they joined through temporary link.**"
        
        emb = discord.Embed(title=f"{member} has Joined the Server!",description = f"{build}",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'OAsis Bot Invite Tracking',icon_url = member.guild.icon)

        await channel.send(embed = emb)

    async def log_invite_leave(self,member,inviter = None):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        channelid = ref.child(str(member.guild.id)).child("ilogging").get()   

        if not channelid:
            return
                
        channel = member.guild.get_channel(int(channelid))

        if not channel:
            return

        build = ""
        date = member.joined_at
        unix = time.mktime(date.timetuple())
        formatted = "<t:" + str(int(unix)) + ":F>"
        build += f"**Member Leaving Information:** {member.mention} ( `{member.id}` )\n"
        timedelta = datetime.datetime.now(datetime.timezone.utc) - member.joined_at
        if timedelta.days >= 7:
            build += f"**Joined at:** {formatted} ({timedelta.days//7} weeks ago)\n"
        elif timedelta.days >= 1:
            build += f"**Joined at:** {formatted} ({timedelta.days} days ago)\n"
        elif timedelta.seconds >= 3600:
            build += f"**Joined at:** {formatted} ({timedelta.seconds//3600} hours ago)\n"
        elif timedelta.seconds >= 60:
            build += f"**Joined at:** {formatted} ({timedelta.seconds//60} minutes ago)\n"
        else:
            build += f"**Joined at:** {formatted} (under one minute ago)\n"

        if inviter and inviter == "vanity":
            build += f"**Invited By:** Vanity Link"
        elif inviter:
            build += f"**Invited By:** {inviter.mention} (`{inviter.id}`)"
        else:
            build += f"**I could not trace how this member joined! Perhaps they joined through a temporary link.**"
        
        emb = discord.Embed(title=f"{member} has left the Server!",description = f"{build}",
                                color=discord.Color.red())
        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'Oasis Bot Invite Tracking',icon_url = member.guild.icon)

        await channel.send(embed = emb)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.tracker.cache_invites()
        print('Invite Cog Loaded.')

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.tracker.update_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.tracker.add_guild_cache(guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            inviter = await self.tracker.fetch_inviter(member)  # inviter is the member who invited
        except:
            return await self.log_invite_join(member)

        if not inviter:
            return await self.log_invite_join(member)

        ref = db.reference("/",app = firebase_admin._apps['invites'])

        memberdata = ref.child(str(member.guild.id)).child(str(member.id)).get() # member who got invited data

        if inviter == "vanity" and not memberdata:
            data = {'invited':"vanity"}
            ref.child(str(member.guild.id)).child(str(member.id)).set(data)
        elif inviter == "vanity" and memberdata:
            ref.child(str(member.guild.id)).child(str(member.id)).child("invited").set("vanity")
        elif not memberdata:
            data = {'invited':inviter.id}
            ref.child(str(member.guild.id)).child(str(member.id)).set(data)
        else:
            ref.child(str(member.guild.id)).child(str(member.id)).child("invited").set(inviter.id)

        if not inviter == "vanity":        
            inviterdata = ref.child(str(member.guild.id)).child(str(inviter.id)).get() # invter data

            if not inviterdata:
                data = {'invites':[member.id]}
                ref.child(str(member.guild.id)).child(str(inviter.id)).set(data)
            else:
                leaves = inviterdata.get("leaves",[])
                invites = inviterdata.get("invites",[])

                if not member.id in invites:
                    invites.append(member.id)
                
                if member.id in leaves:
                    leaves.remove(member.id)
                    ref.child(str(member.guild.id)).child(str(inviter.id)).child("leaves").set(leaves)

                ref.child(str(member.guild.id)).child(str(inviter.id)).child("invites").set(invites)

            await self.log_invite_join(member,inviter)
        else:
            await self.log_invite_join(member,"vanity")
    
    @commands.Cog.listener()
    async def on_member_remove(self,member):
        inviteruser = None
        ref = db.reference("/",app = firebase_admin._apps['invites'])

        memberdata = ref.child(str(member.guild.id)).child(str(member.id)).get() # member who got invited data

        if memberdata:
            inviter = memberdata.get("invited",None)
            if inviter and not inviter == "vanity":
                inviteruser = await self.client.fetch_user(int(inviter))
                inviterdata = ref.child(str(member.guild.id)).child(str(inviter)).get()
                if inviterdata:
                    inviteslist = inviterdata.get("invites",None)

                    if inviteslist:
                        try:
                            inviteslist.remove(member.id)
                            inviterdata["invites"] = inviteslist
                        except:
                            pass
                    leaves = inviterdata.get("leaves",None)

                    if leaves and member.id not in leaves:
                        leaves.append(member.id)
                    else:
                        leaves = [member.id]

                    inviterdata["leaves"] = leaves
                    
                    ref.child(str(member.guild.id)).child(str(inviter)).set(inviterdata)
        else:
            inviter = None

        if memberdata:
            ref.child(str(member.guild.id)).child(str(member.id)).delete()
        if inviter and inviter == "vanity":
            await self.log_invite_leave(member,"vanity")
        else:
            await self.log_invite_leave(member,inviteruser)

    @commands.command(hidden = True)
    @commands.is_owner()
    async def cacheinvites(self,ctx):
        await self.tracker.cache_invites()
        await ctx.reply("Cached Invites")

    @commands.hybrid_command(name= "invites",help = "View who invited a member, as well as their invite count.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The user to lookup information for.")
    async def invites(self,ctx,member:discord.Member = None):
        ref = db.reference("/",app = firebase_admin._apps['invites'])

        member = member or ctx.author

        invitedby = ref.child(str(member.guild.id)).child(str(member.id)).child("invited").get()
        invites = ref.child(str(member.guild.id)).child(str(member.id)).child("invites").get()
        leaves = ref.child(str(member.guild.id)).child(str(member.id)).child("leaves").get()

        if invites:
            invites = len(invites)

        if leaves:
            leaves = len(leaves)

        if invitedby and invitedby == "vanity":
            invitedby = "Vanity Invite"
            user = None
        elif invitedby:
            user = await self.client.fetch_user(int(invitedby))
        else:
            user = None

        emb = discord.Embed(title=f"{member} Invite Information",description = f"{member.mention} (`{member.id}`)",
                                color=discord.Color.random())

        if user:
            emb.add_field(name = "Invited By:",value = f"{user.mention} | {user} (`{user.id}`)",inline = False)
        elif invitedby:
            emb.add_field(name = "Invited By:",value = f"`{invitedby}`",inline = False)
        else:
            emb.add_field(name = "Invited By:",value = f"No Data",inline = False)

        emb.add_field(name = "Invites:",value = f"`{invites}`")
        emb.add_field(name = "Leaves:",value = f"`{leaves}`")
        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'Oasis Bot Invite Tracking',icon_url = member.guild.icon)

        await ctx.send(embed = emb)
        
async def setup(client):
    await client.add_cog(InviteTracking(client))

class InviteTracker():
    def __init__(self, bot):
        self.bot = bot
        self._cache = {}
        self.add_listeners()
    
    def add_listeners(self):
        self.bot.add_listener(self.cache_invites, "on_ready")
        self.bot.add_listener(self.update_invite_cache, "on_invite_create")
        self.bot.add_listener(self.remove_invite_cache, "on_invite_delete")
        self.bot.add_listener(self.add_guild_cache, "on_guild_join")
        self.bot.add_listener(self.remove_guild_cache, "on_guild_remove")
    
    async def cache_invites(self):
        for guild in self.bot.guilds:
            try:
                self._cache[guild.id] = {}
                for invite in await guild.invites():
                    self._cache[guild.id][invite.code] = invite
                try:
                    vanity = await guild.vanity_invite()
                    self._cache[guild.id]['vanity'] = vanity
                except Forbidden:
                    continue
            except Forbidden:
                continue
    
    async def update_invite_cache(self, invite):
        if invite.guild.id not in self._cache.keys():
            self._cache[invite.guild.id] = {}
        self._cache[invite.guild.id][invite.code] = invite
    
    async def remove_invite_cache(self, invite):
        if invite.guild.id not in self._cache.keys():
            return
        ref_invite = self._cache[invite.guild.id][invite.code]
        if (ref_invite.created_at.timestamp()+ref_invite.max_age > datetime.datetime.now().timestamp() or ref_invite.max_age == 0) and ref_invite.max_uses > 0 and ref_invite.uses == ref_invite.max_uses-1:
            try:
                async for entry in invite.guild.audit_logs(limit=1, action=AuditLogAction.invite_delete):
                    if entry.target.code != invite.code:
                        self._cache[invite.guild.id][ref_invite.code].revoked = True
                        return
                else:
                    self._cache[invite.guild.id][ref_invite.code].revoked = True
                    return
            except Forbidden:
                self._cache[invite.guild.id][ref_invite.code].revoked = True
                return
        else:
            self._cache[invite.guild.id].pop(invite.code)
    
    async def add_guild_cache(self, guild):
        self._cache[guild.id] = {}
        for invite in await guild.invites():
            self._cache[guild.id][invite.code] = invite
        try:
            vanity = await guild.vanity_invite()
            self._cache[guild.id]['vanity'] = vanity
        except:
            pass
    
    async def remove_guild_cache(self, guild):
        try:
            self._cache.pop(guild.id)
        except KeyError:
            return
    
    async def fetch_inviter(self, member):
        await sleep(self.bot.latency)
        try:
            vanity = self._cache[member.guild.id]['vanity']
            new_vanity = await member.guild.vanity_invite()
            if new_vanity.uses - vanity.uses == 1:
                self._cache[member.guild.id]['vanity'] = new_vanity
                return "vanity"
        except:
            pass
        for new_invite in await member.guild.invites():
            for cached_invite in self._cache[member.guild.id].values():
                if new_invite.code == cached_invite.code and new_invite.uses > cached_invite.uses or cached_invite.revoked:
                    if cached_invite.revoked:
                        self._cache[member.guild.id].pop(cached_invite.code)
                    elif new_invite.inviter == cached_invite.inviter:
                        self._cache[member.guild.id][cached_invite.code] = new_invite
                    else:
                        self._cache[member.guild.id][cached_invite.code].uses += 1
                    return cached_invite.inviter