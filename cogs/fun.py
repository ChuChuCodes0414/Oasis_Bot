import discord
from discord.ext import commands
import random
import firebase_admin
from firebase_admin import db
import asyncio
import json
from discord_components import DiscordComponents, Button,SelectOption,Select,Interaction
import datetime

class Fun(commands.Cog):
    """
        Some fun commands! There are fun badges to unlock in this category, view yours using `o!profile`.
        \n**Setup for this Category**
        Giveaway Manager: `o!settings set giveawaymanager <role>` 
    """

    def __init__(self,client):
        self.client = client
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
                        "color":"<:ColorBadge:912893729482883142> **Color Game**\nThis person got to level 20 in the color game...pretty good memory"
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


    @commands.Cog.listener()
    async def on_ready(self):
        print('Fun Cog Loaded.')

    def giveaway_role_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            giveaway = ref.child(str(ctx.message.guild.id)).child('giveaway').get()
            role_ob = ctx.message.guild.get_role(giveaway)
            if role_ob in ctx.message.author.roles:
                return True
            else:
                return False
        return commands.check(predicate)

    @commands.command(aliases=['8ball','predictor'],description = 'What does the bot have to say about your question?',help = "8ball <question>")
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def _8ball(self,ctx,*,question):
        responses = ["It is certain.",
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
        choice = random.choice(responses)
        if ('<@' in question or "@&" in question or "@everyone" in question or "@here" in question):
            await ctx.reply(f'You cannot ping people with this command.')
        else:
            await ctx.reply(f'Question: {question}\nAnswer: {choice}')

        if choice == "Yes.":
            await self.grant_badge(ctx,ctx.author.id,"8ball")

    async def get_items(self,ctx,member):
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        current = ref.child(str(member)).child("badges").get()

        if current:
            return "fighter1" in current,"fighter2" in current
        else:
            return False,False

    async def add_fight_stat(self,ctx,member,outcome):
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        current = ref.child(str(member)).child("fight").get()

        if not current:
            ref.child(str(member)).child("fight").child(outcome).set(1)
            return 1
        elif not outcome in current:
            current[outcome] = 1
            ref.child(str(member)).child("fight").set(current)
            return 1
        else:
            current[outcome] += 1
            ref.child(str(member)).child("fight").set(current)
            return current[outcome]
        
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

    async def get_fight_lb(self,ctx,category):
        if category not in ["total","win","lose"]:
            return await ctx.reply("You only got 3 choices: total, win, or lose. Gotta pick one.")
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        profiles = ref.get()

        def check(a,category):
            if category == "total":
                return profiles[a]["fight"].get("win",0) + profiles[a]["fight"].get("lose",0)

            return profiles[a]["fight"].get(category,0)
            

        sortedprofiles = sorted(profiles,key = lambda a: check(a,category),reverse = True)
        if not sortedprofiles:
            return await ctx.reply("Hmm, for some reason it seems the leaderboards are empty.")
        build = ""
        #await ctx.send(str(sortedprofiles))
        count = 1
        for person in sortedprofiles[:10]:
            try:
                if category == "total":
                    string = profiles[person]["fight"].get("win",0) + profiles[person]["fight"].get("lose",0)
                    formatted = '{:,}'.format(string)
                else:
                    formatted = '{:,}'.format(profiles[person]["fight"][category])
                build += f'{count}. <@{person}>: `{formatted}` fights\n'
                count += 1
            except:
                pass

        emb = discord.Embed(title=f"Global {category.capitalize()} Fight Leaderboard",
                            description=f"{build}",
                            color=discord.Color.blue())

        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)

        await ctx.reply(embed = emb)



    @commands.command(aliases=['penis'],description = 'How big is your pp? Is bigger always better?',help = "pp <person>",brief = "(Please note that this is rigged for some users. Do not use this to fight)")
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def pp(self,ctx,*,person = None):
        if not person:
            person = ctx.author
        person = str(person)
        if person.isnumeric():
            member = ctx.guild.get_member(int(person))
            if not member:
                pass
            else:
                person = member
        person = str(person)

        size = random.randint(0,11) * "="

        pp = f'8{size}D'

        embed=discord.Embed(description=f"**{person}'s pp**\n{pp}")

        await ctx.reply(embed = embed)
        
    @commands.command(aliases=['smartrate'],description = "What's your iq level?",help = "iq <user>")
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def iq(self,ctx,person = None):
        if not person:
            person = ctx.author
        person = str(person)
        if person.isnumeric():
            member = ctx.guild.get_member(int(person))
            if not member:
                pass
            else:
                person = member
        person = str(person)

        iq = random.randint(-1000,1000)

        embed=discord.Embed(description=f"**{person}'s IQ**\n{iq}")

        await ctx.reply(embed = embed)

        if iq == 1000:
            await self.grant_badge(ctx,ctx.author.id,"iq")

    @commands.command(aliases=['hownabisthenab','nab'],description = "What's your nab rate?",help = "nabrate <user>")
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def nabrate(self,ctx,person = None):
        if not person:
            person = ctx.author
        person = str(person)
        if person.isnumeric():
            member = ctx.guild.get_member(int(person))
            if not member:
                pass
            else:
                person = member
        person = str(person)

        nab = random.randint(0,100)

        embed=discord.Embed(description=f"**{person}'s Nab Rate**\n{nab}% Nab")

        await ctx.reply(embed = embed)

        if nab == 100:
            await self.grant_badge(ctx,ctx.author.id,"nab")

    @commands.command(description = "Roast a fellow member.",help = "roast <user>",brief= "Don't take these too seriously, they are meant to be fun.")
    @commands.cooldown(1,10,commands.BucketType.user)
    async def roast(self,ctx,person:discord.Member):
        roasts = random.randint(0,len(self.roasts)-1)

        if person == ctx.author:
            return await ctx.reply("Imagine, trying to roast yourself. Do better.")
        elif person.bot:
            return await ctx.reply("Looks like you ran out of people to roast, are you trying to roast a bot? Must be sad to be that lonely.")
        await ctx.reply(f"{person.mention} {self.roasts[roasts]}")


    @commands.command(description = 'Drop a prize for others to pick up!',help = "drop <item> [channel] [word]",brief = 'Command has changed to what it once was, but now with quotes for easier usage.'
     + '\n\nExample:\n\n`o!drop "discord nitro" #general "nitro is mine!"`\n`o!drop nitro`\n`o!drop "nitro boost"`')
    @giveaway_role_check()
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def drop(self,ctx,item,channel : discord.TextChannel = None,word = None):
        wordlist = ["claim","grab","oasis","steal","mine","give","clutch","snatch","take","swipe"]
        channel = channel or ctx.channel


        word = word or wordlist[random.randint(0,len(wordlist)-1)]

        embed=discord.Embed(title=f"Someone has dropped {item} in this channel!",description=f"Type the words `{word}` to claim!", color=discord.Color.random())
        message = await channel.send(embed=embed)

        if not channel == ctx.channel:
            await ctx.reply(f"<a:PB_greentick:865758752379240448> Successfully dropped!")

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
            await message.channel.send("You took too long, and the drop is now cancelled!")
            await ctx.reply(f"Your drop was cancelled, since no one responded.")
            return
        await channel.send(f"Claimed by {msg.author.mention} :tada:")
        await ctx.reply(f"{ctx.author.mention} your prize was claimed! Please give {item} to {msg.author.mention}")

    @commands.command(description = 'How many people have been banned here...',help = "bans")
    @commands.cooldown(rate=1, per=5)
    async def bans(self,ctx):
        guild = ctx.guild
        banned_users = await ctx.guild.bans()
        await ctx.reply(f'{guild} has **{len(banned_users)}** banned users.')


    @commands.command(aliases = ['gtn'],description = "Host a guess the number game in the channel.",help = "guessthenumber [start] [end] [number] [channel]")
    async def guessthenumber(self,ctx,start:int = None,end:int = None,target:int = None,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        if not start: start = 1
        if not end: end = start + 99
        if not target: target = random.randint(start,end)
        if start < 0 or end < 0 or start >= end or target < start or target > end or target < 0: return await ctx.reply("Yea that doesn't look like valid input.")

        embed = discord.Embed(title = "Guess the Number!",description = f"The range for this game is **{start}** - **{end}**",color = discord.Color.random())
        embed.set_author(name="Hosted by " + ctx.author.display_name,icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text = f"Good luck! You have 2 minutes to guess. {target}")
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

    @commands.command(description = "How good is your memory?",help = "colorgame")
    async def colorgame(self,ctx):
        order = []
        buttons = [[Button(emoji = self.client.get_emoji(904111618391158875),style = 1),Button(emoji = self.client.get_emoji(904112302918369301),style = 2)],[Button(emoji = self.client.get_emoji(904112314393968740),style = 3),Button(emoji = self.client.get_emoji(904112322484789338),style = 4)]]
        buttons1 = [[Button(emoji = self.client.get_emoji(904111618391158875),style = 1,disabled = False),Button(emoji = self.client.get_emoji(904112302918369301),style = 2,disabled = True)],[Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = True),Button(emoji = self.client.get_emoji(904112322484789338),style = 4,disabled = True)]]
        buttons2 = [[Button(emoji = self.client.get_emoji(904111618391158875),style = 1,disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),style = 2,disabled = False)],[Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = True),Button(emoji = self.client.get_emoji(904112322484789338),style = 4,disabled = True)]]
        buttons3 = [[Button(emoji = self.client.get_emoji(904111618391158875),style = 1,disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),style = 2,disabled = True)],[Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = False),Button(emoji = self.client.get_emoji(904112322484789338),style = 4,disabled = True)]]
        buttons4 = [[Button(emoji = self.client.get_emoji(904111618391158875),style = 1,disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),style = 2,disabled = True)],[Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = True),Button(emoji = self.client.get_emoji(904112322484789338),style = 4,disabled = False)]]
        buttonsa = [[Button(emoji = self.client.get_emoji(904111618391158875),style = 1,disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),style = 2,disabled = True)],[Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = True),Button(emoji = self.client.get_emoji(904112322484789338),style = 4,disabled = True)]]
        embed = discord.Embed(description = f"{ctx.author.mention} **Color Game**\nLevel 1\nWatch what colors are displayed!",color = discord.Color.random())
        level = 1
        message = await ctx.send(embed = embed,components = buttons)
        def check(i):
            if i.message.id == message.id and i.author.id == ctx.author.id:
                return True
            else:
                return False
        while True:
            color = random.randint(1,4)
            order.append(color)

            for current in order:
                if current == 1:
                    await message.edit(embed = embed,components = buttons1)
                elif current == 2:
                    await message.edit(embed = embed,components = buttons2)
                elif current == 3:
                    await message.edit(embed = embed,components = buttons3)
                elif current == 4:
                    await message.edit(embed = embed,components = buttons4)    
                await asyncio.sleep(0.7)
                await message.edit(embed = embed,components = buttonsa)
                await asyncio.sleep(0.7)
            embed = discord.Embed(description = f"{ctx.author.mention} **Color Game**\nLevel {level}\nRepeat those colors now!",color = discord.Color.random())
            await message.edit(embed = embed,components = buttons)

            for current in order:
                try:
                    interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
                except asyncio.TimeoutError:
                    return await ctx.send("Well you took too long to respond. Try again next time.")
                
                if interaction.component.style == current:
                    if not interaction.responded:
                        await interaction.respond(type = 6)
                    continue
                else:
                    if current == 1: color = "Blue"
                    elif current == 2: color = "Gray"
                    elif current == 3: color = "Green"
                    elif current == 4: color = "Red"
                    embed = discord.Embed(description = f"You lost! The color was **{color}**. You made it to level **{level}**")
                    await interaction.respond(embed = embed,ephemeral = False)
                    embed = discord.Embed(description = f"{ctx.author.mention} **Color Game**\nLevel {level}\nYou Lose!",color = discord.Color.red())
                    await message.edit(embed = embed, components = buttonsa)
                    if level >= 20:
                        await self.grant_badge(ctx,ctx.author.id,"color")
                    return

            level += 1
            embed = discord.Embed(description = f"{ctx.author.mention} **Color Game**\nLevel {level}\nWatch what colors are displayed!",color = discord.Color.random())
            await message.edit(embed = embed, components = buttonsa)
            await asyncio.sleep(1)         




    @commands.command(description = "A fun fight, where you pick items and battle to the death.",help = 'fight <user>',brief = "You can get some cool badges from this command, and there is a leaderboard too which is pretty cool.")
    @commands.cooldown(1, 30,commands.BucketType.user)
    async def fight(self,ctx,user: discord.Member):
        if ctx.author.id in self.fighters or user.id in self.fighters:
            return await ctx.reply("Hold up, either you or your opponent is in a fight already. Take a chill pill and relax buddy.\nPOV: Fight broke because of interaction? Try `o!fixfight`!")
        elif ctx.author.id == user.id:
            return await ctx.reply("Hey, you can't fight yourself. Find another person to fight instead.")

        userchoosen = ""
        ctxchoosen = ""
        ctxhealth = 100
        ctxdefense = 0
        userhealth = 100
        userdefense = 0
        message = await ctx.reply(f"{user.mention}, {ctx.author.mention} is challenging you to a fight! Do you accept?",components = [
                [Button(emoji = "✅",style = 3),Button(emoji = "✖",style = 4)]
            ])

        def check(i):
            if i.message.id == message.id:
                return True
            else:
                return False

        while True:
            try:
                interaction = await self.client.wait_for("button_click", timeout = 60.0,check = check)
            except asyncio.TimeoutError:
                return await ctx.send("Well you took too long to respond. Try again next time.")

            if not interaction.user.id == user.id:
                embed=discord.Embed(description=f"Only {user.mention} can accept or deny the fight request!", color=discord.Color.red())
                await interaction.respond(embed = embed)
                continue

            if str(interaction.component.emoji) == "✖":
                return await interaction.respond(content = "Well it seems your fight request was denied. Sad.",ephemeral  = False)
            else:
                break
        if ctx.author.id in self.fighters or user.id in self.fighters:
            return await ctx.reply("Hold up, either you or your opponent is in a fight already. Take a chill pill and relax buddy.")
        self.fighters.append(user.id)
        self.fighters.append(ctx.author.id)
        await asyncio.sleep(1)

        embed=discord.Embed(title = "The fight begins!",description=f"First, it is time to pick your item. Both of you will choose one item. You have 30 seconds to choose.", color=discord.Color.random())
        embed.add_field(name = "Passive Items",value = "These items give passive boosts, meaning that they are active during the entire fight.")
        embed.add_field(name = "Active Items",value = "These items open up an option during the fight, depending on what you choose. Using these items will be your turn in the fight.")

        selectslist = [
            SelectOption(value = "None",label = "No Item",description = "No item? No problem. Do it old style.",default = True),
            SelectOption(value = "Shield",label = "Shield (passive)",description = "Gives chance to block your opponent's attack.",emoji = self.client.get_emoji(865758696579006495)),
            SelectOption(value = "Clover",label = "Clover (passive)",description = "A higher chance to have a successful hit.",emoji = self.client.get_emoji(865759726961033288)),
            SelectOption(value = "Potion",label = "Potion (passive)",description = "Less damage taken by all hits.",emoji = self.client.get_emoji(865758671313174549)),
            SelectOption(value = "Sword",label = "Sword (active)",description = "High damage but a high chance of failure.",emoji = self.client.get_emoji(865758905220202506)),
            SelectOption(value = "Axe",label = "Axe (active)",description = "Medium damage, but a less chance of fail against sword.",emoji = self.client.get_emoji(865758717004742706)),
            SelectOption(value = "Armor",label = "Armor (active)",description = "Opens option to defend, decreases the atk from attacker.",emoji = self.client.get_emoji(865759592259256361)),
            SelectOption(value = "Crossbow",label = "Crossbow (unlockable) (active)",description = "A very reliable item, with good damage.",emoji = self.client.get_emoji(878828750811312138)),
            SelectOption(value = "Rocket Launcher",label = "Rocket Launcher (unlockable) (active)",description = "Wait a minute, this item doesn't fit with the others.",emoji = self.client.get_emoji(878829510294925362)),
            ]
        embed.set_footer(text = f"Both parties should select weapons now!")
        message = await ctx.send(embed = embed,components = [Select(options =selectslist )])
        
        if not interaction.responded:
            await interaction.respond(type = 6)

        ctxc,ctxrl = await self.get_items(ctx,ctx.author.id)
        userc,userrl = await self.get_items(ctx,user.id)

        while True:
            if ctxchoosen != "" and userchoosen != "":
                await message.edit(components = [Select(options =selectslist,disabled = True)])
                break
            try:
                interaction = await self.client.wait_for("select_option", timeout = 30.0,check = check)
            except asyncio.TimeoutError:
                self.fighters.remove(user.id)
                self.fighters.remove(ctx.author.id)
                return await ctx.send("Well you took too long to respond. Try again next time.")

            if not (interaction.user.id == ctx.author.id or interaction.user.id == user.id):
                embed=discord.Embed(description=f"Only people fighting can choose weapons!", color=discord.Color.red())
                if not interaction.responded:
                    await interaction.respond(embed = embed)
                continue

            if interaction.user.id == ctx.author.id:
                if ctxchoosen != "":
                    await interaction.respond(content = f"Hey, you already made your choice")
                    continue
                ctxchoosen = interaction.values[-1]
                if ctxchoosen == "Crossbow" and not ctxc:
                    if not interaction.responded:
                        await interaction.respond(content = f"Hey, you don't have the crossbow unlocked")
                    ctxchoosen = ""
                elif ctxchoosen == "Rocket Launcher" and not ctxrl:
                    if not interaction.responded:
                        await interaction.respond(content = f"Hey, you don't have the rocket launcher unlocked")
                    ctxchoosen = ""
                elif not interaction.responded:
                    await interaction.respond(content = f"{ctx.author.mention} has chosen {ctxchoosen}!",ephemeral  = False)
            elif interaction.user.id == user.id:
                if userchoosen != "":
                    await interaction.respond(content = f"Hey, you already made your choice")
                    continue
                userchoosen = interaction.values[-1]
                if userchoosen == "Crossbow" and not userc:
                    if not interaction.responded:
                        await interaction.respond(content = f"Hey, you don't have the crossbow unlocked")
                    userchoosen = ""
                elif userchoosen == "Rocket Launcher" and not userrl:
                    if not interaction.responded:
                        await interaction.respond(content = f"Hey, you don't have the rocket launcher unlocked")
                    userchoosen = ""
                elif not interaction.responded:
                    await interaction.respond(content = f"{user.mention} has chosen {userchoosen}!",ephemeral  = False)

            if ctxchoosen != "" and userchoosen != "":
                await message.edit(components = [Select(options =selectslist,disabled = True)])
                break


        embed=discord.Embed(title = f"Let the fight Begin!",description=f"", color=discord.Color.random())

        if ctxchoosen in ["Sword","Axe","Armor","Crossbow","Rocket Launcher"]:
            ctxbuttons = [Button(label = "Punch",style = 1),Button(label = "Smack",style = 1),Button(label = "Kick",style = 1),Button(label = ctxchoosen,style = 1),Button(label = "End",style = 2)]
        else:
            ctxbuttons = [Button(label = "Punch",style = 1),Button(label = "Smack",style = 1),Button(label = "Kick",style = 1),Button(label = "End",style = 2)]

        if userchoosen in ["Sword","Axe","Armor","Crossbow","Rocket Launcher"]:
            userbuttons = [Button(label = "Punch",style = 4),Button(label = "Smack",style = 4),Button(label = "Kick",style = 4),Button(label = userchoosen,style = 4),Button(label = "End",style = 2)]
        else:
            userbuttons = [Button(label = "Punch",style = 4),Button(label = "Smack",style = 4),Button(label = "Kick",style = 4),Button(label = "End",style = 2)]

        starter = random.randint(0,2)
        if starter == 0:
            turn = ctx.author
        else:
            turn = user

        description = "Who will prevail? Who will see their end?"
        embed=discord.Embed(title = f"The fight begins!",description=description, color=discord.Color.random())
        embed.add_field(name = ctx.author,value = f"**Player Health:** `{ctxhealth}`\n**Player Defense:** `{ctxdefense}`\n**Special Item:** `{ctxchoosen}`")
        embed.add_field(name = user,value = f"**Player Health:** `{userhealth}`\n**Player Defense:** `{userdefense}`\n**Special Item:** `{userchoosen}`")
        embed.set_footer(text = f"{turn}'s Turn to Choose! You have 30 seconds.")
        message = await ctx.send(embed = embed)
        while True:
            embed=discord.Embed(title = f"The fight begins!",description=description, color=discord.Color.random())
            embed.add_field(name = ctx.author,value = f"**Player Health:** `{ctxhealth}`\n**Player Defense:** `{ctxdefense}`\n**Special Item:** `{ctxchoosen}`")
            embed.add_field(name = user,value = f"**Player Health:** `{userhealth}`\n**Player Defense:** `{userdefense}`\n**Special Item:** `{userchoosen}`")
            embed.set_footer(text = f"{turn}'s Turn to Choose! You have 30 seconds.")
            if turn == ctx.author:
                await message.edit(ctx.author.mention,embed = embed,components = [ctxbuttons])
            else:
                await message.edit(user.mention,embed = embed,components = [userbuttons])
            description = ""
            while True:
                try:
                    interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
                except asyncio.TimeoutError:
                    await ctx.send("Well you took too long to respond. Try again next time.")
                    self.fighters.remove(user.id)
                    self.fighters.remove(ctx.author.id)
                    return

                if not interaction.user.id == turn.id:
                    embed=discord.Embed(description=f"Only {turn.mention} can choose an action!", color=discord.Color.red())
                    if not interaction.responded:
                        await interaction.respond(embed = embed)
                    continue

                choice = interaction.component.label
                failmax = 101
                if turn == ctx.author and ctxchoosen == "Clover":
                    failmax = 350
                elif turn == user and userchoosen == "Clover":
                    failmax = 350
                
                failrate = random.randint(1,failmax)
                fail = False
                knockback = 0
                damage = 0
                buffdef = 0
                if choice == "Sword":
                    damage = random.randint(30,40)
                    if failrate <= 40:
                        fail = True
                        description = f"**{turn}** tried to use their sword, but they missed the stab!"
                elif choice == "Axe":
                    damage = random.randint(20,30)
                    if failrate <= 25:
                        fail = True
                        description = f"**{turn}** tried to use their axe, but they hit a tree instead. How unfortunate"
                elif choice == "Punch":
                    damage = random.randint(5,15)
                    if failrate <= 5:
                        fail = True
                        description = f"**{turn}** tried to punch, but somehow they missed! How unlucky."
                elif choice == "Smack":
                    damage = random.randint(10,30)
                    if failrate <= 20:
                        fail = True
                        description = f"**{turn}** tried smack but missed the opponent. Someone needs a lesson in smacking"
                elif choice == "Kick":
                    damage = random.randint(30,50)
                    if failrate <= 50:
                        fail = True
                        knockback = random.randint(5,20)
                        description = f"**{turn}** tried to kick but failed and fell down! \nThis caused **{turn}** to suffer `{knockback}` points of damage!"
                elif choice == "Armor":
                    buffdef = random.randint(15,40)
                    description = f"**{turn}** used a bit of armor! They protect themselves, increasing their defense by `{buffdef}`"
                elif choice == "Crossbow":
                    damage = random.randint(25,35)
                    if failrate <= 3:
                        fail = True
                        description = f"**{turn}** tried use their crossbow, but it snapped and failed. How did that happen?"
                elif choice == "Rocket Launcher":
                    damage = random.randint(40,60)
                    if failrate <= 25:
                        fail = True
                        knockback = random.randint(14,40)
                        description = f"**{turn}** shot their rocket, but it blew up in their face instead!\nThis caused **{turn}** to suffer `{knockback}` points of damage"
                elif choice == "End":
                    self.fighters.remove(user.id)
                    self.fighters.remove(ctx.author.id)
                    return await interaction.respond(content = f"**{turn}** ended the battle, seems like a coward to me.",ephemeral  = False)
                
                if turn == ctx.author:
                    if userchoosen == "Shield" and damage > 0:
                        shield = random.randint(1,100)
                        if shield <= 25:
                            description = description or f"**{turn}** had a successful hit of `{damage}` damage, however {user}'s `shield` blocked the hit!"
                            break
                    if fail:
                        ctxhealth -= knockback
                    else:
                        if userchoosen == "Potion":
                            realdamage = int(damage * 0.8)
                            description = description or f"**{turn}** used `{choice}`! It caused their opponent to take `{realdamage}` damage after {user}'s `potion` effect!"
                        elif userchoosen == "Armor":
                            realdamage = int(damage * (1-(userdefense/100)))
                            description = description or f"**{turn}** used `{choice}`! It caused their opponent to take `{realdamage}` damage after {user}'s `armor`!"
                        else:
                            realdamage = damage
                        ctxdefense += buffdef
                        userhealth -= realdamage

                        if ctxdefense > 100:
                            ctxdefense = 100
                else:
                    if ctxchoosen == "Shield" and damage > 0:
                        shield = random.randint(1,100)
                        if shield <= 25:
                            description = description or f"**{turn}** had a successful hit of `{damage}` damage, however {ctx.author}'s `shield` blocked the hit!"
                            break
                    if fail:
                        userhealth -= knockback
                    else:
                        if ctxchoosen == "Potion":
                            realdamage = int(damage * 0.8)
                            description = description or f"**{turn}** used `{choice}`! It caused their opponent to take `{realdamage}` damage after {ctx.author}'s `potion` effect!"
                        elif ctxchoosen == "Armor":
                            realdamage = int(damage * (1-(ctxdefense/100)))
                            description = description or f"**{turn}** used `{choice}`! It caused their opponent to take `{realdamage}` damage after {ctx.author}'s `armor`!"
                        else:
                            realdamage = damage
                        userdefense += buffdef
                        ctxhealth -= realdamage

                        if userdefense > 100:
                            userdefense = 100

                if description == "":
                    description = f"**{turn}** used `{choice}`! It caused their opponent to take `{damage}` damage!"

                if not interaction.responded:
                    await interaction.respond(type = 6)
                break

            if turn == ctx.author:
                turn = user
            else:
                turn = ctx.author

            if ctxhealth <= 0:
                wins = await self.add_fight_stat(ctx,user.id,"win")
                losses = await self.add_fight_stat(ctx,ctx.author.id,"lose")
                embed=discord.Embed(title = f"The fight is Over!",description=f'{description}\n**{user}** is the winner! 🏆', color=discord.Color.gold())
                embed.add_field(name = ctx.author,value = f"**Player Health:** `0`\n**Player Defense:** `{ctxdefense}`\n**Special Item:** `{ctxchoosen}`")
                embed.add_field(name = user,value = f"**Player Health:** `{userhealth}`\n**Player Defense:** `{userdefense}`\n**Special Item:** `{userchoosen}`")
                embed.set_footer(text = f"{user} has won {wins} fights | {ctx.author} has lost {losses} fights")
                await message.edit(embed = embed)

                if wins >= 50:
                    await self.grant_badge(ctx,user.id,"fighter1")
                elif wins >= 100:
                    await self.grant_badge(ctx,user.id,"fighter2")
                break
            elif userhealth <= 0:
                wins = await self.add_fight_stat(ctx,ctx.author.id,"win")
                losses = await self.add_fight_stat(ctx,user.id,"lose")
                embed=discord.Embed(title = f"The fight is Over!",description=f'{description}\n{ctx.author} is the winner! 🏆', color=discord.Color.gold())
                embed.add_field(name = ctx.author,value = f"**Player Health:** `{ctxhealth}`\n**Player Defense:** `{ctxdefense}`\n**Special Item:** `{ctxchoosen}`")
                embed.add_field(name = user,value = f"**Player Health:** `0`\n**Player Defense:** `{userdefense}`\n**Special Item:** `{userchoosen}`")
                embed.set_footer(text = f"{ctx.author} has won {wins} fights | {user} has lost {losses} fights")
                await message.edit(embed = embed)

                if wins >= 50:
                    await self.grant_badge(ctx,ctx.author.id,"fighter1")
                elif wins >= 100:
                    await self.grant_badge(ctx,ctx.author.id,"fighter2")
                break
        self.fighters.remove(user.id)
        self.fighters.remove(ctx.author.id)
    

    @commands.command(description = "That fight command break again? Run this to fix your problems.",help = "fixfight",brief = "Note that this can't fix your life problems...sorry about that.")
    async def fixfight(self,ctx):
        try:
            self.fighters.remove(ctx.author.id)
            await ctx.reply("You were removed from the fighters list.")
        except:
            await ctx.reply("You sure you were in the fighters list anyways?")

    @commands.command(hidden = True)
    @commands.is_owner()
    async def badgeadd(self,ctx,member:discord.Member,badge):
        output = await self.grant_badge(ctx,member.id,badge)
        if output:
            return await ctx.reply(f"<a:PB_greentick:865758752379240448> **{member}** was given the **{badge}** badge.")
        else:
            return await ctx.reply("Badge was not granted. Are you sure that badge exsists, and that this member does not already have the badge?")
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def badgeremove(self,ctx,member:discord.Member,badge):
        output = await self.remove_badge(ctx,member.id,badge)
        if output:
            return await ctx.reply(f"<a:PB_greentick:865758752379240448> **{member}** was removed of the **{badge}** badge.")
        else:
            return await ctx.reply("Badge was not removed. Are you sure that badge exsists, and this member has the badge you are removing?")

    @commands.command(description = "View the global fight leaderboard!",help = "fightlb [category]",brief = "There are 3 categories: total, win, and lose.")
    async def fightlb(self,ctx,category = "total"):
        await self.get_fight_lb(ctx,category)

    @commands.command(description = "View your profile, with badges and fight stats.",help = "profile [member]")
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
        

def setup(client):
    client.add_cog(Fun(client))
