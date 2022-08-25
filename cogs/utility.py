import discord
from discord.ext import commands
from discord import app_commands
import firebase_admin
from firebase_admin import db
import datetime
import asyncio
import pytz

class Utility(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.short = "🛠 | Utility"
        ref = db.reference("/",app = firebase_admin._apps['afk'])
        self.cache = ref.get() or {} 
        self.active = {}
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        for guild,data in ref.get().items():
            if data.get("bumpchannel",None):
                self.active[str(guild)] = str(data.get("bumpchannel"))
        self.ctx_menu = app_commands.ContextMenu(
            name='Member Info',
            callback=self.contextmemberinfo,
        )
        self.client.tree.add_command(self.ctx_menu)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Utility Cog Loaded.')

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.id == 302050872383242240 and str(message.channel.id) == self.active.get(str(message.guild.id),None):
            if len(message.embeds) > 0:
                dict = message.embeds[0].to_dict()
                if dict["description"].startswith("Bump done!"):
                    overwrite = message.channel.overwrites_for(message.guild.default_role)
                    overwrite.send_messages = False
                    await message.channel.set_permissions(message.guild.default_role, overwrite=overwrite)
                    await message.channel.send(embed = discord.Embed(description = f"Thank you for bumping! Make sure to leave a review at [https://disboard.org/server/{message.guild.id}](https://disboard.org/server/{message.guild.id})",color = discord.Color.random()))
                    await asyncio.sleep(7200)
                    overwrite = message.channel.overwrites_for(message.guild.default_role)
                    overwrite.send_messages = None
                    await message.channel.set_permissions(message.guild.default_role, overwrite=overwrite)
                    ref = db.reference("/",app = firebase_admin._apps['settings'])
                    ping = ref.child(str(message.guild.id)).child("bumpping").get()
                    if ping:
                        await message.channel.send(f"<@&{ping}>",embed = discord.Embed(description = f"It has been 2 hours since the last successful bump, could someone run `/bump`?",color = discord.Color.random()))
                    else:
                        await message.channel.send(embed = discord.Embed(description = f"It has been 2 hours since the last successful bump, could someone run `/bump`?",color = discord.Color.random()))
            return
        if message.author.bot:
            return
        if self.cache.get(str(message.guild.id),{}).get(str(message.author.id),None) and not self.cache.get(str(message.guild.id)).get(str(message.author.id)).get("invulnerable"):
            self.cache[str(message.guild.id)].pop(str(message.author.id))
            ref = db.reference("/",app = firebase_admin._apps['afk'])
            ref.child(str(message.guild.id)).child(str(message.author.id)).delete()
            if message.author.nick and message.author.nick.startswith("[AFK]"):
                try:
                    await message.author.edit(nick = message.author.nick[6:])
                except:
                    pass
            await message.reply(embed = discord.Embed(description = f"Welcome back **{message.author}**! I have removed your afk."),delete_after = 5)
        build = ""
        remove = []
        for mention in message.mentions:
            if str(mention.id) in self.cache.get(str(message.guild.id),{}) and not self.cache.get(str(message.guild.id),{}).get(str(mention.id)).get("cooldown"):
                build += f"**{mention}** is afk: {self.cache[str(message.guild.id)][str(mention.id)]['message']} (<t:{self.cache[str(message.guild.id)][str(mention.id)]['time']}:R>)\n"
                self.cache[str(message.guild.id)][str(mention.id)]["cooldown"] = True
                remove.append(mention)
        if build != "":
            await message.reply(embed = discord.Embed(description = build),delete_after = 5)
        await asyncio.sleep(10)
        for mention in remove:
            self.cache[str(message.guild.id)][str(mention.id)].pop("cooldown")

    @commands.hybrid_command(name= "memberinfo",help = "View some basic information about a member.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The user to lookup information for.")
    async def memberinfo(self, ctx: commands.Context, member: discord.Member = None) -> None:
        member = member or ctx.author
        embed = discord.Embed(title = f"Member Information for {member}",description = f"{member.id} | {member.display_name}",color = member.color)
        embed.add_field(name = "Account Creation:",value = f"<t:{int(member.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:f> (<t:{int(member.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:R>)",inline = False)
        embed.add_field(name = "Joined At",value = f"<t:{int(member.joined_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:f> (<t:{int(member.joined_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:R>)",inline = False)
        embed.add_field(name = "Top Role",value = member.top_role.mention)
        embed.add_field(name = "Top 20 Roles",value = " ".join([x.mention for x in list(reversed(member.roles))[0:min(len(member.roles),20)]]))
        embed.set_thumbnail(url = member.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        await ctx.reply(embed = embed)
    
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def contextmemberinfo(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
        embed = discord.Embed(title = f"Member Information for {member}",description = f"{member.id} | {member.display_name}",color = member.color)
        embed.add_field(name = "Account Creation:",value = f"<t:{int(member.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:f> (<t:{int(member.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:R>)",inline = False)
        embed.add_field(name = "Joined At",value = f"<t:{int(member.joined_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:f> (<t:{int(member.joined_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:R>)",inline = False)
        embed.add_field(name = "Top Role",value = member.top_role.mention)
        embed.add_field(name = "Top 20 Roles",value = " ".join([x.mention for x in list(reversed(member.roles))[0:min(len(member.roles),20)]]))
        embed.set_thumbnail(url = member.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        await interaction.response.send_message(embed = embed,ephemeral = True)
    
    @commands.hybrid_command(name = "serverinfo",help = "View some basic information about the current server.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def serverinfo(self, ctx: commands.Context) -> None:
        embed = discord.Embed(title = f"Server Information for {ctx.guild.name}",description = ctx.guild.id,color = discord.Color.random())
        embed.add_field(name = "Creation Date",value = f"<t:{int(ctx.guild.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:f> (<t:{int(ctx.guild.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:R>)",inline = False)
        embed.add_field(name = "Server Owner",value = ctx.guild.owner)
        embed.add_field(name = "Vanity Invite",value = ctx.guild.vanity_url_code)
        embed.add_field(name = "Boost Status",value = f"Level {ctx.guild.premium_tier}\n{ctx.guild.premium_subscription_count} Boosts")
        embed.add_field(name = "Channel Statistics",value = f"{len(ctx.guild.text_channels)} Text Channels\n{len(ctx.guild.voice_channels)} Voice Channels")
        humans = len([m for m in ctx.guild.members if not m.bot])
        bots = ctx.guild.member_count-humans
        embed.add_field(name = "Member Statistics",value = f"Total Members: {len(ctx.guild.members)}\nHumans: {humans}\nBots: {bots}")
        embed.set_thumbnail(url = ctx.guild.icon)
        embed.timestamp = datetime.datetime.now()
        await ctx.reply(embed = embed)
    
    @commands.hybrid_command(name = "whois",help = "View some basic information for any discord user.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(user = "The user to lookup information for.")
    async def whois(self, ctx: commands.Context, user: discord.User = None) -> None:
        user = user or ctx.author
        embed = discord.Embed(title = f"User information for {user}",description = user.id,color = user.color)
        embed.add_field(name = "Account Creation:",value = f"<t:{int(user.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:f> (<t:{int(user.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:R>)",inline = False)
        mutuals = '\n'.join([x.name for x in user.mutual_guilds[:min(len(user.mutual_guilds),20)]])
        embed.add_field(name = "Mutual Servers",value = f"{len(user.mutual_guilds)} Mutuals\n{mutuals}")
        embed.set_thumbnail(url = user.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        await ctx.reply(embed = embed)
    
    @commands.hybrid_group(name = "afk")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def afk(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help afk` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)
    
    @afk.command(name = "set",help = "Set your server afk to let other people know you aren't there!")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(message = "The message to be displayed if someone mentions you.")
    async def set(self, ctx: commands.Context, *,message: str = None) -> None:
        message = message or "AFK"
        ref = db.reference("/",app = firebase_admin._apps['afk'])
        current = ref.child(str(ctx.guild.id)).child(str(ctx.author.id)).get()
        if current:
            ref.child(str(ctx.guild.id)).child(str(ctx.author.id)).child("message").set(message)
            self.cache[str(ctx.guild.id)][str(ctx.author.id)]["message"] = message
            self.cache[str(ctx.guild.id)][str(ctx.author.id)]["invlunerable"] = True
            await ctx.reply(embed = discord.Embed(description = f"I have updated your afk message to: {message}",color = discord.Color.green()),ephemeral = True)
            await asyncio.sleep(10)
            self.cache[str(ctx.guild.id)][str(ctx.author.id)].pop("invulnerable")
        else:
            ref.child(str(ctx.guild.id)).child(str(ctx.author.id)).set({"message":message,"time":int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())})
            if self.cache.get(str(ctx.guild.id)):
                self.cache[str(ctx.guild.id)][str(ctx.author.id)] = {"message":message,"time":int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())}
            else:
                self.cache[str(ctx.guild.id)] = {str(ctx.author.id):{"message":message,"time":int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())}}
            self.cache[str(ctx.guild.id)][str(ctx.author.id)]["invulnerable"] = True
            try:
                await ctx.author.edit(nick= "[AFK] " + ctx.author.display_name)
            except:
                pass
            await ctx.reply(embed = discord.Embed(description = f"I have set your afk to: {message}",color = discord.Color.green()))
            await asyncio.sleep(10)
            self.cache[str(ctx.guild.id)][str(ctx.author.id)].pop("invulnerable")

    
    @afk.command(name = "remove",help = "As a moderator, remove the afk of a member.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The member to remove the afk from.")
    @commands.has_permissions(moderate_members = True)
    async def remove(self, ctx: commands.Context, member: discord.Member) -> None:
        if str(member.id) in self.cache.get(str(ctx.guild.id),{}):
            ref = db.reference("/",app = firebase_admin._apps['afk'])
            self.cache[str(ctx.guild.id)].pop(str(member.id))
            ref.child(str(ctx.guild.id)).child(str(member.id)).delete()
            await ctx.reply(embed = discord.Embed(description = f"I have removed the afk status for **{member}**!",color = discord.Color.green()),ephemeral = True)
        else:
            await ctx.reply(embed = discord.Embed(description = f"**{member}** does not have an afk status set!",color = discord.Color.red()),ephemeral = True)

    @commands.hybrid_group(name = "time")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def time(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help time` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)
    
    @time.command(name = "set",help = "Set up your timezone in the bot.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(timezone = "Your timezone in tz database format.")
    async def timeset(self,ctx:commands.Context,timezone: str):
        if timezone not in pytz.all_timezones:
            return await ctx.reply(embed = discord.Embed(description = "I do not recognize that timezone! Please see [this page](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for a list of valid timezones.",color = discord.Color.red()),ephemeral = True)
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        ref.child(str(ctx.author.id)).child("timezone").set(timezone)
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        there_now = utc_now.astimezone(pytz.timezone(timezone))
        await ctx.reply(embed = discord.Embed(description = f"I have set your timezone as **{timezone}**, where it should be **{there_now.strftime('%A, %B %d, %Y %I:%M %p (utc%z)')}**",color = discord.Color.green()))

    @time.command(name = "me",help = "Check your own time, even though you could look at a clock nearby.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def timeme(self,ctx:commands.Context):
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        timezone = ref.child(str(ctx.author.id)).child("timezone").get()
        
        if not timezone:
            return await ctx.reply(embed = discord.Embed(description = "Your timezone is not setup! Use `/time set` first to get started.",color = discord.Color.red()))

        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        there_now = utc_now.astimezone(pytz.timezone(timezone))
        await ctx.reply(embed = discord.Embed(description = f"For **{ctx.author}** in **{timezone}**\nIt is currently **{there_now.strftime('%A, %B %d, %Y %I:%M %p (utc%z)')}**\nYour Local Time: <t:{int(utc_now.replace(tzinfo=datetime.timezone.utc).timestamp())}:F>",color = discord.Color.green()))

    @time.command(name = "check",help = "Check someone else's time, because they need to go to bed.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The member to check the time of.")
    async def timecheck(self,ctx:commands.Context, member: discord.Member):
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        timezone = ref.child(str(member.id)).child("timezone").get()
        
        if not timezone:
            return await ctx.reply(embed = discord.Embed(description = f"**{member}'s** timezone is not setup! Tell them to use `/time set` first to get started.",color = discord.Color.red()))

        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        there_now = utc_now.astimezone(pytz.timezone(timezone))
        await ctx.reply(embed = discord.Embed(description = f"For **{member}** in **{timezone}**\nIt is currently **{there_now.strftime('%A, %B %d, %Y %I:%M %p (utc%z)')}**\nYour Local Time: <t:{int(utc_now.replace(tzinfo=datetime.timezone.utc).timestamp())}:F>",color = discord.Color.green()))

async def setup(client):
    await client.add_cog(Utility(client))