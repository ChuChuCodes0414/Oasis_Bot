import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button
import datetime
import math
import firebase_admin
from firebase_admin import db
import random
import asyncio
import uuid
from pythonvariables import winterdata

class Winter(commands.Cog):
    '''
        Winter drops for winter! Use help command for more info.
    '''
    def __init__(self,client):
        self.client = client
        self.replybegin = "<:replybegin:913966561075822744>"
        self.replyend = "<:replyend:913967325429002302>"
        self.replyline = "<:replyline:913967318378352652>"
        self.replycont = "<:replycont:913966803263291422>"
        self.emoji = "<:gingerbread:911437212283985930>"
        self.item = "gingerbread"
        self.event = "winter"
        self.choices = ["button","phrase","unscramble","boss","word","fastclick"]
        self.titles = [f"Quick, {self.item}s are being dropped!",f"Someone dropped some {self.item}s!",f"You found {self.item}s in the oven!!",f"Oh, {self.item}s!"]
        self.phrasestext = winterdata.WINTER_PHRASESTEXT
        self.phrases = winterdata.WINTER_PHRASES
        self.wordstext = winterdata.WINTER_WORDTEXT
        self.words = winterdata.WINTER_WORDS
        self.active = []
        self.disabled = {}
        self.slowmode = []
    
    @commands.Cog.listener()
    async def on_ready(self):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        data = ref.get()

        for guild,guilddata in data.items():
            thanksgiving = guilddata.get(self.event,None)
            if thanksgiving:
                if thanksgiving.get("enabled",False):
                    self.active.append(int(guild))
                disabled = thanksgiving.get("disabled",[])
                build = []
                for channel in disabled:
                    build.append(int(channel))
                if len(build) > 0:
                    self.disabled[int(guild)] = build

        print('Winter Cog Loaded, and channels cached.')

    def teams_check():
        async def predicate(ctx):
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            if not ref.child(str(ctx.guild.id)).child("winter").child("team").get():
                return False
            else:
                return True
        return commands.check(predicate)
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def wintercache(self,ctx):
        await ctx.send(self.active)
        await ctx.send(self.disabled)
        await ctx.send(f"{len(self.phrases)} | {len(self.phrasestext)}")
        await ctx.send(f"{len(self.words)} | {len(self.wordstext)}")
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def cachewinter(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        data = ref.get()
        for guild,guilddata in data.items():
            thanksgiving = guilddata.get(self.event,None)
            if thanksgiving:
                if thanksgiving.get("enabled",False):
                    self.active.append(int(guild))
                disabled = thanksgiving.get("disabled",[])
                build = []
                for channel in disabled:
                    build.append(int(channel))
                if len(build) > 0:
                    self.disabled[int(guild)] = build
        await ctx.send("cached?")

    async def add_items(self,guild,user,amount):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        data = ref.child(self.event).child(str(guild.id)).child("players").child(str(user.id)).child("amount").get() or 0
        ref.child(self.event).child(str(guild.id)).child("players").child(str(user.id)).child("amount").set(data + amount)
        return True
        
    @commands.Cog.listener()
    async def on_message(self,message):
        if not message.guild:
            return
        if message.guild.id not in self.active or message.author.bot or message.channel.id in self.disabled.get(message.guild.id,[]):
            return

        chance = random.randint(1,100)
        if message.guild.id == 798822518571925575:
            try:
                author = message.author
                role = message.guild.get_role(910813134099476511)
                if role in author.roles:
                    if not chance <= 3:
                        return
                elif not chance<= 2:
                    return
            except:
                pass
        elif not chance <= 2:
            return
        event = self.choices[random.randint(0,len(self.choices)-1)]
        await self.event_spawn(event, message,None,None)

    async def event_spawn(self,event,message,option = None,secondary = None):
        if event == "button":
            title = self.titles[random.randint(0,len(self.titles))-1]
            embed = discord.Embed(title = title,description = "Be the first to click the button to claim!",color = discord.Color.gold())
            message = await message.channel.send(embed = embed,components = [Button(label = f"Claim {self.item}s",style = 3)])

            def check(i):
                if i.message.id == message.id:
                    return True
                else:
                    return False

            try:
                interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
            except asyncio.TimeoutError:
                return await message.edit("The drop timed out. Are yall dead?",embed = embed, components = [Button(label = f"Claim {self.item}s",style = 3,disabled = True)])
                
            await message.edit("Drop Claimed!",embed = embed, components = [Button(label = f"Claim {self.item}s",style = 2,disabled = True)])

            amount = random.randint(50,100)
            embed = discord.Embed(description = f"{interaction.user.mention} Claimed **{amount} {self.emoji}**",color = discord.Color.green())
            embed.set_footer(text = f"Use [prefix]{self.item} to see how much {self.item} you have!")
            await self.add_items(message.guild,interaction.user,amount)
            return await interaction.respond(embed = embed,ephemeral = False)
        elif event == "phrase":
            title = self.titles[random.randint(0,len(self.titles))-1]
            num = random.randint(0,len(self.phrases)-1)
            phrase = self.phrases[num]
            phrasetext = self.phrasestext[num]

            embed = discord.Embed(title = title,description = f"Type the phrase\n\n{phrasetext}\n\nto pick it up!",color = discord.Color.gold())
            message = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == message.channel.id and i.content == phrasetext:
                    return True
                if i.channel.id == message.channel.id and i.content == phrase:
                    return True
                else:
                    return False
            
            while True:
                try:
                    message = await self.client.wait_for("message",timeout = 45.0,check = check)
                except asyncio.TimeoutError:
                    return await message.edit("The drop timed out. Are yall dead?")

                if message.content == phrasetext:
                    await message.reply("You cheating mf, nice try.")
                else:
                    break
            
            amount = random.randint(300,500)
            embed = discord.Embed(description = f"{message.author.mention} Claimed **{amount} {self.emoji}**",color = discord.Color.green())
            embed.set_footer(text = f"Use [prefix]{self.item} to see how much {self.item} you have!")
            await self.add_items(message.guild,message.author,amount)
            await message.reply(embed = embed)
        elif event == "word":
            title = self.titles[random.randint(0,len(self.titles))-1]
            num = random.randint(0,len(self.words)-1)
            word = self.words[num]
            wordtext = self.wordstext[num]

            embed = discord.Embed(title = title,description = f"Type the word\n\n{wordtext}\n\nto pick it up!",color = discord.Color.gold())
            message = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == message.channel.id and i.content.lower() == wordtext:
                    return True
                if i.channel.id == message.channel.id and i.content.lower() == word:
                    return True
                else:
                    return False

            while True:
                try:
                    message = await self.client.wait_for("message",timeout = 30.0,check = check)
                except asyncio.TimeoutError:
                    return await message.edit("The drop timed out. Are yall dead?")

                if message.content == wordtext:
                    await message.reply("You cheating mf, nice try.")
                else:
                    break
            
            amount = random.randint(100,200)
            embed = discord.Embed(description = f"{message.author.mention} Claimed **{amount} {self.emoji}**",color = discord.Color.green())
            embed.set_footer(text = f"Use [prefix]{self.item} to see how much {self.item} you have!")
            await self.add_items(message.guild,message.author,amount)
            await message.reply(embed = embed)
        elif event == "unscramble":
            title = self.titles[random.randint(0,len(self.titles))-1]
            word = self.words[random.randint(0,len(self.words)-1)]
            scrambled = list(word)
            random.shuffle(scrambled)
            scrambled = ''.join(scrambled)

            embed = discord.Embed(title = title,description = f"Unscramble\n\n{scrambled}\n\nto pick it up!",color = discord.Color.gold())
            message = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == message.channel.id and i.content == word:
                    return True
                else:
                    return False
            
            try:
                message = await self.client.wait_for("message",timeout = 30.0,check = check)
            except asyncio.TimeoutError:
                return await message.edit("The drop timed out. Are yall dead?")
            
            amount = random.randint(300,600)
            embed = discord.Embed(description = f"{message.author.mention} Claimed **{amount} {self.emoji}**",color = discord.Color.green())
            embed.set_footer(text = f"Use [prefix]{self.item} to see how much {self.item} you have!")
            await self.add_items(message.guild,message.author,amount)
            await message.reply(embed = embed)
        elif event == "boss":
            mega = option or random.randint(0,100)
            if mega >= 10:
                type = secondary or random.randint(0,1000)
                if type <= 20:
                    type = "legendary"
                    title = "🟨 Legendary BOSS!"
                    description = f"Jeez this thing has a lot of health! Take it down to grab it's {self.item}!"
                    footer = f"Kill the boss to receieve 4000 {self.item}s!!! This boss has a 2% Chance of Spawning."
                    multiplier = 60
                    final = 4000
                    health = 2000
                elif type <= 110:
                    type = "epic"
                    title = "🟪 Epic Boss!"
                    description = f"Nice, it has {self.item}s. Hit the button to grab it's {self.item}s!"
                    footer = f"Kill the boss to receieve 2,000 {self.item}s! This boss has a 9% Chance of Spawning."
                    multiplier = 12
                    final = 2000
                    health = 400
                elif type <= 310:
                    type = "rare"
                    title = "🟦 Rare Boss!"
                    description = f"Not quite the rarest boss, but it still has {self.item}s! Let's go for it."
                    footer = f"Kill the boss to receieve 500 {self.item}s! This boss has a 20% Chance of Spawning."
                    multiplier = 3
                    final = 500
                    health = 200
                elif type <= 610:
                    type = "uncommon"
                    title = "🟩 Uncommon Boss"
                    description = f"Not quite the rarest boss, but it still has {self.item}! Let's go for it."
                    footer = f"Kill the boss to receieve 100 {self.item}s! This boss has a 30% Chance of Spawning."
                    multiplier = 1
                    final = 100
                    health = 150
                else:
                    type = "common"
                    title = "⬜ Common Boss"
                    description = f"Might as well take a shot at this, it's free {self.item}." 
                    footer = f"Kill the boss to receieve 50 {self.item}s! This boss has a 39% Chance of spawning"
                    multiplier = 0.5
                    final = 50
                    health = 100
                
                edescription = description + f"\n\n**Boss Health 😡:** {health}/{health}"
                embed = discord.Embed(title = title,description = edescription,color = discord.Color.random())
                embed.set_footer(text = footer)
                current = health
                message = await message.channel.send(embed = embed,components = [Button(label = "Hit Boss",style = 4)])

                def check(i):
                    if i.message.id == message.id:
                        return True
                    else:
                        return False

                hitters = {}
                while True:
                    try:
                        try:
                            interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
                        except asyncio.TimeoutError:
                            return await message.edit("The boss ran. Are yall dead?",embed = embed, components = [Button(label = "Hit Boss",style = 4,disabled = True)])

                        kick = random.randint(5,30)
                        current -= kick

                        if current <= 0:
                            current = 0
                            finalkick = interaction.user
                            embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}"
                            await message.edit(embed = embed)
                            await interaction.respond(type = 6)
                            hitters[interaction.user] = hitters.get(interaction.user,0) + 0
                            await message.edit("The boss was defeated!",embed = embed, components = [Button(label = "Hit Boss",style = 4,disabled = True)])
                            break
                        
                        embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}"
                        await message.edit(embed = embed)
                        await interaction.respond(type = 6)
                        hitters[interaction.user] = hitters.get(interaction.user,0) + kick
                    except:
                        pass
                
                pot = len(hitters) * 100 * multiplier
                description = ""
                for hitter,kicked in hitters.items():
                    if hitter == finalkick:
                        given = int(final + pot * (kicked/health))
                        msg = f"**{hitter.name}** got the final hit! They got **{given} {self.emoji}**\n"
                        await self.add_items(message.guild,hitter,given)
                    else:
                        given = int(pot * (kicked/health))
                        msg = f"**{hitter.name}** got **{given} {self.emoji}**\n"
                        await self.add_items(message.guild,hitter,given)
                
                    description += msg
                embed = discord.Embed(description = description,color = discord.Color.gold())
                await message.reply(embed = embed)
            else:
                type = secondary or random.randint(1,100)
                if type == 1:
                    type = "gold"
                    title = f"{self.client.get_emoji(908552154254573638)} Gold MEGABOSS!"
                    description = "The boss will not stick around long! Target the weak points!"
                    footer = f"Kill the boss to receieve 30000 {self.item}s!!! This boss has a 1% Chance of Spawning."
                    multiplier = 280
                    final = 30000
                    weak = 1000
                    health = 10000
                    color = discord.Color.gold()
                elif type <= 21:
                    type = "silver"
                    title = f"{self.client.get_emoji(908552154166468609)} Silver MEGABOSS!"
                    description = "The boss will not stick around long! Target the weak points!"
                    footer = f"Kill the boss to receieve 10000 {self.item}s!!! This boss has a 20% Chance of Spawning."
                    multiplier = 140
                    final = 10000
                    weak = 700
                    health = 5000
                    color = discord.Color.lighter_grey()
                else:
                    type = "bronze"
                    title = f"{self.client.get_emoji(908552154275545138)} Bronze MEGABOSS!"
                    description = "The boss will not stick around long! Target the weak points!"
                    footer = f"Kill the boss to receieve 5000 {self.item}s!!! This boss has a 79% Chance of Spawning."
                    multiplier = 70
                    weak = 400
                    final = 5000
                    health = 1000
                    color = discord.Color.from_rgb(205, 127, 50)
                
                edescription = description + f"\n\n**Boss Health 😡:** {health}/{health}\n**Weak Point:** {weak}/{weak} | 1/4"
                embed = discord.Embed(title = title,description = edescription,color = color)
                embed.set_footer(text = footer)
                buttons = [[Button(label = "Hit Boss"),Button(label = "Hit Boss"),Button(label = "Hit Boss"),Button(label = "Hit Boss")]]
                dbuttons = [[Button(label = "Hit Boss",disabled = True),Button(label = "Hit Boss",disabled = True),Button(label = "Hit Boss",disabled = True),Button(label = "Hit Boss",disabled = True)]]
                weakb = random.randint(0,3)
                buttons[0][weakb] = Button(label = "Hit Weak Point!",style = 3)

                message = await message.channel.send(embed = embed,components = buttons)

                def check(i):
                    if i.message.id == message.id:
                        return True
                    else:
                        return False

                hitters = {}
                currentweak = weak
                current = health
                weakpoint = 1
                while True:
                    try:
                        try:
                            interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
                        except asyncio.TimeoutError:
                            if weakpoint < 5:
                                dbuttons[0][weakb] = Button(label = "Hit Weak Point!",style = 3,disabled = True)
                            return await message.edit("The boss ran. Are yall dead?",embed = embed, components = dbuttons)

                        if weakpoint < 5:
                            if interaction.component.label == "Hit Weak Point!":
                                kick = random.randint(20,60)
                                currentweak -= kick
                                hitters[interaction.user] = hitters.get(interaction.user,0) + kick
                            else:
                                kick = random.randint(1,5)
                                current -= kick
                                hitters[interaction.user] = hitters.get(interaction.user,0) + kick
                        else:
                            kick = random.randint(50,100)
                            current -= kick
                            hitters[interaction.user] = hitters.get(interaction.user,0) + kick
                        
                        if current <= 0:
                            current = 0
                            if weakpoint < 5:
                                embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}\n**Weak Point:** {currentweak}/{weak} | {weakpoint}/4"
                            else:
                                embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}"
                            await message.edit(embed = embed,components = dbuttons)
                            await interaction.respond(type = 6)
                            finalkick = interaction.user
                            break
                        if currentweak <= 0:
                            currentweak = 0
                            await interaction.respond(type = 6)
                            if weakpoint == 4:
                                embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}\n**Weak Point:** {currentweak}/{weak} | {weakpoint}/4\n\nWeak point {weakpoint} defeated! Heavy damage is enabled on the boss! Hit the boss with all you got."
                                weakpoint += 1
                                buttons[0][weakb] = Button(label = "Hit Boss")
                                await message.edit(embed = embed, components = dbuttons)
                                currentweak = weak
                                await asyncio.sleep(5)
                                embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}"
                                await message.edit(embed = embed, components = buttons)
                            else:
                                embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}\n**Weak Point:** {currentweak}/{weak} | {weakpoint}/4\n\nWeak point {weakpoint} defeated! Generating next weak point."
                                await message.edit(embed = embed, components = dbuttons)
                                weakpoint += 1
                                currentweak = weak
                                buttons[0][weakb] = Button(label = "Hit Boss")
                                weakb = random.randint(0,3)
                                buttons[0][weakb] = Button(label = "Hit Weak Point!",style = 3)
                                await asyncio.sleep(5)
                                embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}\n**Weak Point:** {currentweak}/{weak} | {weakpoint}/4"
                                await message.edit(embed = embed, components = buttons)
                        else:
                            if weakpoint < 5:
                                embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}\n**Weak Point:** {currentweak}/{weak} | {weakpoint}/4"
                            else:
                                embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}"
                            await message.edit(embed = embed)
                            await interaction.respond(type = 6)
                    except:
                        pass
                pot = len(hitters) * 7 * multiplier
                values = hitters.values()
                total = sum(values)
                description = ""
                for hitter,kicked in hitters.items():
                    if hitter == finalkick:
                        given = int(final + pot * (kicked/total))
                        msg = f"**{hitter.name}** got the final hit! They got **{given} {self.emoji}**\n"
                        await self.add_items(message.guild,hitter,given)
                    else:
                        given = int(pot * (kicked/health))
                        msg = f"**{hitter.name}** got **{given} {self.emoji}**\n"
                        await self.add_items(message.guild,hitter,given)
                
                    description += msg
                embed = discord.Embed(description = description,color = discord.Color.gold())
                await message.reply(embed = embed)

        elif event == "fastclick":
            buttons = [[Button(emoji = self.client.get_emoji(904112302918369301),disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),disabled = True)]]
            selected = random.randint(0,3)
            
            embed = discord.Embed(title = "Think Fast! Let's see your reaction time.",description = f"Once the buttons are opened, click the green one first to claim the {self.item}!",color = discord.Color.gold())
            message = await message.channel.send(embed = embed,components = buttons)
            buttons[0][selected] = Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = False)

            time = random.randint(3,10)
            await asyncio.sleep(time)
            await message.edit(components = buttons)

            def check(i):
                if i.message.id == message.id:
                    return True
                else:
                    return False

            try:
                interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
            except asyncio.TimeoutError:
                buttons[0][selected] = Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = True)
                return await message.edit("The drop timed out. Are yall dead?", components = buttons)
            buttons[0][selected] = Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = True)
            await message.edit(components = buttons)

            amount = random.randint(100,300)
            embed = discord.Embed(description = f"{interaction.user.mention} Claimed **{amount} {self.emoji}**",color = discord.Color.green())
            embed.set_footer(text = f"Use [prefix]{self.item} to see how much {self.item} you have!")
            await self.add_items(message.guild,interaction.user,amount)
            return await interaction.respond(embed = embed,ephemeral = False)
    
    @commands.command(hidden = True,help = "spawn <event> [option] [secondary]")
    @commands.is_owner()
    async def spawn(self,ctx,event,option:int = None,secondary:int = None):
        await self.event_spawn(event,ctx.message,option,secondary)

    @commands.command(help = "gingerbread [user]",description = f"Shows the amount of event items you or another user has.")
    async def gingerbread(self,ctx,user:discord.Member = None):
        user = user or ctx.author
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        data = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(user.id)).child("amount").get() or 0
        team = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(user.id)).child("team").get()
        if team:
            teamname = ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(team)).child("name").get()
            embed = discord.Embed(title = f"{user.name}'s {self.item}s",description = f"`{data}` {self.emoji}\n**Supporting Team:** {teamname} | {team}")
        else:
            embed = discord.Embed(title = f"{user.name}'s {self.item}s",description = f"`{data}` {self.emoji}")
        await ctx.reply(embed = embed)

    @commands.command(aliases = ['gblb'],help = "gingerbreadleaderboard",description = "Who has most event items in the server?")
    async def gingerbreadleaderboard(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child(self.event).child(str(ctx.guild.id)).child("players").get() 
        if log:
            def check(a):
                if "amount" in log[a]:
                    return log[a]["amount"]
                return 0
            users = sorted(log,key = lambda a: check(a),reverse = True)
        else:
            users,log = {},{}


        build = ""
        count = 1
        if len(users) > 0:
            for user in users:
                try:
                    amount = log[user]["amount"]
                    build += f"{count}. <@{user}>: `{amount}` {self.item}s {self.emoji}\n"
                    count += 1
                except:
                    pass
                if count >= 11:
                    break
        else:
            build = "No data to show"
        
        if len(build) == 0:
            build = "No data to show"

        embed = discord.Embed(title = f"Leaderboard for {ctx.guild.name} {self.event} Event",description = build,color = discord.Color.random())
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)

    @commands.command(help = "givegingerbread <amount> <user>",description = "Give event items to other people.")
    async def givegingerbread(self,ctx,amount:float,user:discord.Member):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        amount = int(amount)
        if amount <= 0:
            embed = discord.Embed(description = f"You need to give out a positive amount, don't try to break me.",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        giver = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("amount").get() or 0

        if giver <= amount:
            embed = discord.Embed(description = f"You only have `{giver}`{self.emoji}, how are you planning to give out `{amount}`?",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        giver -= amount
        ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("amount").set(giver)
        receiever = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(user.id)).child("amount").get() or 0
        receiever += amount
        ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(user.id)).child("amount").set(receiever)

        embed = discord.Embed(description = f"{ctx.author.mention}, you gave {user.mention} `{amount}`{self.emoji}.\nYou now have `{giver}`{self.emoji} and they have `{receiever}`{self.emoji}")
        await ctx.reply(embed = embed)
    
    @commands.command(help = "agivegingerbread <amount> <user>",description = "As an admin, give event items to someone. Basically god mode.")
    @commands.has_permissions(administrator= True)
    async def agivegingerbread(self,ctx,amount:float,user:discord.Member):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        amount = int(amount)
        if amount <= 0:
            embed = discord.Embed(description = f"You need to give out a positive amount, don't try to break me.",color = discord.Color.red())
            return await ctx.reply(embed = embed)

        receiever = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(user.id)).child("amount").get() or 0
        receiever += amount
        ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(user.id)).child("amount").set(receiever)

        embed = discord.Embed(description = f"{ctx.author.mention}, you generated and gave {user.mention} `{amount}`{self.emoji}.\nThey have `{receiever}`{self.emoji}")
        await ctx.reply(embed = embed)

    @commands.command(help = "gingerbreadtoggle <enable or disable>",description = "Allow or disable drops in your server.")
    @commands.has_permissions(administrator = True)
    async def gingerbreadtoggle(self,ctx,choice):
        if choice.lower() == 'enable':
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            ref.child(str(ctx.guild.id)).child(self.event).child("enabled").set(True)
            self.active.append(ctx.guild.id)
            embed = discord.Embed(description = f"{self.item} drops are enabled guild wide!",color = discord.Color.green())
            embed.set_footer(text = "Disable drops in a channel with [prefix]dropsdisable")
            return await ctx.reply(embed = embed)
        if choice.lower() == "disable" and ctx.guild.id in self.active:
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            ref.child(str(ctx.guild.id)).child(self.event).child("enabled").set(False)
            self.active.remove(ctx.guild.id)
            embed = discord.Embed(description = f"{self.item} drops are disabled guild wide!",color = discord.Color.green())
            return await ctx.reply(embed = embed)
        elif choice.lower() == "disable":
            embed = discord.Embed(description = f"{self.item} drops are not enabled here!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        
        embed = discord.Embed(description = f"You have 2 choices: `enable` or `disable`. Pick one.",color = discord.Color.red())
        return await ctx.reply(embed = embed)

    @commands.command(help = "dropsdisable [channel]",description = "Disable drops in a channel.")
    @commands.has_permissions(administrator = True)
    async def dropsdisable(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel

        if channel.id in self.disabled.get(ctx.guild.id,[]):
            embed = discord.Embed(description = f"{channel.mention} already was disabled for drops!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        
        disabled = self.disabled.get(ctx.guild.id,[])
        disabled.append(channel.id)
        self.disabled[ctx.guild.id] = disabled

        ref = db.reference("/",app = firebase_admin._apps['settings'])
        channels = ref.child(str(ctx.guild.id)).child(self.event).child("disabled").get() or []
        channels.append(channel.id)
        ref.child(str(ctx.guild.id)).child(self.event).child("disabled").set(channels)

        embed = discord.Embed(description = f"{channel.mention} is now disabled for {self.item} drops!",color = discord.Color.green())
        return await ctx.reply(embed = embed)

    @commands.command(help = "dropsenable [channel]",description = "Removes disable in a channel.")
    @commands.has_permissions(administrator = True)
    async def dropsenable(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel

        if channel.id not in self.disabled.get(ctx.guild.id,[]):
            embed = discord.Embed(description = f"{channel.mention} already was enabled for drops!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        
        disabled = self.disabled.get(ctx.guild.id,[])
        disabled.remove(channel.id)
        self.disabled[ctx.guild.id] = disabled

        ref = db.reference("/",app = firebase_admin._apps['settings'])
        channels = ref.child(str(ctx.guild.id)).child(self.event).child("disabled").get() or []
        channels.remove(channel.id)
        ref.child(str(ctx.guild.id)).child(self.event).child("disabled").set(channels)

        embed = discord.Embed(description = f"{channel.mention} is now enabled for {self.item} drops!",color = discord.Color.green())
        return await ctx.reply(embed = embed)
    
    @commands.command(help = "teamtoggle <enable/disable>",description = "Enable or disable teams.")
    @commands.has_permissions(administrator = True)
    async def teamtoggle(self,ctx,input):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        current = ref.child(str(ctx.guild.id)).child("winter").child("team").get()
        if input.lower() == "enable" and not current:
            ref.child(str(ctx.guild.id)).child("winter").child("team").set(True)
            await ctx.reply("Teams enabled!")
        elif input.lower() == "enable" and current:
            return await ctx.reply("Why are you enabling something that's already enabled?")
        elif input.lower() == "disable" and current:
            ref.child(str(ctx.guild.id)).child("winter").child("team").set(False)
            await ctx.reply("Teams disabled!")
        elif input.lower() == "disable" and not current:
            return await ctx.reply("Why are you disabling something that's already disabled?")
        else:
            await ctx.reply("You got 2 options: `disable` or `enable`.")


    @commands.command(aliases = ['gbtlb'],help = "gingerbreadteamleaderboard",description = "Which team has the most items?")
    @teams_check()
    async def gingerbreadteamleaderboard(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        teams = ref.child(self.event).child(str(ctx.guild.id)).child("team").get()
        if not teams:
            return await ctx.reply("Teams do not exsist here!") 
        teamamounts = {}
        message = await ctx.reply(f"<a:OB_Loading:907101653692456991> Generating team leaderboard...")
        for team,teamdata in teams.items():
            teammembers = teamdata['members']
            total = 0
            for member in teammembers:
                total += ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(member)).child("amount").get() or 0 
            teamamounts[team] = [teamdata['name'],total]
        
        def check(a):
            try:
                return teamamounts[a][1]
            except:
                return 0
        sortedteams = sorted(teamamounts,key = lambda a: check(a),reverse = True)

        build = ""
        count = 1
        for team in sortedteams:
            build += f"**{count}. {teamamounts[team][0]}**\n"
            build += f"{self.replycont} **Team ID:** {team}\n"
            build += f"{self.replyend} **Total:** {teamamounts[team][1]} {self.emoji}\n\n"
            count += 1

            if count >= 6:
                break

        embed = discord.Embed(title = f"Team Leaderboard for {ctx.guild.name} {self.event} Event",description = build,color = discord.Color.random())
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await message.edit("",embed = embed)

    @commands.command(help = "teamcreate <privacy> <name>",description = "Create a team, if team mode is on for your server.",brief = "Make sure to include a team name, and whether your team is public or private.")
    @teams_check()
    async def teamcreate(self,ctx,privacy,*,teamname):
        ref = db.reference("/",app = firebase_admin._apps['elead'])

        persondata = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("team").get()
        if persondata:
            return await ctx.reply("You are already on a team! Leave your current team before joining another one.")

        if privacy.lower() in ['public','private']:
            pass
        else:
            privacy = 'public'
        teamid = int(str(uuid.uuid4().int)[0:11])
        teamdata = {"name":teamname,"members":[ctx.author.id],"privacy":privacy.lower()}
        embed = discord.Embed(title = "Confirming Action",description = f"You are creating a team with the following details:\n\nTeam Name: {teamname}\nTeam Privacy: {privacy}\nTeam Captain: {ctx.author.mention}",color = discord.Color.random())
        message = await ctx.reply(f"{ctx.author.mention}",embed = embed,components = [
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
                await ctx.send("Well you took too long to respond. Try again next time.")
                return await message.edit(components = [[Button(emoji = "✅",style = 3,disabled = True),Button(emoji = "✖",style = 4,disabled = True)]])

            if not interaction.user.id == ctx.author.id:
                embed=discord.Embed(description=f"Only {ctx.author.mention} can use these.", color=discord.Color.red())
                await interaction.respond(embed = embed)
                continue

            if str(interaction.component.emoji) == "✖":
                await interaction.respond(content = "Guess we aren't doing this today",ephemeral  = False)
                return await message.edit(components = [[Button(emoji = "✅",style = 2,disabled = True),Button(emoji = "✖",style = 4,disabled = True)]])
            else:
                break
        await message.edit(components = [[Button(emoji = "✅",style = 3,disabled = True),Button(emoji = "✖",style = 2,disabled = True)]])
        embed = discord.Embed(title = "Team Created!",color = discord.Color.green())
        embed.add_field(name = "Team Information ℹ️",value = f"Team Name: {teamname}\nTeam Privacy: {privacy}\nTeam Captain: {ctx.author.mention}")
        embed.set_footer(text = f"Team ID: {teamid}")
        ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(teamid)).set(teamdata)
        ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("team").set(teamid)
        await interaction.respond(embed = embed,ephemeral = False)
    
    @commands.command(help = "teamjoin <teamid>",description = "Join a team!",brief = "If the team is private, the team owner will get a notification that you would like to join.")
    @teams_check()
    async def teamjoin(self,ctx,teamid:int):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        persondata = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("team").get()
        if persondata:
            return await ctx.reply("You are already on a team! Leave your current team before joining another one.")

        teamdata = ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(teamid)).get()
        if not teamdata:
            return await ctx.reply("That does not look like a valid team id.")
        if len(teamdata['members']) >= 5:
            return await ctx.reply("This team is already at the limit of 5 members! Find another team to join")
        def check(i):
            if i.channel.id == ctx.channel.id and i.author.id == ctx.message.author.id:
                return True
            else:
                return False
        if teamdata['privacy'] == "private":
            status = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("applications").child(str(teamid)).get()
            if status:
                return await ctx.reply("You have already applied to this team! Please wait for their decision.")
            requestid = int(str(uuid.uuid4().int)[0:11])
            embed = discord.Embed(description = f"**{teamdata['name']}** is a private team! Type a quick explanation on why you should be able to join the team.",color = discord.Color.random())
            embed.set_footer(text = "You application, along with your short response, will be sent to the team leader for review.")
            message = await ctx.reply(embed = embed)
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too to respond. Try again when you can type faster.")
            
            requestdata = {"applicant":ctx.author.id,"reason":msg.content,"status":"🟨 Pending"}
            ref.child(self.event).child(str(ctx.guild.id)).child("teamapplications").child(str(teamid)).child(str(requestid)).set(requestdata)
            ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("applications").child(str(teamid)).set(requestid)
            embed = discord.Embed(description = f"Thank you for your application! You can view your application while it is pending with `[prefix]applicationview {requestid}`",color = discord.Color.green())
            await message.reply(embed = embed)

            try:
                host = ctx.guild.get_member(int(teamdata['members'][0]))
                embed = discord.Embed(title = f"You have a new team application in {ctx.guild.name}!",description = f"View the application with `[prefix]applicationview {requestid}`",color = discord.Color.random())
                dm = host.dm_channel
                if dm == None:
                    dm = await host.create_dm()
                await dm.send(embed = embed)
            except:
                pass
        else:
            otherapps = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("applications").get()
            if otherapps:
                for teamid,appid in otherapps.items():
                    ref.child(self.event).child(str(ctx.guild.id)).child("teamapplications").child(str(teamid)).child(str(appid)).delete()
            ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("applications").delete()
            teamdata['members'].append(ctx.author.id)
            ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(teamid)).set(teamdata)
            ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("team").set(teamid)
            embed = discord.Embed(description = f"Success! You have joined {teamdata['name']}, best of luck.",color = discord.Color.green())
            await ctx.reply(embed = embed)
    
    @commands.command(help = "applicationview <applicationid>",description = "View an application.",brief = "You can only view your own application, or as a team owner who has applied to your team.")
    @teams_check()
    async def applicationview(self,ctx,id:int):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        team = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("team").get()
        if team:
            teamdata = ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(team)).get()
            teammembers = teamdata['members']

            if int(teammembers[0]) == ctx.author.id:
                application = ref.child(self.event).child(str(ctx.guild.id)).child("teamapplications").child(str(team)).child(str(id)).get()
                if not application:
                    return await ctx.reply("There is no application for your team with that id!")
                elif not application['status'] == "🟨 Pending":
                    embed = discord.Embed(title = f"Application #{id}",color = discord.Color.green())
                    embed.add_field(name = "Applicant",value = f"<@{application['applicant']}> (`{application['applicant']}`)",inline = False)     
                    embed.add_field(name = "Status",value = application['status'],inline = False)
                    embed.add_field(name = "Application Reason",value = application['reason'])
                    if application['status'] == "🟥 Rejected":
                        embed.add_field(name = "Rejection Reason",value = application['rreason'],inline = False)
                        embed.color = discord.Color.red()
                    await ctx.reply(embed = embed)
                else:
                    embed = discord.Embed(title = f"Application #{id}",color = discord.Color.gold())
                    embed.add_field(name = "Applicant",value = f"<@{application['applicant']}> (`{application['applicant']}`)",inline = False)     
                    embed.add_field(name = "Status",value = application['status'],inline = False)
                    embed.add_field(name = "Application Reason",value = application['reason'])
                    embed.set_footer(text = "Accept or deny this application with the buttons below!")
                    message = await ctx.reply(embed = embed, components = [[Button(emoji = "✅",style = 3),Button(emoji = "✖",style = 4)]])

                    def check(i):
                        if i.message.id == message.id:
                            return True
                        else:
                            return False

                    while True:
                        try:
                            interaction = await self.client.wait_for("button_click", timeout = 60.0,check = check)
                        except asyncio.TimeoutError:
                            return await message.edit(components = [[Button(emoji = "✅",style = 3,disabled = True),Button(emoji = "✖",style = 4,disabled = True)]])

                        if not interaction.user.id == ctx.author.id:
                            embed=discord.Embed(description=f"Only {ctx.author.mention} can use these.", color=discord.Color.red())
                            await interaction.respond(embed = embed)
                            continue

                        if str(interaction.component.emoji) == "✖":
                            embed = discord.Embed(description = "Enter the reason for the rejection.",color = discord.Color.red())
                            await interaction.respond(embed = embed,ephemeral = False)
                            def check(i):
                                if i.channel.id == ctx.channel.id and i.author.id == ctx.message.author.id:
                                    return True
                                else:
                                    return False
                            try:
                                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
                            except asyncio.TimeoutError:
                                return await ctx.send("You took too to respond. Try again when you can type faster.")
                            embed = discord.Embed(title = f"Rejected Application #{id}",description = f"You rejected <@{application['applicant']}> from {teamdata['name']}.",color = discord.Color.red())
                            await msg.reply(embed = embed)
                            await message.edit(components = [[Button(emoji = "✅",style = 2,disabled = True),Button(emoji = "✖",style = 4,disabled = True)]])
                            application['status'] = "🟥 Rejected"
                            application['rreason'] = msg.content
                            ref.child(self.event).child(str(ctx.guild.id)).child("teamapplications").child(str(team)).child(str(id)).set(application)
                            ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(application['applicant'])).child("applications").child(str(team)).delete()
                            try:
                                host = ctx.guild.get_member(int(application['applicant']))
                                embed = discord.Embed(description = f"You were rejected from {teamdata['name']}",color = discord.Color.red())
                                embed.add_field(name = "Rejection Reason",value = msg.content)
                                dm = host.dm_channel
                                if dm == None:
                                    dm = await host.create_dm()
                                await dm.send(embed = embed)
                            except:
                                pass
                        elif str(interaction.component.emoji) == "✅":
                            embed = discord.Embed(title = f"Accepted Application #{id}",description = f"You accepted <@{application['applicant']}> to {teamdata['name']}.",color = discord.Color.green())
                            await interaction.respond(embed = embed,ephemeral  = False)
                            await message.edit(components = [[Button(emoji = "✅",style = 3,disabled = True),Button(emoji = "✖",style = 2,disabled = True)]])
                            application['status'] = "🟩 Accepted"
                            ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(application['applicant'])).child("applications").child(str(team)).delete()
                            ref.child(self.event).child(str(ctx.guild.id)).child("teamapplications").child(str(team)).child(str(id)).set(application)
                            otherapps = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(application['applicant'])).child("applications").get()
                            if otherapps:
                                for teamid,appid in otherapps.items():
                                    ref.child(self.event).child(str(ctx.guild.id)).child("teamapplications").child(str(teamid)).child(str(appid)).delete()
                            ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(application['applicant'])).child("applications").delete()
                            teamdata['members'].append(application['applicant'])
                            ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(team)).set(teamdata)
                            ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(application['applicant'])).child("team").set(int(team))
                            try:
                                host = ctx.guild.get_member(int(application['applicant']))
                                embed = discord.Embed(description = f"You were accepted into {teamdata['name']}",color = discord.Color.green())
                                dm = host.dm_channel
                                if dm == None:
                                    dm = await host.create_dm()
                                await dm.send(embed = embed)
                            except:
                                pass
            else:
                return await ctx.reply("Only your team leader can view applications for your team!")
        else:
            apps = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("applications").get()
            if not apps:
                return await ctx.reply("You don't have any applications!")
            application = None
            for teamid,appid in apps.items():
                if appid == id:
                    application = ref.child(self.event).child(str(ctx.guild.id)).child("teamapplications").child(str(teamid)).child(str(appid)).get()
            if application:
                embed = discord.Embed(title = f"Application #{id}",color = discord.Color.green())
                embed.add_field(name = "Applicant",value = f"<@{application['applicant']}> (`{application['applicant']}`)",inline = False)     
                embed.add_field(name = "Status",value = application['status'],inline = False)
                embed.add_field(name = "Application Reason",value = application['reason'])
                if application['status'] == "🟨 Pending":
                    embed.color = discord.Color.gold()
                elif application['status'] == "🟥 Rejected":
                    embed.color = discord.Color.red()
                    embed.add_field(name = "Rejection Reason",value = application['rreason'],inline = False)
                elif application['status'] == "🟩 Accepted":
                    embed.color = discord.Color.green()
                await ctx.reply(embed = embed)
            else:
                return await ctx.reply("That isn't your application!")

    @commands.command(help = "teamlist",description = "List the teams in the server.")
    @teams_check()
    async def teamlist(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        teams = ref.child(self.event).child(str(ctx.guild.id)).child("team").get()
        if not teams:
            return await ctx.reply("There are no teams here to list!")
        
        embed = discord.Embed(title = f"Team List for {ctx.guild.name}",color = discord.Color.random())
        description = "`Team ID | Team Name`\n"
        for teamid,teamdata in teams.items():
            description += f"{teamid} | {teamdata['name']}\n"
        embed.description = description
        await ctx.reply(embed = embed)
    
    @commands.command(help = "applicationlist",description = "List your applications, or applications pending on your team.")
    @teams_check()
    async def applicationlist(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        team = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("team").get()
        if team:
            teamdata = ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(team)).get()
            teammembers = teamdata['members']

            if int(teammembers[0]) == ctx.author.id:
                applications = ref.child(self.event).child(str(ctx.guild.id)).child("teamapplications").child(str(team)).get()
                if not applications:
                    return await ctx.reply("There are no applications for your team!")
                else:
                    embed = discord.Embed(title = "Your Team Aplications",color = discord.Color.random())
                    pages = math.ceil(len(applications)/5)
                    index = 1
                    start = 0
                    end = min(5,len(applications))
                    keys = list(applications.keys())
                    description = ""
                    for application in keys[start:end]:
                        description += f"{self.replybegin} Application #{application}\n"
                        description += f"{self.replyline} Status: {applications[application]['status']}\n"
                        description += f"{self.replyend} Applicant: <@{applications[application]['applicant']}> `{applications[application]['applicant']}`\n"
                    embed.description = description
                    embed.set_footer(text = f"Showing Page {index} of {pages}")
                    if pages > 1:
                        message = await ctx.reply(embed = embed,components = [[Button(label = "Back",disabled = True),Button(label = "Next")]])
                    else:
                        return await ctx.reply(embed = embed,components = [[Button(label = "Back",disabled = True),Button(label = "Next",disabled = True)]])
                    
                    def check(i):
                        if i.message.id == message.id:
                            if (i.component.label.startswith("Next") or i.component.label.startswith("Back")):
                                return True
                            else:
                                return False
                        else:
                            return False

                    while True:
                        description = ""
                        try:
                            interaction = await self.client.wait_for("button_click", timeout = 120.0,check = check)
                        except asyncio.TimeoutError:
                            try:
                                await message.edit("Message no longer Active",components = [
                                    [
                                        Button(label = "Back",disabled = True),
                                        Button(label = "Next",disabled = True)
                                    ]
                                ])
                                break
                            except:
                                break
                        
                        if interaction.component.label == "Next":
                            index += 1
                        else:
                            index -= 1
                        start = (index-1) * 5
                        end = min(len(applications),(index-1)*5 + 5)
                        for application in keys[start:end]:
                            description += f"{self.replybegin} Application #{application}\n"
                            description += f"{self.replyline} Status: {applications[application]['status']}\n"
                            description += f"{self.replyend} Applicant: <@{applications[application]['applicant']}> `{applications[application]['applicant']}`\n"
                        embed.description = description
                        embed.set_footer(text = f"Showing Page {index} of {pages}")
                        if index == pages:
                            await message.edit(embed = embed, components = [[Button(label = "Back"),Button(label = "Next",disabled = True)]])
                        elif index == 1:
                            await message.edit(embed = embed, components = [[Button(label = "Back",disabled = True),Button(label = "Next")]])
                        else:
                            await message.edit(embed = embed, components = [[Button(label = "Back"),Button(label = "Next")]])
                        await interaction.respond(type = 6)
            else:
                return await ctx.reply("You aren't the team leader!")
        else:
            await ctx.reply("You aren't on a team! What applications do you even need to view...")

    @commands.command(description = "Kick a team member out of your team.",help = "teamkick <member>",brief = "Looks like someone is slacking.")
    @teams_check()
    async def teamkick(self,ctx,member:discord.Member):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        team = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(ctx.author.id)).child("team").get()
        if team:
            teamdata = ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(team)).get()
            teammembers = teamdata['members']

            if int(teammembers[0]) == ctx.author.id:
                memberteam = ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(member.id)).child("team").get()
                if not memberteam:
                    return await ctx.reply("This person isn't even in a team lmao.")
                if int(memberteam) == int(team):
                    ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(member.id)).child("team").delete()
                    teammembers.remove(member.id)
                    ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(team)).child("members").set(teammembers)
                    await ctx.reply(embed = discord.Embed(description = f"Successfully kicked {member.mention} out of your team.",color = discord.Color.green()))
                    try:
                        embed = discord.Embed(description = f"You were kicked from {teamdata['name']}",color = discord.Color.red())
                        dm = member.dm_channel
                        if dm == None:
                            dm = await member.create_dm()
                        await dm.send(embed = embed)
                    except:
                        pass
                else:
                    return await ctx.reply("This person isn't in your team...")
            else:
                return await ctx.reply("You aren't the team leader...")
    
    @commands.command(description = "View the information for a team.",help = "teaminfo <teamid>")
    @teams_check()
    async def teaminfo(self,ctx,teamid:int):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        teamdata = ref.child(self.event).child(str(ctx.guild.id)).child("team").child(str(teamid)).get()
        if not teamdata:
            return await ctx.reply("You sure that's a valid team id?")
        
        embed = discord.Embed(title = f"Team Info for {teamdata['name']}",description = f"ID: {teamid}",color = discord.Color.random())
        embed.add_field(name = "Team Members",value = "\n ".join([f"{self.replycont} <@" + str(i) + ">" for i in teamdata['members'] if i != teamdata['members'][-1]]) + f"\n{self.replyend} <@{teamdata['members'][-1]}>",inline = False)
        embed.add_field(name = "Team Privacy",value = teamdata['privacy'],inline = False)
        total = 0
        for member in teamdata['members']:
            total += ref.child(self.event).child(str(ctx.guild.id)).child("players").child(str(member)).child("amount").get() or 0 
        embed.add_field(name = "Total Items",value = f"`{total}` {self.emoji}",inline = False)
        await ctx.reply(embed = embed)



def setup(client):
    client.add_cog(Winter(client))

    