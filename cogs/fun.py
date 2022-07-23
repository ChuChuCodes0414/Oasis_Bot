from re import L
import discord
from discord import ui, app_commands
from discord.ext import commands,menus
import random
import firebase_admin
from utils import timing
from firebase_admin import db
import asyncio
import datetime

class Fun(commands.Cog):
    """
        Some fun commands! There are fun badges to unlock in this category, view yours using `o!profile`.
        \n**Setup for this Category**
    """

    def __init__(self,client):
        self.client = client
        self.short = "🎈 | Fun Commands"
        self.fighters = []
        self.badges = {
                        "dev":"<:PB_BadgeDev:866505179795554315> **Bot Developer**\nThis person develops the bot that you are using!",
                        "mod":"<:PB_BadgeMod:866504829051994132> **Bot Mod**\nThis person is a mod for the bot in the support server, and has access to some cool bot commands!",
                        "fighter1":"<:PB_BadgeFighter:866505136888872990> **Fighter I**\nThis person has done a lot of fighting with the bot, gaining 50+ wins!",
                        "fighter2":"<:PB_BadgeFighter2:866846614584950806> **Fighter II**\nThis person must be really addicting to this fight command, gaining 100+ wins! Probably not the best idea to fight this person.",
                        "early":"<:PB_BadgeEarly:866847704680103956> **Early Supporter**\nThis person was one of the first few people to invite the bot to their server!",
                        "iq":"<:IQBadge:870129049232637992> **IQ**\nThis person somehow got the maximum IQ score possible. That's a 1/2000 chance!",
                        "8ball":"<:8ballBadge:870129771122671627> **8ball**\nAnd the bot says...`yes`.",
                        "nab":"<:NabBadge:870130999500095549> **Nab**\nThis person got the maximum nabrate...but it's only a 1/100 chance. Must mean this person is a nab.",
                        "color":"<:ColorBadge:912893729482883142> **Color Game**\nThis person got to level 20 in the color game...pretty good memory",
                        "1y":"<:1yBadge:979206493377294396> **One Year**\nThis person used the bot during the 2.0.2 Anniversary Update!"
                    }
        self.roasts = ["Light travels faster than sound, that's why you seemed bright until you spoke",
                        "I would explain whats going wrong with you, but I forgot my english-to-dumbass dictionary at home",
                        "It’s impossible to underestimate you.",
                        "I thought of you today. It reminded me to take out the trash.",
                        "If ignorance is bliss, you must be the happiest person on the planet.",
                        "May both sides of your pillow be uncomfortably warm.",
                        "Remember when I asked for your opinion? Me neither.",
                        "Some day you'll go far...and I hope you stay there.",
                        "I'd agree with you, but then we would both be wrong.",
                        "You look like a before picture.",
                        "Calling you a donkey is an insult to the donkey",
                        "The trash will be picked tomorrow. Get ready to sit in."]
        self.responses = ["It is certain.",
                    "It is decidedly so.",
                    "Without a doubt.",
                    "Yes - definitely.",
                    "You may rely on it.",
                    "As I see it, yes.",
                    "Most likely.",
                    "Outlook good.",
                    "Yes.",
                    "Signs point to yes.",
                    "Reply hazy, try again.",
                    "Ask again later.",
                    "Better not tell you now.",
                    "Cannot predict now.",
                    "Concentrate and ask again.",
                    "Don't count on it.",
                    "My reply is no.",
                    "My sources say no.",
                    "Outlook not so good.",
                    "Very doubtful."]
        self.wordlist = ["claim","grab","serenity","steal","mine","give","clutch","snatch","take","swipe"]
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Fun Cog Loaded.')

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
            return True
            
        return commands.check(predicate)
        
    async def grant_badge(self,ctx,member,badge):
        if not badge in self.badges:
            return False
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        badgelist = ref.child(str(member)).child("badges").get()
        if not badgelist:
            ref.child(str(member)).child("badges").set([badge])
            return True
        elif not badge in badgelist:
            badgelist.append(badge)
            ref.child(str(member)).child("badges").set(badgelist)
            return True
        else:
            return False

    async def remove_badge(self,ctx,member,badge):
        if not badge in self.badges:
            return False
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        badgelist = ref.child(str(member)).child("badges").get()
        if not badgelist:
            return False
        elif badge in badgelist:
            badgelist.remove(badge)
            ref.child(str(member)).child("badges").set(badgelist)
            return True
        else:
            return False

    @commands.command(name = "8ball",aliases=['predictor'],help = 'What does the bot have to say about your question?')
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def _8ball(self,ctx,*,question):
        choice = random.choice(self.responses)
        embed = discord.Embed(title = question,description = f"**The totally magic 8ball says...**\n{choice}",color = discord.Color.random())
        await ctx.reply(embed = embed)
        if choice == "Yes.":
            await self.grant_badge(ctx,ctx.author.id,"8ball")

    @commands.command(aliases=['penis'],help = 'How big is your pp? Is bigger always better?')
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def pp(self,ctx,*,person = None):
        try:
            member = await commands.converter.MemberConverter().convert(ctx,person)
            person = str(member)
        except:
            person = person
        person = person or ctx.author

        size = random.randint(0,11) * "="

        pp = f'8{size}D'

        embed=discord.Embed(description=f"**{person}'s pp**\n{pp}",color = discord.Color.random())

        await ctx.reply(embed = embed)
        
    @commands.command(aliases=['smartrate'],help = "What's your iq level?")
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def iq(self,ctx,person = None):
        try:
            member = await commands.converter.MemberConverter().convert(ctx,person)
            person = str(member)
        except:
            person = person
        person = person or ctx.author

        iq = random.randint(-1000,1000)

        embed=discord.Embed(description=f"**{person}'s IQ**\n{iq}",color = discord.Color.random())

        await ctx.reply(embed = embed)

        if iq == 1000:
            await self.grant_badge(ctx,ctx.author.id,"iq")

    @commands.command(aliases=['hownabisthenab','nab'],help = "What's your nab rate?")
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def nabrate(self,ctx,person = None):
        try:
            member = await commands.converter.MemberConverter().convert(ctx,person)
            person = str(member)
        except:
            person = person
        person = person or ctx.author

        nab = random.randint(0,100)

        embed=discord.Embed(description=f"**{person}'s Nab Rate**\n{nab}% Nab",color = discord.Color.random())

        await ctx.reply(embed = embed)

        if nab == 100:
            await self.grant_badge(ctx,ctx.author.id,"nab")

    @commands.command(help = "Roast a fellow member.",brief= "Don't take these too seriously, they are meant to be fun.")
    @commands.cooldown(1,10,commands.BucketType.user)
    async def roast(self,ctx,person:discord.Member):
        roasts = random.randint(0,len(self.roasts)-1)
        if person == ctx.author:
            return await ctx.reply(embed = discord.Embed(description = "Imagine, trying to roast yourself. Do better.",color = discord.Color.red()))
        elif person.bot:
            return await ctx.reply(embed = discord.Embed(description = "Looks like you ran out of people to roast, are you trying to roast a bot? Must be sad to be that lonely.",color = discord.Color.red()))
        await ctx.reply(f"{person.mention} {self.roasts[roasts]}")

    @commands.command(help = 'Drop a prize for others to pick up!',brief = 'Command has changed to what it once was, but now with quotes for easier usage.'
     + '\n\nExample:\n\n`o!drop "discord nitro" #general "nitro is mine!"`\n`o!drop nitro`\n`o!drop "nitro boost"`')
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def drop(self,ctx,item,channel : discord.TextChannel = None,word = None):
        channel = channel or ctx.channel
        word = word or random.choice(self.wordlist)

        embed=discord.Embed(title=f"Someone has dropped {item} in this channel!",description=f"Type the words `{word}` to claim!", color=discord.Color.random())
        message = await channel.send(embed=embed)

        if not channel == ctx.channel:
            await ctx.reply(embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully dropped!\n[Jump to the message]({message.jump_url})",color = discord.Color.green()))

        def check(message: discord.Message):
            if message.author.bot:
                return False
            return message.content.lower() == word and message.channel == channel

        try:
            msg = await self.client.wait_for("message",timeout = 270.0,check=check)
        except asyncio.TimeoutError:
            try:
                await message.edit("Drop no longer Active",embed = embed
                )
            except:
                pass
            await message.channel.send(embed = discord.Embed(description = "You took too long, and the drop is now cancelled!",color = discord.Color.red()))
            await ctx.reply(embed = discord.Embed(description = f"Your drop was cancelled, since no one responded.",color = discord.Color.red()))
            return
        await message.reply(embed = discord.Embed(description = f"Claimed by {msg.author.mention} :tada:",color = discord.Color.random()))
        await ctx.reply(embed = discord.Embed(description = f"{ctx.author.mention} your prize was claimed! Please give {item} to {msg.author.mention}",color = discord.Color.green()))

    @commands.command(aliases = ['sos'],help = "Host a giveaway with a split or steal function!")
    @eman_role_check()
    async def splitorsteal(self,ctx,time,requirements,*,prize):
        time = timing.timeparse(time,0,300)
        if isinstance(time,str):
            await ctx.reply(embed = discord.Embed(description = time,color = discord.Color.red()))
        if requirements and requirements.lower() != "none":
            requirements = requirements.split(";;")
            req,by,bl = [],[],[]
            for require in requirements:
                require = require.split(":")
                try:
                    role = await commands.converter.RoleConverter().convert(ctx,require[1])
                except:
                    role = None
                if len(require) != 2 or not role:
                    return await ctx.reply(embed = discord.Embed(description = "I could not process your requirements!",color = discord.Color.red()))
                elif require[0].startswith("role"):
                    req.append(role)
                elif require[0].startswith("bypass"):
                    by.append(role)
                elif require[0].startswith("blacklist"):
                    bl.append(role)
        else:
            req,by,bl = None,None,None
        view = GiveawayEnter(req,by,bl)
        now = datetime.datetime.now(datetime.timezone.utc)
        end = now + time
        unix = int(end.replace(tzinfo=datetime.timezone.utc).timestamp())
        time = time.total_seconds()
        embed = discord.Embed(title = f"Split or Steal For: {prize}",description = f"Ending at: <t:{unix}:f>\nTime Remaining: <t:{unix}:R>\nHosted By: {ctx.author.mention}",color = discord.Color.green())
        reqbuild = ""
        if req:
            reqbuild += "Required Roles:" + ', '.join(role.mention for role in req)
        if by:
            reqbuild += "\nBypass Roles:" + ', '.join(role.mention for role in by)
        if bl:
            reqbuild += "\nBlacklisted Roles:" + ', '.join(role.mention for role in bl)
        if reqbuild == "":
            reqbuild = "None!"
        embed.add_field(name = "Requirements",value = reqbuild,inline = False)
        message = await ctx.send(embed = embed,view = view)
        await ctx.message.delete()
        await asyncio.sleep(time)
        view.stop()
        entrees = view.entered
        if len(entrees) < 2:
            embed.description = f"Ended at: <t:{unix}:f>"
            embed.color = None
            embed.insert_field_at(0,name = "Winners",value = f"No winners determined\nHosted By: {ctx.author.mention}")
            view.children[0].disabled = True
            await message.edit(embed = embed,view = view)
            return await message.reply(embed = discord.Embed(description = "There were not enough valid entrees!",color = discord.Color.red()))
        winners = random.sample(entrees,2)
        embed.description = f"Ended at: <t:{unix}:f>"
        embed.color = None
        embed.insert_field_at(0,name = "Winners",value = f"{winners[0].mention} and {winners[1].mention}!\nHosted By: {ctx.author.mention}")
        view.children[0].disabled = True
        await message.edit(embed = embed,view = view)
        embed = discord.Embed(title = "Now is the time to discuss!",description = "You now have 30 seconds to discuss with the other winner! Do it quickly...",color = discord.Color.random())
        embed.set_footer(text = "The channel will unlock for the winners shortly.")
        await ctx.send(winners[0].mention + winners[1].mention,embed = embed)
        overwrite = ctx.channel.overwrites_for(winners[0])
        overwrite.send_messages = True
        await ctx.channel.set_permissions(winners[0], overwrite=overwrite)
        overwrite = ctx.channel.overwrites_for(winners[1])
        overwrite.send_messages = True
        await ctx.channel.set_permissions(winners[1], overwrite=overwrite)
        await asyncio.sleep(25)
        await ctx.send(embed = discord.Embed(description = "5 seconds remaining!",color = discord.Color.random()))
        await asyncio.sleep(5)
        await ctx.channel.set_permissions(winners[0], overwrite=None)
        await ctx.channel.set_permissions(winners[1], overwrite=None)
        embed = discord.Embed(title = "Now it is time to decide!",description = "Press the button below to choose.",color = discord.Color.random())
        embed.set_footer(text = "You have 30 seconds to choose!")
        view = SplitorSteal(winners)
        message = await ctx.send(embed = embed,view = view)
        response = await view.wait()
        for child in view.children:
            child.disabled = True
        await message.edit(view = view)
        if response:
            return await message.reply(embed = discord.Embed(description = "The buttons timed out! One or both of the winners did not choose.",color = discord.Color.red()))
        async with ctx.typing():
            await asyncio.sleep(3)
        if view.u1 == "split" and view.u2 == "split":
            return await message.reply(embed = discord.Embed(description = f"Both **{winners[0].mention}** and **{winners[1].mention}** decide to split. Congrats!",color = discord.Color.green()))
        if view.u1 == "steal" and view.u2 == "steal":
            return await message.reply(embed = discord.Embed(description = f"Both **{winners[0].mention}** and **{winners[1].mention}** decide to steal. Bummer!",color = discord.Color.red()))
        if view.u1 == "steal" and view.u2 == "split":
            return await message.reply(embed = discord.Embed(description = f"**{winners[0].mention}** decided to steal while **{winners[1].mention}** decide to split. GG!",color = discord.Color.gold()))
        return await message.reply(embed = discord.Embed(description = f"**{winners[1].mention}** decided to steal while **{winners[0].mention}** decide to split. GG!",color = discord.Color.gold()))

    @commands.command(aliases = ['gtn'],help = "Host a guess the number game in the channel.")
    async def guessthenumber(self,ctx,start:int = None,end:int = None,target:int = None,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        if not start: start = 1
        if not end: end = start + 99
        if not target: target = random.randint(start,end)
        if start < 0 or end < 0 or start >= end or target < start or target > end or target < 0: return await ctx.reply("Yea that doesn't look like valid input.")

        embed = discord.Embed(title = "Guess the Number!",description = f"The range for this game is **{start}** - **{end}**",color = discord.Color.random())
        embed.set_author(name="Hosted by " + ctx.author.display_name,icon_url=ctx.author.avatar)
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.set_footer(text = f"Good luck! You have 2 minutes to guess.")
        message = await channel.send(embed = embed)
        def check(i):
            if i.channel.id == message.channel.id and i.content == str(target):
                return True
            else:
                return False
        try:
            message = await self.client.wait_for("message",timeout = 120.0,check = check)
        except asyncio.TimeoutError:
            return await message.edit("The game timed out. Yall are bad")

        embed = discord.Embed(description = f"{message.author.mention} guessed the number! The number was **{target}**.")
        await message.reply(embed = embed)

    @commands.command(help = "How good is your memory?")
    async def colorgame(self,ctx):
        order = []
        embed = discord.Embed(title = f"Setting Up {ctx.author}'s Colorgame...",description = f"The bot will show you a sequence of colors by enabling and disabling buttons. After showing the sequence, it is your turn to press the buttons in the same sequence!",color = discord.Color.random())
        message = await ctx.reply(embed = embed)
        view = ColorGame(ctx)
        embed = discord.Embed(title = f"{ctx.author}'s Color Game",description = f"Level 1\nWatch the color sequence now!")
        await message.edit(embed = embed,view = view)
        while True:
            next = random.randint(0,3)
            order.append(next)
            for selected in order:
                view.children[selected].disabled = False
                await message.edit(embed = embed,view = view)
                await asyncio.sleep(1)
                view.children[selected].disabled = True
                await message.edit(embed = embed,view = view)
                await asyncio.sleep(1)
            for child in view.children:
                child.disabled = False
            embed = discord.Embed(title = f"{ctx.author}'s Color Game",description = f"Level {len(order)}\nEnter in the sequence now!")
            await message.edit(embed = embed,view = view)
            view.responding = True
            view.order = order
            await view.wait()
            if view.value == True:
                embed = discord.Embed(title = f"{ctx.author}'s Color Game",description = f"Level {len(order)+1}\nWatch the color sequence now!")
                view = ColorGame(ctx)
                await message.edit(embed = embed,view = view)
                continue
            else:
                embed = discord.Embed(title = f"{ctx.author}'s Color Game",description = f"Level {len(order)}\nYou Lost!",color = discord.Color.red())
                view = ColorGame(ctx)
                view.children[4].disabled = True
                await message.edit(embed = embed,view = view)
                if len(order) >= 20:
                    await self.grant_badge(ctx,ctx.author.id,"color")
                break
            
    @commands.command(help = "View your profile, with badges and fight stats.")
    async def profile(self,ctx,member :discord.Member = None):
        if not member:
            member = ctx.author
        ref = db.reference("/",app = firebase_admin._apps['profile'])

        embed=discord.Embed(title = f"Profile for {member}",color=discord.Color.random())

        badges = ref.child(str(member.id)).child("badges").get()

        if not badges:
            embed.add_field(name = "Badges",value = "This user has no badges. Sad.")
        else:
            build = ""
            for badge in badges:
                build += self.badges[badge] + "\n"
            embed.add_field(name = "Badges",value = build)

        fightstats = ref.child(str(member.id)).child("fight").get()

        if fightstats:
            build = ""
            wins = fightstats.get("win",0)
            loses = fightstats.get("lose",0)
            total = wins + loses
            embed.add_field(name = "Fighting Statistics",value = f"Wins: `{wins}`\nLosses: `{loses}`\nTotal Fights: `{total}`",inline = False)
        await ctx.reply(embed = embed) 
    
    '''
    @app_commands.command(name="commandrequest",description = "Request a custom command!")
    async def requestcommand(self, interaction: discord.Interaction) -> None:
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        if ref.child(str(interaction.user.id)).child("commandrequest").get():
            return await interaction.response.send_message(embed = discord.Embed(description = "You have already requested a custom command!",color = discord.Color.red()),ephemeral = True)
        embed = discord.Embed(title = "Request a custom command!",description = "As a part of the first anniversary of Oasis Bot, you can now request a custom command! Please read *carefully* for instructions.",color = discord.Color.random())
        embed.add_field(name = "What can I request?",value = "You can basically request any simple command, which can respond however you choose. The functionality, however, should be limited and simple. This could include a simple phrase response, image, button press, etc.",inline = False)
        embed.add_field(name = "Where will my custom command be?",value = "Your custom command will be in a hidden category, and must be in the form of a command (beginning with the bot prefix). Your command cannot be a slash command.",inline = False)
        embed.add_field(name = "What is the request process?",value = "When you are ready, click the button below to get started. You can then fill out a command name, and then what your command should do! You can also include some reasons for your custom command. The developer will then review your request, and then make a decision. Note that you can only make one request, so make it count!",inline = False)
        embed.add_field(name = "How long will the command stay?",value = "As long as your command does not cause issues, it will stay for as long as the bot is up!",inline = False)
        embed.add_field(name = "Disclaimed",value = "The Oasis and Serenity Bot team reserve the right to deny or alter your request, and may choose to remove your command whenver deemed fit. By filling out this form, you agree to turn over this command idea to the development team and allow its use on any bot run by the team. Any troll submissions will result in your blacklist from the bot, which can be permanent.",inline = False)
        embed.set_footer(text = "Click the button below to get started!")
        view = CommandRequestConfirm()
        await interaction.response.send_message(embed = embed, view = view, ephemeral = True)
        await view.wait()
    '''

class CommandRequestConfirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 60)
 
    @ui.button(label = "Start Request Form",style = discord.ButtonStyle.green)
    async def enter(self,interaction,button):
        await interaction.response.send_modal(CustomCommand())
        self.stop()

class GiveawayEnter(discord.ui.View):
    def __init__(self,req,by,bl):
        super().__init__()
        self.req = req
        self.by = by
        self.bl = bl
        self.entered = []
    
    async def interaction_check(self, interaction):
        if interaction.user in self.entered:
            await interaction.response.send_message(embed = discord.Embed(description = f"You are already entered into this giveaway!",color = discord.Color.red()),ephemeral = True)
            return False
        if self.bl:
            for role in self.bl:
                if role in interaction.user.roles:
                    await interaction.response.send_message(embed = discord.Embed(description = f"You are blacklisted due to the {role.mention} role!",color = discord.Color.red()),ephemeral = True)
                    return False
        if self.by:
            for role in self.by:
                if role in interaction.user.roles:
                    return True
        if self.req:
            for role in self.req:
                if role not in interaction.user.roles:
                    await interaction.response.send_message(embed = discord.Embed(description = f"You are missing the {role.mention} role!",color = discord.Color.red()),ephemeral = True)
                    return False
        return True
    
    @ui.button(label = "Enter!",style = discord.ButtonStyle.green)
    async def enter(self,interaction,button):
        self.entered.append(interaction.user)
        await interaction.response.send_message(embed = discord.Embed(description = f"You have succesfully entered!",color = discord.Color.green()),ephemeral = True)

class SplitorSteal(discord.ui.View):
    def __init__(self,users):
        super().__init__(timeout = 30)
        self.u1 = None
        self.u2 = None
        self.users = users
    
    async def interaction_check(self, interaction):
        return interaction.user in self.users
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True 
    
    @ui.button(label = "Split",style = discord.ButtonStyle.blurple)
    async def split(self,interaction,button):
        if interaction.user == self.users[0] and not self.u1:
            await interaction.response.send_message(embed = discord.Embed(description = f"**{interaction.user}** has selected their answer!",color = discord.Color.random()))
            self.u1 = "split"
            if self.u2 and self.u1:
                self.stop()
        elif interaction.user == self.users[0]:
            return await interaction.response.send(embed = discord.Embed(description = f"You have already selected your answer!",color = discord.Color.red()))
        elif interaction.user == self.users[1] and not self.u2:
            await interaction.response.send_message(embed = discord.Embed(description = f"**{interaction.user}** has selected their answer!",color = discord.Color.random()))
            self.u2 = "split"
            if self.u2 and self.u1:
                self.stop()
        else:
            await interaction.response.send_message(embed = discord.Embed(description = f"You have already selected your answer!",color = discord.Color.red()),ephemeral = True)

    @ui.button(label = "Steal",style = discord.ButtonStyle.blurple)
    async def steal(self,interaction,button):
        if interaction.user == self.users[0] and not self.u1:
            await interaction.response.send_message(embed = discord.Embed(description = f"**{interaction.user}** has selected their answer!",color = discord.Color.random()))
            self.u1 = "steal"
            if self.u2 and self.u1:
                self.stop()
        elif interaction.user == self.users[0]:
            return await interaction.response.send(embed = discord.Embed(description = f"You have already selected your answer!",color = discord.Color.red()))
        elif interaction.user == self.users[1] and not self.u2:
            await interaction.response.send_message(embed = discord.Embed(description = f"**{interaction.user}** has selected their answer!",color = discord.Color.random()))
            self.u2 = "steal"
            if self.u2 and self.u1:
                self.stop()
        else:
            await interaction.response.send_message(embed = discord.Embed(description = f"You have already selected your answer!",color = discord.Color.red()),ephemeral = True)

class ColorGame(discord.ui.View):
    def __init__(self,ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.responding = False
        self.value = None
        self.order = []
        self.count = 0

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author and self.responding

    async def check_response(self,number):
        if number == self.order[self.count]:
            if self.count == len(self.order)-1:
                return 2
            self.count += 1
            return 0
        else:
            if self.order[self.count] == 0: return "Blue"
            if self.order[self.count] == 1: return "Gray"
            if self.order[self.count] == 2: return "Green"
            if self.order[self.count] == 3: return "Red"
    
    @ui.button(emoji='<:BlueButton:904111618391158875>', style=discord.ButtonStyle.blurple,row = 0,disabled = True)
    async def blue(self, interaction, button):
        check = await self.check_response(0)
        if check == 0: 
            await interaction.response.defer()
        elif check == 2:
            await interaction.response.defer()
            self.value = True
            self.stop()
        else:
            await interaction.response.defer()
            self.value = False
            self.stop()
            await interaction.response.send_message(embed = discord.Embed(description = f"You lost! The color was **{check}**"))

    @ui.button(emoji='<:GrayButton:904112302918369301>', style=discord.ButtonStyle.gray,row = 0,disabled = True)
    async def gray(self, interaction, button):
        check = await self.check_response(1)
        if check == 0: 
            await interaction.response.defer()
        elif check == 2:
            await interaction.response.defer()
            self.value = True
            self.stop()
        else:
            await interaction.response.defer()
            self.value = False
            self.stop()
            await interaction.response.send_message(embed = discord.Embed(description = f"You lost! The color was **{check}**"))

    @ui.button(emoji='<:GreenButton:904112314393968740>', style=discord.ButtonStyle.green,row = 1,disabled = True)
    async def green(self, interaction, button):
        check = await self.check_response(2)
        if check == 0: 
            await interaction.response.defer()
        elif check == 2:
            await interaction.response.defer()
            self.value = True
            self.stop()
        else:
            await interaction.response.defer()
            self.value = False
            self.stop()
            await interaction.response.send_message(embed = discord.Embed(description = f"You lost! The color was **{check}**"))

    @ui.button(emoji='<:RedButton:904112322484789338>', style=discord.ButtonStyle.red,row = 1,disabled = True)
    async def red(self, interaction, button):
        check = await self.check_response(3)
        if check == 0: 
            await interaction.response.defer()
        elif check == 2:
            await interaction.response.defer()
            self.value = True
            self.stop()
        else:
            await interaction.response.defer()
            self.value = False
            self.stop()
            await interaction.response.send_message(embed = discord.Embed(description = f"You lost! The color was **{check}**"))
    
    @ui.button(label='End Interaction', style=discord.ButtonStyle.blurple,row = 2,disabled = True)
    async def stop_page(self, interaction, button):
        await interaction.response.defer()
        self.value = False
        self.stop()

class CustomCommand(discord.ui.Modal,title = "Custom Command Request!"):
    name = discord.ui.TextInput(label = "Command Name",placeholder="Short, one word name for your command...",max_length = 15)
    description = discord.ui.TextInput(label = "Command Description",style = discord.TextStyle.long,placeholder = "Describe what your command should do here!",max_length = 400)
    reason = discord.ui.TextInput(label = "Why should I add your command?",style = discord.TextStyle.long,placeholder = "Give a few reasons why your command is interesting...",max_length = 400,required = False)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.client.get_channel(978481339437305897)
        embed = discord.Embed(title = "Command Request Sent!",description = f"{interaction.user.mention} | {interaction.user} (`{interaction.user.id}`)")
        embed.add_field(name = "Command Name",value = self.name.value)
        embed.add_field(name = "Command Description",value = self.description.value,inline = False)
        embed.add_field(name = "Command Reasoning",value = self.reason.value,inline = False)
        await channel.send(embed = embed)
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        ref.child(str(interaction.user.id)).child("commandrequest").set(True)
        await interaction.response.send_message(embed = discord.Embed(description = f'Thank you for your request! It has been sent to the developer.',color = discord.Color.random()), ephemeral=True)

async def setup(client):
    await client.add_cog(Fun(client))
