import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import db
import datetime

class Freeloader(commands.Cog):
    """
        Tracking for freeloaders for dank memer heists, via checking the heist result messages. All commands require a mod role.
        \n**Setup for this Category**
        Mod Role: `o!settings add mod <role>` 
        Freeloader Logging Channel: `o!settings set freeloaderlog <channel>`
    """
    
    def __init__(self,client):
        self.client = client
        self.tracking = {}
        self.info = {'joiners' : [None],'leavers' : 0,'tracking' : True,'channeltrack':False,'freeloaders':[]}
        self.messagecache = {}
        self.channelcache = []
        self.guildcache = []


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
    async def on_ready(self):
        ref = db.reference("/",app = firebase_admin._apps['freeloader'])
        data = ref.get()
        for guild,guilddata in data.items():
            if guilddata.get("tracking",False) == True:
                self.guildcache.append(int(guild))
                self.channelcache.append(int(guilddata.get("channeltrack")))

        print('Freeloader Cog Loaded.')
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def cachefreeloader(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['freeloader'])
        data = ref.get()
        for guild,guilddata in data.items():
            if guilddata.get("tracking",False) == True:
                self.guildcache.append(int(guild))
                self.channelcache.append(int(guilddata.get("channeltrack")))
            if guilddata.get("messageid",None):
                guild = self.client.get_guild(int(guild))
                if not guild:
                    continue
                try:
                    messageob = self.messagecache[str(guild.id)]
                except:
                    messageob = None
                if not messageob:
                    channel = ref.child(str(guild.id)).child("channeltrack").get()
                    channel = guild.get_channel(int(channel))
                    messages = ref.child(str(guild.id)).child("messageid").get() or []
                    messageob = []
                    for message in messages:
                        try:
                            messageob.append(await channel.fetch_message(int(message)))
                        except:
                            continue
                    self.messagecache[str(guild.id)] = messageob
                    await ctx.send(f"Messages cached for {guild.id}")

        await ctx.send(self.guildcache)
        await ctx.send(self.channelcache)

    @commands.Cog.listener()
    async def on_member_join(self,member):
        if member.guild.id in self.guildcache:
            ref = db.reference("/",app = firebase_admin._apps['freeloader'])
            joiners = ref.child(str(member.guild.id)).child('joiners').get()
            if joiners:
                joiners.append(member.id)
            else:
                joiners = [member.id]
            ref.child(str(member.guild.id)).child('joiners').set(joiners)

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        if member.guild.id in self.guildcache:
            ref = db.reference("/",app = firebase_admin._apps['freeloader'])
            ref2 = db.reference("/",app = firebase_admin._apps['settings'])
            leavers = ref.child(str(member.guild.id)).child('leavers').get() or 0 
            username = member.name

            try:
                messageob = self.messagecache[str(member.guild.id)]
            except:
                messageob = None
            if not messageob:
                channel = ref.child(str(member.guild.id)).child("channeltrack").get()
                channel = member.guild.get_channel(int(channel))
                messages = ref.child(str(member.guild.id)).child("messageid").get() or []
                messageob = []
                for message in messages:
                    try:
                        messageob.append(await channel.fetch_message(int(message)))
                    except:
                        continue
                self.messagecache[str(member.guild.id)] = messageob
            
            for message in messageob:
                try:
                    content = message.content
                except:
                    continue
                if f'+ {username} '  in content or f'- {username} ' in content or f'# {username}' in content:
                    freeloaders = ref.child(str(member.guild.id)).child("freeloaders").get() or []
                    freeloaders.append(member.id)
                    ref.child(str(member.guild.id)).child("freeloaders").set(freeloaders)
                    log = ref2.child(str(member.guild.id)).child('flogging').get()
                    if log:
                        embed=discord.Embed(title=f"⚠ Alert For {member}",description=f"`This user is likely a freeloader!`", color=discord.Color.red())
                        embed.set_thumbnail(url = member.avatar_url)
                        embed.add_field(name = "User Information",value = f'{member.id}\n{member.mention}',inline = True)
                        embed.add_field(name = "Heist Joining Information",value = f'[Link to Result Message]({message.jump_url})',inline = False)
                        embed.timestamp = datetime.datetime.utcnow()
                        embed.set_footer(text = f'Oasis Bot Freeloader Tracking',icon_url = member.guild.icon_url)
                        channel = member.guild.get_channel(log)
                        
                        await channel.send(embed = embed)
                    break

            ref.child(str(member.guild.id)).child('leavers').set(leavers + 1)

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.guild and message.author.id == 570013288977530880 and message.channel.id in self.channelcache and message.guild.id in self.guildcache:
                if str(message.content).startswith('```'):
                    ref = db.reference("/",app = firebase_admin._apps['freeloader'])
                    ids = ref.child(str(message.guild.id)).child('messageid').get() or []
                    ids.append(message.id)
                    ref.child(str(message.guild.id)).child('messageid').set(ids)
                    try:
                        self.messagecache[str(message.guild.id)].append(message)
                    except:
                        self.messagecache[str(message.guild.id)] = [message]
                elif str(message.content).startswith('Amazing job everybody, we racked up a total of'):
                    ref = db.reference("/",app = firebase_admin._apps['freeloader'])
                    ref.child(str(message.guild.id)).child('leavers').set(0)
                    ref.child(str(message.guild.id)).child('joiners').set([])
                 

    @commands.command(description = "Start tracking for freeloaders",help = "track [channel]")
    @mod_role_check()
    async def track(self,ctx,channel:discord.TextChannel=None):
        if ctx.guild.id in self.guildcache:
            await ctx.reply("You need to stop tracking a channel for this guild first with `[prefix]stoptrack`.")
        channel = channel or ctx.channel

        store = self.info.copy()

        store['channeltrack'] = channel.id
        self.channelcache.append(channel.id)
        self.guildcache.append(ctx.guild.id)
        ref = db.reference("/",app = firebase_admin._apps['freeloader'])
        ref.child(str(ctx.message.guild.id)).set(store)

        await ctx.reply(f"<a:PB_greentick:865758752379240448> Now checking for freeloaders in {channel.mention}!")

    @commands.command(description = "Stop tracking for freeloaders",help = "stoptrack [channel]")
    @mod_role_check()
    async def stoptrack(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        if ctx.guild.id not in self.guildcache or channel.id not in self.channelcache:
            return await ctx.send("Don't think you were tracking there in the first place.")
        ref = db.reference("/",app = firebase_admin._apps['freeloader'])
        ref.child(str(ctx.message.guild.id)).child("tracking").set(False)
        self.guildcache.remove(ctx.guild.id)
        self.channelcache.remove(channel.id)
        try:
            self.channelcache.remove(ctx.channel.id)
        except:
            pass
        await ctx.reply(f"<a:PB_greentick:865758752379240448> No longer checking for freeloaders!")

    @commands.command(description = "Embed showing statistics about freeloaders.",help = "freeloaders",brief = "This command pulls up an embed showing statistics. A 'freeloading member' is someone who joins within the tracking period, joins the heist, and leaves within the tracking period."
            +" A 'potential freeloader' is someone who joins the heist and leaves within the tracking period, but does not join within the tracking period. More statistics are also shown below the embed.")
    @mod_role_check()
    async def freeloaders(self,ctx):
        suspects = ""
        potentials = ""
        ref = db.reference("/",app = firebase_admin._apps['freeloader'])
        leavers = ref.child(str(ctx.message.guild.id)).child('leavers').get()
        joiners = ref.child(str(ctx.message.guild.id)).child('joiners').get()
        freeloaders = ref.child(str(ctx.message.guild.id)).child("freeloaders").get()
        messages = self.messagecache.get(str(ctx.guild.id),[]) 
        channel = ref.child(str(ctx.message.guild.id)).child('channeltrack').get()
        tracking  = ref.child(str(ctx.message.guild.id)).child('tracking').get()

        if freeloaders:
            if len(freeloaders) >= 20:
                stop = 21
            else:
                stop = len(freeloaders)
            for freeloader in freeloaders[:stop]:
                if joiners:
                    if freeloader in joiners:
                        suspects += str(freeloader) + "\n"
                    else:
                        potentials += str(freeloader) + "\n"
                else:
                    potentials += str(freeloader) + "\n"
    

        if suspects == "":
            suspects = "None"
        
        if potentials == "":
            potentials = "None"

        if not channel:
            channel = "Not Tracking"
        else:
            channel = "<#" + str(channel) + ">"

        if not joiners:
            amountjoin = 0
        else:
            amountjoin = len(joiners)

        if messages:
            messageamount = len(messages)
        else:
            messageamount = 0


        if not leavers:
            amountleavers = 0
        else:
            amountleavers = leavers
        
        embed=discord.Embed(title="Potential Freeloaders <a:freeloader:888104716104515654>",description=f"List of potential freeloaders from the heist", color=discord.Color.red())
        embed.add_field(name="Freeloading Members",value=suspects,inline=False)
        embed.add_field(name="Potential Freeloaders",value=potentials,inline = False)
        embed.add_field(name="Other Statistics",value = f'New Member Count: {amountjoin}\nPeople Leaving After Heist: {amountleavers}\nLooking for Heist Messages in: {channel}\nTracking Messages: {messageamount}\nTracking: {tracking}')

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=embed)

    @commands.command(description = "Embed showing who has joined the server within tracking period.",help = "joiners")
    @mod_role_check()
    async def joiners(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['freeloader'])
        joiners = ref.child(str(ctx.message.guild.id)).child('joiners').get()

        if not joiners:
            return await ctx.send("Hmmm, seems like no one has joined yet.")

        build = ""
        if len(joiners) >= 30:
            stop = 31
        else:
            stop = len(joiners)
        for person in joiners[:stop]:
            build += f"{person}\n"
    
        embed=discord.Embed(title="Server Joiners",description=f"List of most recent 30 people who have joined server within tracking period", color=discord.Color.green())
        embed.add_field(name="Joiners",value=build,inline=False)

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)

        await ctx.reply(embed = embed)

def setup(client):
    client.add_cog(Freeloader(client))
