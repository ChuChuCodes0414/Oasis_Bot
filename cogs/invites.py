import discord
import DiscordUtils
from discord.ext import commands
import firebase_admin
from firebase_admin import db
from datetime import datetime

class Invites(commands.Cog):
    '''
        Tracks invites for your server, and logs them too. Note this cannot track vanity invites.
        \n**Setup for this Category**
        Invite Log: `o!settings set invitelog <channel>` 
    '''
    def __init__(self, client):
        self.client = client
        self.tracker = DiscordUtils.InviteTracker(client)

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
        now = datetime.now()
        diff = now - date
        formatcreate = date.strftime("%b %d %Y %H:%M:%S")
        accountage = f"{diff.days} Days Old"

        build += f"**Member Joining Information:** {member.mention} ( `{member.id}` )\n"
        if diff.days <= 30:
            build += f"**⚠ This Account is Under 30 days Old! ⚠**\n**Account Creation Date:** {formatcreate}\n**Account Age:** {accountage}\n"
        else:
            build += f"**Account Creation Date:** {formatcreate}\n**Account Age:** {accountage}\n"

        if inviter:
            build += f"**Invited By:** {inviter.mention} ( `{inviter.id} `)"
        else:
            build += f"**I could not trace how this member joined! Perhaps they joined through a vanity invite, or temporary link.**"
        
        emb = discord.Embed(title=f"{member} has Joined the Server!",description = f"{build}",
                                color=discord.Color.green())
        emb.timestamp = datetime.utcnow()
        emb.set_footer(text = f'Oasis Bot Invite Tracking',icon_url = member.guild.icon_url)

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
        joined = member.joined_at.strftime("%Y-%m-%d %H:%M")
        build += f"**Member Leaving Information:** {member.mention} ( `{member.id}` )\n"
        build += f"**Joined at:** {joined} ({(datetime.utcnow() - member.joined_at).days} days ago)\n"
        if inviter:
            build += f"**Invited By:** {inviter.mention} (`{inviter.id}`)"
        else:
            build += f"**I could not trace how this member joined! Perhaps they joined through a vanity invite, or temporary link.**"
        
        emb = discord.Embed(title=f"{member} has left the Server!",description = f"{build}",
                                color=discord.Color.red())
        emb.timestamp = datetime.utcnow()
        emb.set_footer(text = f'Oasis Bot Invite Tracking',icon_url = member.guild.icon_url)

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

        if not memberdata:
            data = {'invited':inviter.id}
            ref.child(str(member.guild.id)).child(str(member.id)).set(data)
        else:
            ref.child(str(member.guild.id)).child(str(member.id)).child("invited").set(inviter.id)

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
    
    @commands.Cog.listener()
    async def on_member_remove(self,member):
        inviteruser = None
        ref = db.reference("/",app = firebase_admin._apps['invites'])

        memberdata = ref.child(str(member.guild.id)).child(str(member.id)).get() # member who got invited data

        if memberdata:
            inviter = memberdata.get("invited",None)
            if inviter:
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

                

        if memberdata:
            ref.child(str(member.guild.id)).child(str(member.id)).delete()
        await self.log_invite_leave(member,inviteruser)


    @commands.command(hidden = True)
    @commands.is_owner()
    async def cacheinvites(self,ctx):
        await self.tracker.cache_invites()
        await ctx.reply("Cached Invites")

    @commands.command(description = "How many invites do you have? And who invited you?",help = "invites [member]")
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

        if invitedby:
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
        emb.timestamp = datetime.utcnow()
        emb.set_footer(text = f'Oasis Bot Invite Tracking',icon_url = member.guild.icon_url)

        await ctx.send(embed = emb)
        

        
def setup(client):
    client.add_cog(Invites(client))
    