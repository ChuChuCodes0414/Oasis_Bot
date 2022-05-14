import discord
import firebase_admin
from firebase_admin import db
import datetime
from utils import timing
from itertools import starmap, chain
from discord.ext import commands, menus
from discord import ui

class EventTracking(commands.Cog):
    """
        This category allows you to track event manager activity. Most commands will require you to set up a role for event managers. You can also setup a channel to log when event is completed.
        \n**Setup for this Category**
        Event Manager Role: `o!settings set eventmanager <role>`
        Event Logging Channel: `o!settings set eventlog <channel>`
    """

    def __init__(self,client):
        self.client = client
        self.eventslist = {
        'greentea': 'Multiplayer game, be the fastest to write a word containing the group of 3 letters indicated.',
        'redtea':'Multiplayer game, find the longest word containing the group of 3 letters indicated.',
        'blacktea':'Multiplayer game, write a word containing the group of 3 letters indicated.',
        'yellowtea':'Multiplayer game, find the largest amount of words containing the group of 3 letters indicated.',
        'mixtea':'Multiplayer game, a mix of all the tea games.',
        'rumble':'React and let the bot stimulate a hunger games scenario, last one standing wins!',
        'mafia': 'Work with your side to ensure that your team wins! Each member receieves a special role, some of which have functions. Use `m.help` for more information.',
        'skribble': 'Test your drawing skills, and try to identify what others are drawing!',
        'uno':'Everyone is dealt cards at the beginning of the match. You can play a card of the same type or color, the person with no cards first wins! Use `uno help` for more information.',
        'fight':'Fight another chosen opponent, or the sponsor, for the prize of the event! Fight details will be specified in the event channel',
        'gartic':'Try to identify the drawing that is shown before everyone else! But be careful, if you fail to identify a round, your game is over!',
        'acro':'Come up with a funny acronym for a set of letters provided, and then vote on which one is the best!',
        'nunchi':'Count up from a number in order, but if you are the second person to say that number you are eliminated!'
        }
        self.short = "<a:event:923046835952697395> | Event Tracking"

    def eman_role_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            
            '''
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            emanrole = ref.child(str(ctx.message.guild.id)).child('event').get()
            emanrole_ob = ctx.message.guild.get_role(emanrole)
            if emanrole_ob in ctx.message.author.roles:
                return True
            else:
                return False
            '''
            return True
            
        return commands.check(predicate)

    def eman_channel_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            else:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            echannel = ref.child(str(ctx.message.guild.id)).child('echannel').get()
            if echannel:
                if ctx.message.channel.id == int(echannel):
                    return True
                else:
                    return False
            return False
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Event Logging Cog Loaded.')

    async def add_log(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child(str(ctx.message.guild.id)).child(str(user)).get() or 0
        ref.child(str(ctx.message.guild.id)).child(str(user)).set(log+1)
        return log + 1

    async def set_log(self,ctx,user,amount):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        ref.child(str(ctx.message.guild.id)).child(str(user)).set(amount)
        return amount

    async def remove_log(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        try:
            ref.child(str(ctx.guild.id)).child(str(user)).delete()
        except:
            return False
        return True

    async def get_leaderboard(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child(str(ctx.message.guild.id)).get()
        if log:
            return sorted(log, key=log.get, reverse=True) , log
        else:
            return {},{}

    async def get_amount(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child(str(ctx.message.guild.id)).child(str(user)).get() or 0
        return log

    async def ping_event(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        ping = ref.child(str(ctx.message.guild.id)).child('eping').get() 
        return ping

    async def post_log(self,ctx,channel,message,type,prize,donor):
        emb = discord.Embed(title=f"Event Recorded for {ctx.message.author.name}",description = f"{ctx.message.author.mention}",
                                color=discord.Color.random())
        emb.add_field(name = "Event information:",value = f"[Link to Event]({message.jump_url})\nEvent Type: {type}\nEvent Prize: {prize}\nEvent Donor: {donor}")

        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'Oasis Bot Event Logging',icon_url = ctx.message.channel.guild.icon)
        await channel.send(embed = emb)

    @commands.command(help = "Start an event with a ping and an embed. Will also increment your log tracking by one.")
    @eman_role_check()
    @eman_channel_check()
    async def estart(self,ctx,time,*,values = "event/reqruirement/amount/channel/donor/message"):
        try:
            event,requirement,amount,location,donor,message = values.split("/")
        except:
            raise commands.UserInputError

        await ctx.message.delete()

        channel = await commands.converter.TextChannelConverter().convert(ctx,location.strip())
        donor = await commands.converter.MemberConverter().convert(ctx,donor.strip())

        if event in self.eventslist.keys():
            eventinfo = self.eventslist[event]
        else:
            eventinfo = event

        timebuild = timing.timeparse(time,1,0)
        if isinstance(timebuild,str):
            return await ctx.send(embed = discord.Embed(description = timebuild,color = discord.Color.red()))
        until = discord.utils.utcnow() + timebuild
        unix = int(until.replace(tzinfo=datetime.timezone.utc).timestamp())
        
        embed=discord.Embed(title="<a:event:923046835952697395> It's Event Time <a:event:923046835952697395>" ,color=discord.Color.random())
        build = ""
        embed.set_author(name="Hosted by " + ctx.author.display_name,icon_url=ctx.author.avatar)
        embed.set_thumbnail(url=ctx.guild.icon)
        build += f"**Event Type:** {event}\n**Event Info:** {eventinfo}\n**Requirement:** {requirement}\n**Prize:** {amount}\n**Channel:** {channel.mention}\n"
        build += f"**Donor:**{donor.mention}\n**Message:** {message}\n"
        build += f"\nThe event begins <t:{unix}:R>"
        embed.description = build
        embed.set_footer(text = "Good luck!")

        user = ctx.message.author.id
        await self.add_log(ctx,user)
        ping = await self.ping_event(ctx)
        if ping:
            message = await ctx.send(f"<@&{ping}> {event} in {channel.mention}",embed=embed)
        else:
            message = await ctx.send(embed = embed)
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        logchannel = ref.child(str(ctx.message.guild.id)).child('elogging').get()
        if logchannel:
            channel = ctx.guild.get_channel(logchannel)
            if channel:
                await self.post_log(ctx,channel,message,event,amount,donor)

    @commands.command(help = "Manually add one log to your event status.")
    @eman_role_check()
    async def elog(self,ctx):
        user = ctx.message.author.id
        output = await self.add_log(ctx,user)
        await ctx.reply(embed = discord.Embed(description = f"Logged event for <@{user}>. They now have {output} events logged!",color = discord.Color.green()))

    @commands.command(help = "Shows the amount of events you or another user has done.")
    @eman_role_check()
    async def eamount(self,ctx,user:discord.Member = None):
        user = user or ctx.message.author
        amount = await self.get_amount(ctx,user.id)
        embed=discord.Embed(description =f"Event Amount for {user}: `{amount}` Events",color=discord.Color.random())
        await ctx.reply(embed=embed)

    @commands.command(aliases = ['eventlb','elb'],help = "Show the events leaderboard.")
    @eman_role_check()
    async def eleaderboard(self,ctx):
        users,log = await self.get_leaderboard(ctx)
        formatter = EventPageSource(users, log)
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(ctx)

    @commands.command(help = "Set the log amount for a specified user")
    @commands.has_permissions(administrator= True)
    async def esetlog(self,ctx,member:discord.Member,log):
        changed = await self.set_log(ctx,str(member.id),int(log))
        await ctx.reply(embed = discord.Embed(description = f'Changed log amount for **{member}** to `{changed}`!',color = discord.Color.green()))

    @commands.command(help = "Remove log data for a specified user.")
    @commands.has_permissions(administrator= True)
    async def eremovelog(self,ctx,member):
        store = member
        try:
            member = await commands.converter.MemberConverter().convert(ctx,member)
        except:
            try:
                member = await commands.converter.UserConverter().convert(ctx,store)
            except:
                raise commands.UserInputError

        output = await self.remove_log(ctx,str(member.id))

        if not output:
            return await ctx.reply(embed = discord.Embed(descipription = "Something went wrong. Are you sure that is a valid member that has event data?",color = discord.Color.red()))
        await ctx.reply(embed = discord.Embed(description = f'Removed logs for **{member}**!',color = discord.Color.green()))

class MyMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source, *, delete_message_after=False):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.message)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value
    
    async def send_initial_message(self, ctx, message):
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await message.reply(**kwargs)
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author

    @ui.button(emoji='<:doubleleft:930948763885899797>', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction,button):
        await self.show_page(0)
        await interaction.response.defer()

    @ui.button(emoji='<:arrowleft:930948708458172427>', style=discord.ButtonStyle.blurple)
    async def before_page(self, interaction, button):
        await self.show_checked_page(self.current_page - 1)
        await interaction.response.defer()

    @ui.button(emoji='<:arrowright:930948684718432256>', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction, button):
        await self.show_checked_page(self.current_page + 1)
        await interaction.response.defer()

    @ui.button(emoji='<:doubleright:930948740557193256>', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction, button):
        await self.show_page(self._source.get_max_pages() - 1)
        await interaction.response.defer()
    
    @ui.button(label='End Interaction', style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction, button):
        await interaction.response.defer()
        self.stop()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
    
class EventPageSource(menus.ListPageSource):
    def __init__(self, data, log):
        super().__init__(data, per_page=10)
        self.log = log
    def format_leaderboard_entry(self, no, user):
        return f"**{no}. <@{user}>** `{self.log[user]} events`"
    async def format_page(self, menu, users):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_leaderboard_entry, enumerate(users, start=starting_number))
        page_content = "\n".join(iterator)
        embed = discord.Embed(
            title=f"Events Leaderboard [{page + 1}/{max_page}]", 
            description=page_content,
            color= discord.Color.random()
        )
        embed.set_footer(text=f"Use the buttons below to navigate pages!") 
        return embed

async def setup(client):
    await client.add_cog(EventTracking(client))
