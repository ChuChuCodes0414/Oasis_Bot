import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import db
import datetime
class EventLogging(commands.Cog):
    """
        This category allows you to track event manager activity. Most commands will require you to set up a role for event managers. You can also setup a channel to log when event is completed.
        \n**Setup for this Category**
        Event Manager Role: `o!settings set eventmanager <role>`
        Event Logging Channel: `o!settings set eventlog <channel>`
    """

    def __init__(self,client):
        self.client = client

        self.eventslist= {
        'greentea': 'Multiplayer game, be the fastest to write a word containing the group of 3 letters indicated.',
        'redtea':'Multiplayer game, find the longest word containing the group of 3 letters indicated.',
        'blacktea':'Multiplayer game, write a word containing the group of 3 letters indicated.',
        'yellowtea':'Multiplayer game, find the largest amount of words containing the group of 3 letters indicated.',
        'mixtea':'Multiplayer game, a mix of all the tea games.',
        'rumble':'React and let the bot stimulate a hunger games scenario, last one standing wins!',
        'mafia': 'Work with your side to ensure that your team wins! Each member receieves a special role, some of which have functions. Use `m.help` for more information.',
        'skribble': 'Test your drawing skills, and try to identify what others are drawing!',
        'uno':'Everyone is dealt cards at the beginning of the match. You can play a card of the same type or color, the person with no cards first wins! Use `uno help` for more information.',
        'fight':'Fight another chosen opponent, or the sponsor, for the prize of the event! Fight details will be specified in the event channel'
        }

    def eman_role_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            emanrole = ref.child(str(ctx.message.guild.id)).child('event').get()
            emanrole_ob = ctx.message.guild.get_role(emanrole)
            if emanrole_ob in ctx.message.author.roles:
                return True
            else:
                return False
        return commands.check(predicate)

    def eman_channel_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
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
        print('Logging Cog Loaded.')

    async def add_log(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child(str(ctx.message.guild.id)).get()

        if log == None:
            ref.child(str(ctx.message.guild.id)).set({
                str(user):1
            })
            return 1
        if not str(user) in log.keys():
            log[str(user)] = 1
        else:
            log[str(user)] = log[str(user)] + 1
        ref.child(str(ctx.message.guild.id)).set(log)
        return log[str(user)]

    async def set_log(self,ctx,user,amount):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child(str(ctx.message.guild.id)).get()

        if log == None:
            ref.child(str(ctx.message.guild.id)).set({
                str(user):amount
            })
            return 1
        if not str(user) in log.keys():
            log[str(user)] = amount
        else:
            log[str(user)] = amount
        ref.child(str(ctx.message.guild.id)).set(log)
        return log[str(user)]

    async def remove_log(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child(str(ctx.message.guild.id)).get()

        if log == None:
            return False
        if not str(user) in log.keys():
            return False
        else:
            log.pop(str(user))
        ref.child(str(ctx.message.guild.id)).set(log)
        return True

    async def reset_log(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.get()
        ref.set({

        })

    async def get_leaderboard(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child(str(ctx.message.guild.id)).get()

        if log:
            return sorted(log, key=log.get, reverse=True) , log
        else:
            return {},{}

    async def get_amount(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child(str(ctx.message.guild.id)).get()
        if log == None:
            return 0
        if str(user) in log.keys():
            return log[str(user)]
        else:
            return 0

    async def ping_event(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        ping = ref.child(str(ctx.message.guild.id)).child('eping').get()
        if ping:
            await ctx.send(f'<@&{ping}>')

    async def post_log(self,ctx,channel,message,type,prize,donor):
        emb = discord.Embed(title=f"Event Recorded for {ctx.message.author.name}",description = f"{ctx.message.author.mention}",
                                color=discord.Color.green())

        emb.add_field(name = "Event information:",value = f"[Link to Event]({message.jump_url})\nEvent Type: {type}\nEvent Prize: {prize}\nEvent Donor: {donor}")

        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'Oasis Bot Event Logging',icon_url = ctx.message.channel.guild.icon_url)

        await channel.send(embed = emb)

    @commands.command(description = "Manually add one log to your event status.",help = "elog")
    @eman_role_check()
    async def elog(self,ctx):
        user = ctx.message.author.id
        output = await self.add_log(ctx,user)
        await ctx.reply(f"Logged event for <@{user}>. They now have {output} events logged!")

    @commands.command(aliases = ['eventlb','elb'],description = "Show the events leaderboard.",help = "eleaderboard")
    @eman_role_check()
    async def eleaderboard(self,ctx):
        users,log = await self.get_leaderboard(ctx)

        embed=discord.Embed(title="Events Leaderboard", color=discord.Color.green())
        
        count = 1
        for user in users:
            amount = log[user]
            embed.add_field(name=f"{count}",value=f'<@{user}> {amount} events',inline=False)
            count += 1

            if count >= 11:
                break

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)

    @commands.command(description = "Shows the amount of events you or another user has done.",help = "eamount <user>")
    @eman_role_check()
    async def eamount(self,ctx,user:discord.Member = None):
        user = user or ctx.message.author
        amount = await self.get_amount(ctx,user.id)
        embed=discord.Embed(description =f"Event Amount for {user}: `{amount}` Events",color=discord.Color.random())
        await ctx.reply(embed=embed)

    @commands.command(description = "Start an event with a ping and an embed. Will also increment your log tracking by one.",help = "estart <time> <eventype>/<requirement>/<eventprize>/<channel>/<donor>/<message>")
    @eman_role_check()
    @eman_channel_check()
    async def estart(self,ctx,time,*,values = "event/reqruirement/amount/channel/donor/message"):
        eventslist= {
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
        await ctx.message.delete()

        try:
            event,requirement,amount,location,donor,message = values.split("/")
        except:
            return await ctx.send("I could not parse your input! Please try again.")

        if time.lower() == "now":
            timebuild = time
        else:
            timeunit = time[-1]
            timebuild = ""
            if timeunit.isalpha():
                if timeunit.lower() == "s":
                    timebuild = time[:-1] + " seconds"
                elif timeunit.lower() == "m":
                    timebuild = time[:-1] + " minutes"
                elif timeunit.lower() == "h":
                    timebuild = time[:-1] + " hours"
                elif timeunit.lower() == "d":
                    timebuild = time[:-1] + " days"
                else:
                    timebuild = time
            else:
                timebuild = time + " seconds"

        channel = await commands.converter.TextChannelConverter().convert(ctx,location.strip())
        donor = await commands.converter.MemberConverter().convert(ctx,donor.strip())

        if event in eventslist.keys():
            eventinfo = eventslist[event]
        else:
            eventinfo = event

        #### Create the initial embed object ####
        embed=discord.Embed(title="<a:event:923046835952697395> It's Event Time <a:event:923046835952697395>" ,color=discord.Color.random())
        build = ""
        embed.set_author(name="Hosted by " + ctx.author.display_name,icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        build += f"**Event Type:** {event}\n**Event Info:** {eventinfo}\n**Requirement:** {requirement}\n**Prize:** {amount}\n**Channel:** {channel.mention}\n"
        build += f"**Donor:**{donor.mention}\n**Message:** {message}"
        embed.set_footer(text=f"The event begins in {timebuild}")
        embed.description = build

        user = ctx.message.author.id
        output = await self.add_log(ctx,user)
        await self.ping_event(ctx)
        message = await ctx.send(embed=embed)

        ref = db.reference("/",app = firebase_admin._apps['settings'])
        logchannel = ref.child(str(ctx.message.guild.id)).child('elogging').get()
        if logchannel:
            channel = ctx.guild.get_channel(logchannel)
            if channel:
                await self.post_log(ctx,channel,message,event,amount,donor)

    @commands.command(description = "Set the log amount for a specified user",help = "setlog <member> <amount>")
    @commands.has_permissions(administrator= True)
    async def setlog(self,ctx,member,log):
        if str(member).isnumeric():
            guild = ctx.guild
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)
        member = member.id
        changed = await self.set_log(ctx,str(member),int(log))
        await ctx.reply(f'Changed log amount for <@{member}> to {changed}!')

    @commands.command(description = "Remove log data for a specified user.",help = "removelog <member>")
    @commands.has_permissions(administrator= True)
    async def removelog(self,ctx,member):
        store = member
        if str(member).isnumeric():
            guild = ctx.guild
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)

        if not member:
            if not store.isnumeric():
                return await ctx.reply("That does not even look like a valid member.")
            else:
                member = store
        else:
            member = member.id

        output = await self.remove_log(ctx,str(member))

        if not output:
            return await ctx.reply("Something went wrong. Are you sure that is a valid member that has event data?")
        await ctx.reply(f'Removed logs for <@{member}>!')
        


def setup(client):
    client.add_cog(EventLogging(client))
