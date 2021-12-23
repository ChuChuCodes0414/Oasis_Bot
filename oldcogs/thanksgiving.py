import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button
import datetime
import math
import firebase_admin
from firebase_admin import db
import random
import asyncio

class Thanksgiving(commands.Cog):
    '''
        Thanksgiving drops for thanksgiving! Use help command for more info.
    '''
    def __init__(self,client):
        self.client = client
        self.turkey = "<:oasisturkey:907430766592524348>"
        self.choices = ["button","phrase","unscramble","boss","word","fastclick"]
        self.titles = ["Quick, turkeys are being dropped!","Someone dropped some turkeys!","You found turkeys at a farm!","Oh, turkeys!"]
        self.phrasestext = [
            
        ]
        self.phrases = [

        ]
        self.wordstext = [
            
        ]
        self.words = [
            
        ]
        self.active = [870125583886065674]
        self.disabled = {}
        self.slowmode = []
    
    @commands.Cog.listener()
    async def on_ready(self):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        data = ref.get()

        for guild,guilddata in data.items():
            thanksgiving = guilddata.get("thanksgiving",None)
            if thanksgiving:
                if thanksgiving.get("enabled",False):
                    self.active.append(int(guild))
                disabled = thanksgiving.get("disabled",[])
                build = []
                for channel in disabled:
                    build.append(int(channel))
                if len(build) > 0:
                    self.disabled[int(guild)] = build

        print('Thanksgiving Cog Loaded, and channels cached.')
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def thanksgivingcache(self,ctx):
        await ctx.send(self.active)
        await ctx.send(self.disabled)
        await ctx.send(f"{len(self.phrases)} | {len(self.phrasestext)}")
        await ctx.send(f"{len(self.words)} | {len(self.wordstext)}")

    async def add_turkey(self,guild,user,amount):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        data = ref.child("thanksgiving").child(str(guild.id)).child(str(user.id)).child("amount").get() or 0
        ref.child("thanksgiving").child(str(guild.id)).child(str(user.id)).child("amount").set(data + amount)
        return True
        
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.guild.id not in self.active or message.author.bot or message.channel.id in self.disabled.get(message.guild.id,[]):
            return

        chance = random.randint(1,100)
        if not chance <= 50:
            return

        #event = self.choices[random.randint(0,len(self.choices)-1)]
        event = "boss"
        if event == "button":
            title = self.titles[random.randint(0,len(self.titles))-1]
            embed = discord.Embed(title = title,description = "Be the first to click the button to claim!",color = discord.Color.gold())
            message = await message.channel.send(embed = embed,components = [Button(label = "Claim Turkeys",style = 3)])

            def check(i):
                if i.message.id == message.id:
                    return True
                else:
                    return False

            try:
                interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
            except asyncio.TimeoutError:
                return await message.edit("The drop timed out. Are yall dead?",embed = embed, components = [Button(label = "Claim Turkeys",style = 3,disabled = True)])
                
            await message.edit("Drop Claimed!",embed = embed, components = [Button(label = "Claim Turkeys",style = 2,disabled = True)])

            amount = random.randint(50,100)
            embed = discord.Embed(description = f"{interaction.user.mention} Claimed **{amount} {self.turkey}**",color = discord.Color.green())
            embed.set_footer(text = "Use [prefix]turkey to see how much turkey you have!")
            await self.add_turkey(message.guild,interaction.user,amount)
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
                    message = await self.client.wait_for("message",timeout = 30.0,check = check)
                except asyncio.TimeoutError:
                    return await message.edit("The drop timed out. Are yall dead?")

                if message.content == phrasetext:
                    await message.reply("You cheating mf, nice try.")
                else:
                    break
            
            amount = random.randint(300,500)
            embed = discord.Embed(description = f"{message.author.mention} Claimed **{amount} {self.turkey}**",color = discord.Color.green())
            embed.set_footer(text = "Use [prefix]turkey to see how much turkey you have!")
            await self.add_turkey(message.guild,message.author,amount)
            await message.reply(embed = embed)
        elif event == "word":
            title = self.titles[random.randint(0,len(self.titles))-1]
            num = random.randint(0,len(self.words)-1)
            word = self.words[num]
            wordtext = self.wordstext[num]

            embed = discord.Embed(title = title,description = f"Type the word\n\n{wordtext}\n\nto pick it up!",color = discord.Color.gold())
            message = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == message.channel.id and i.content == wordtext:
                    return True
                if i.channel.id == message.channel.id and i.content == word:
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
            embed = discord.Embed(description = f"{message.author.mention} Claimed **{amount} {self.turkey}**",color = discord.Color.green())
            embed.set_footer(text = "Use [prefix]turkey to see how much turkey you have!")
            await self.add_turkey(message.guild,message.author,amount)
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
            embed = discord.Embed(description = f"{message.author.mention} Claimed **{amount} {self.turkey}**",color = discord.Color.green())
            embed.set_footer(text = "Use [prefix]turkey to see how much turkey you have!")
            await self.add_turkey(message.guild,message.author,amount)
            await message.reply(embed = embed)
        elif event == "boss":
            mega = random.randint(0,100)
            if mega >= 100:
                type = random.randint(0,1000)
                if type <= 20:
                    type = "legendary"
                    title = "🟨 Lengendary BOSS!"
                    description = "Jeez this thing has a lot of health! Take it down to grab it's turkey!"
                    footer = "Kill the boss to receieve 4000 turkeys!!! This boss has a 2% Chance of Spawning."
                    multiplier = 60
                    final = 4000
                    health = 2000
                elif type <= 110:
                    type = "epic"
                    title = "🟪 Epic Boss!"
                    description = "Nice, it has turkeys. Hit the button to grab it's turkeys!"
                    footer = "Kill the boss to receieve 2,000 turkeys! This boss has a 9% Chance of Spawning."
                    multiplier = 12
                    final = 2000
                    health = 400
                elif type <= 310:
                    type = "rare"
                    title = "🟦 Rare Boss!"
                    description = "Not quite the rarest boss, but it still has turkeys! Let's go for it."
                    footer = "Kill the boss to receieve 500 turkeys! This boss has a 20% Chance of Spawning."
                    multiplier = 3
                    final = 500
                    health = 200
                elif type <= 610:
                    type = "uncommon"
                    title = "🟩 Uncommon Boss"
                    description = "Not quite the rarest boss, but it still has turkey! Let's go for it."
                    footer = "Kill the boss to receieve 100 turkey! This boss has a 30% Chance of Spawning."
                    multiplier = 1
                    final = 100
                    health = 150
                else:
                    type = "common"
                    title = "⬜ Common Boss"
                    description = "Might as well take a shot at this, it's free turkey." 
                    footer = "Kill the boss to receieve 50 turkey! This boss has a 39% Chance of spawning"
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
                        msg = f"**{hitter.name}** got the final hit! They got **{given} {self.turkey}**\n"
                        await self.add_turkey(message.guild,hitter,given)
                    else:
                        given = int(pot * (kicked/health))
                        msg = f"**{hitter.name}** got **{given} {self.turkey}**\n"
                        await self.add_turkey(message.guild,hitter,given)
                
                    description += msg
                embed = discord.Embed(description = description,color = discord.Color.gold())
                await message.reply(embed = embed)
            else:
                type = random.randint(1,100)
                if type == 1:
                    type = "gold"
                    title = f"{self.client.get_emoji(908552154254573638)} Gold MEGABOSS!"
                    description = "The boss will not stick around long! Target the weak points!"
                    footer = "Kill the boss to receieve 30000 turkeys!!! This boss has a 1% Chance of Spawning."
                    multiplier = 280
                    final = 30000
                    weak = 1000
                    health = 10000
                elif type <= 21:
                    type = "silver"
                    title = f"{self.client.get_emoji(908552154166468609)} Silver MEGABOSS!"
                    description = "The boss will not stick around long! Target the weak points!"
                    footer = "Kill the boss to receieve 10000 turkeys!!! This boss has a 20% Chance of Spawning."
                    multiplier = 140
                    final = 10000
                    weak = 700
                    health = 5000
                else:
                    type = "bronze"
                    title = f"{self.client.get_emoji(908552154275545138)} Bronze MEGABOSS!"
                    description = "The boss will not stick around long! Target the weak points!"
                    footer = "Kill the boss to receieve 5000 turkeys!!! This boss has a 79% Chance of Spawning."
                    multiplier = 70
                    weak = 400
                    final = 5000
                    health = 1000
                
                embed = discord.Embed(title = title,description = description,color = discord.Color.from_rgb(255,0,0))
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
                        interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
                    except asyncio.TimeoutError:
                        if weakpoint < 5:
                            dbuttons[0][weakb] = Button(label = "Hit Weak Point!",style = 3,disabled = True)
                        return await message.edit("The boss ran. Are yall dead?",embed = embed, components = dbuttons)

                    if weakpoint < 5:
                        if interaction.component.label == "Hit Weak Point!":
                            kick = random.randint(20,50)
                            currentweak -= kick
                        else:
                            kick = random.randint(1,5)
                            current -= kick
                    else:
                        kick = random.randint(20,50)
                        current -= kick
                    
                    if current <= 0:
                        current = 0
                        if weakpoint < 5:
                            embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}\n**Weak Point:** {currentweak}/{weak} | {weakpoint}/4"
                        else:
                            embed.description = description + f"\n\n**Boss Health 😡:** {current}/{health}"
                        await message.edit(embed = embed,components = dbuttons)
                        await interaction.respond(type = 6)
                        hitters[interaction.user] = hitters.get(interaction.user,0) + kick
                        finalkick = interaction.user
                        break
                    if currentweak <= 0:
                        currentweak = 0
                        await interaction.respond(type = 6)
                        hitters[interaction.user] = hitters.get(interaction.user,0) + kick
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
                        hitters[interaction.user] = hitters.get(interaction.user,0) + kick
                pot = len(hitters) * 0.01 * multiplier
                values = hitters.values()
                total = sum(values)
                description = ""
                for hitter,kicked in hitters.items():
                    if hitter == finalkick:
                        given = int(final + pot * (kicked/total))
                        msg = f"**{hitter.name}** got the final hit! They got **{given} {self.turkey}**\n"
                        await self.add_turkey(message.guild,hitter,given)
                    else:
                        given = int(pot * (kicked/health))
                        msg = f"**{hitter.name}** got **{given} {self.turkey}**\n"
                        await self.add_turkey(message.guild,hitter,given)
                
                    description += msg
                embed = discord.Embed(description = description,color = discord.Color.gold())
                await message.reply(embed = embed)



        elif event == "fastclick":
            buttons = [[Button(emoji = self.client.get_emoji(904112302918369301),disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),disabled = True)]]
            selected = random.randint(0,3)
            
            embed = discord.Embed(title = "Think Fast! Let's see your reaction time.",description = "Once the buttons are opened, click the green one first to claim the turkey!",color = discord.Color.gold())
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
            embed = discord.Embed(description = f"{interaction.user.mention} Claimed **{amount} {self.turkey}**",color = discord.Color.green())
            embed.set_footer(text = "Use [prefix]turkey to see how much turkey you have!")
            await self.add_turkey(message.guild,interaction.user,amount)
            return await interaction.respond(embed = embed,ephemeral = False)
            





    @commands.command(help = "turkey [user]",description = "Shows the amount of turkeys you or another user has.")
    async def turkey(self,ctx,user:discord.Member = None):
        user = user or ctx.author
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        data = ref.child("thanksgiving").child(str(ctx.guild.id)).child(str(user.id)).child("amount").get() or 0

        embed = discord.Embed(title = f"{user.name}'s turkeys",description = f"`{data}` {self.turkey}")
        await ctx.reply(embed = embed)

    @commands.command(help = "turkeyleaderboard",description = "Who has most turkeys in the server?")
    async def turkeyleaderboard(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child("thanksgiving").child(str(ctx.guild.id)).get() 
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
        for user in users:
            amount = log[user]
            build += f"{count}. <@{user}>: `{amount}` turkeys {self.turkey}\n"
            count += 1

            if count >= 11:
                break

        embed = discord.Embed(title = f"Leaderboard for {ctx.guild.name} Thanksgiving Event",description = build,color = discord.Color.random())
        embed.timestamp = datetime.datetime.utcnow()

        await ctx.reply(embed = embed)

    @commands.command(help = "giveturkey <amount> <user>",description = "Give turkey to other people.")
    async def giveturkey(self,ctx,amount:float,user:discord.Member):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        amount = int(amount)
        if amount <= 0:
            embed = discord.Embed(description = f"You need to give out a positive amount, don't try to break me.",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        giver = ref.child("thanksgiving").child(str(ctx.guild.id)).child(str(ctx.author.id)).child("amount").get() or 0

        if giver <= amount:
            embed = discord.Embed(description = f"You only have `{giver}`{self.turkey}, how are you planning to give out `{amount}`?",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        giver -= amount
        ref.child("thanksgiving").child(str(ctx.guild.id)).child(str(ctx.author.id)).child("amount").set(giver)
        receiever = ref.child("thanksgiving").child(str(ctx.guild.id)).child(str(user.id)).child("amount").get() or 0
        receiever += amount
        ref.child("thanksgiving").child(str(ctx.guild.id)).child(str(user.id)).child("amount").set(receiever)

        embed = discord.Embed(description = f"{ctx.author.mention}, you gave {user.mention} `{amount}`{self.turkey}.\nYou now have `{giver}`{self.turkey} and they have `{receiever}`{self.turkey}")
        await ctx.reply(embed = embed)
    
    @commands.command(help = "agiveturkey <amount> <user>",description = "As an admin, give turkey to someone. Basically god mode.")
    @commands.has_permissions(administrator= True)
    async def agiveturkey(self,ctx,amount:float,user:discord.Member):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        amount = int(amount)
        if amount <= 0:
            embed = discord.Embed(description = f"You need to give out a positive amount, don't try to break me.",color = discord.Color.red())
            return await ctx.reply(embed = embed)

        receiever = ref.child("thanksgiving").child(str(ctx.guild.id)).child(str(user.id)).child("amount").get() or 0
        receiever += amount
        ref.child("thanksgiving").child(str(ctx.guild.id)).child(str(user.id)).child("amount").set(receiever)

        embed = discord.Embed(description = f"{ctx.author.mention}, you generated and gave {user.mention} `{amount}`{self.turkey}.\nThey have `{receiever}`{self.turkey}")
        await ctx.reply(embed = embed)

    @commands.command(help = "turkeytoggle <enable or disable>",description = "Allow or disable drops in your server.")
    @commands.has_permissions(administrator = True)
    async def turkeytoggle(self,ctx,choice):
        if choice.lower() == 'enable':
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            ref.child(str(ctx.guild.id)).child("thanksgiving").child("enabled").set(True)
            self.active.append(ctx.guild.id)
            embed = discord.Embed(description = f"Turkey drops are enabled guild wide!",color = discord.Color.green())
            embed.set_footer(text = "Disable drops in a channel with [prefix]dropsdisable")
            return await ctx.reply(embed = embed)
        if choice.lower() == "disable" and ctx.guild.id in self.active:
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            ref.child(str(ctx.guild.id)).child("thanksgiving").child("enabled").set(False)
            self.active.remove(ctx.guild.id)
            embed = discord.Embed(description = f"Turkey drops are disabled guild wide!",color = discord.Color.green())
            return await ctx.reply(embed = embed)
        elif choice.lower() == "disable":
            embed = discord.Embed(description = f"Turkey drops are not enabled here!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        
        embed = discord.Embed(description = f"You have 2 choices: `enable` or `disable`. Pick one.",color = discord.Color.red())
        return await ctx.reply(embed = embed)

    @commands.command(help = "turkeydisable [channel]",description = "Disable drops in a channel.")
    @commands.has_permissions(administrator = True)
    async def turkeydisable(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel

        if channel.id in self.disabled.get(ctx.guild.id,[]):
            embed = discord.Embed(description = f"{channel.mention} already was disabled for drops!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        
        disabled = self.disabled.get(ctx.guild.id,[])
        disabled.append(channel.id)
        self.disabled[ctx.guild.id] = disabled

        ref = db.reference("/",app = firebase_admin._apps['settings'])
        channels = ref.child(str(ctx.guild.id)).child("thanksgiving").child("disabled").get() or []
        channels.append(channel.id)
        ref.child(str(ctx.guild.id)).child("thanksgiving").child("disabled").set(channels)

        embed = discord.Embed(description = f"{channel.mention} is now disabled for turkey drops!",color = discord.Color.green())
        return await ctx.reply(embed = embed)

    @commands.command(help = "turkeyenable [channel]",description = "Removes disable in a channel.")
    @commands.has_permissions(administrator = True)
    async def turkeyenable(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel

        if channel.id not in self.disabled.get(ctx.guild.id,[]):
            embed = discord.Embed(description = f"{channel.mention} already was enabled for drops!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        
        disabled = self.disabled.get(ctx.guild.id,[])
        disabled.remove(channel.id)
        self.disabled[ctx.guild.id] = disabled

        ref = db.reference("/",app = firebase_admin._apps['settings'])
        channels = ref.child(str(ctx.guild.id)).child("thanksgiving").child("disabled").get() or []
        channels.remove(channel.id)
        ref.child(str(ctx.guild.id)).child("thanksgiving").child("disabled").set(channels)

        embed = discord.Embed(description = f"{channel.mention} is now enabled for turkey drops!",color = discord.Color.green())
        return await ctx.reply(embed = embed)

    @commands.command(help = "teamcreate <team name>",description = "Create a team, if team mode is on for your server.")
    async def teamcreate(self,ctx,*,teamname):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        if ref.child(str(ctx.guild.id)).child("thanksgiving").child("team").get() or False:
            return await ctx.reply("Teams are not enabled here!")


def setup(client):
    client.add_cog(Thanksgiving(client))

    