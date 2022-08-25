import discord
from discord.ext import commands, menus
from discord import Reaction, app_commands, ui
from itertools import starmap, chain
import firebase_admin
from firebase_admin import db
import datetime
import asyncio
import random
import requests
import ast
import html
import cv2
import numpy as np
import textwrap
from typing import Literal
import uuid

class DropsGame(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.short = "🎉 | Drops"
        self.eventtypes = ["button","reaction","sentence","math","trivia","boss"]
        self.settings = {}
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        all = ref.get()
        for guild,data in all.items():
            self.settings[guild] = data.get("drops",{})
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.dump_channel = self.client.get_channel(1005843173353992234)
        print('Drops Cog Loaded.')
    
    @commands.Cog.listener()
    async def on_message(self,message): 
        if message.author.bot or not message.guild or not self.settings.get(str(message.guild.id),{}).get("active",False) or not message.channel.id in self.settings.get(str(message.guild.id),{}).get("channels",[]):
            return
        await self.spawn_event(message,"boss")
    
    async def process_sentence(self,sentence):
        wrapped_text = textwrap.wrap(sentence, width=35)
        height, width = len(wrapped_text) * 32 + 50, 630
        transparent_img = np.zeros((height, width, 4), dtype=np.uint8)
        x,y= 20,50
        for i, line in enumerate(wrapped_text):
            textsize = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            cv2.putText(transparent_img , line, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                        1, 
                        (255,0,0), 
                        2, 
                        lineType = cv2.LINE_AA)
            gap = textsize[1] + 10
            y += gap
        cv2.imwrite("filename.jpg", transparent_img)
        file = discord.File("filename.jpg",filename = "quote.jpg")
        message = await self.dump_channel.send(file = file)
        link = message.attachments[0]
        return link

    async def spawn_event(self,message,type:str = None):
        type = type or self.eventtypes[random.randint(0,len(self.eventtypes)-1)]
        
        if type == "button":
            embed = discord.Embed(title = f"Event Spawn!",description = "Be the first to click the button to claim the prize.",color = discord.Color.random())
            view = ButtonPressView()
            event = await message.channel.send(embed = embed,view = view)
            view.message = event
            response = await view.wait()
            if response:
                return await event.edit(content = "This drop has timed out!")
            view.children[0].disabled = True
            await event.edit(content = "Drop claimed!",view = view)
            amount = random.randint(50,100)
            balance = await self.process_amount(view.value,amount)
            embed = discord.Embed(description = f"**{view.value}** has claimed **{amount}** {self.settings[str(message.guild.id)]['emoji']}!\nTheir total balance is **{balance}** {self.settings[str(message.guild.id)]['emoji']}",color = discord.Color.green())
            await event.reply(embed = embed)
        elif type == "reaction":
            embed = discord.Embed(title = f"Event Spawn!",description = "When the buttons unlock, be the first to press the right one!",color = discord.Color.random())
            view = ReactionView()
            event = await message.channel.send(embed = embed, view = view)
            view.message = event
            await asyncio.sleep(random.randint(4,10))
            button = random.randint(0,4)
            view.children[button].disabled = False
            view.children[button].style = discord.ButtonStyle.green
            view.children[button].emoji = "<:greenbuttonnew:1005840064590401616>"
            await event.edit(view = view)
            response = await view.wait()
            if response:
                return await event.edit(content = "This drop has timed out!")
            view.children[button].disabled = True
            await event.edit(view = view)
            amount = random.randint(75,125)
            balance = await self.process_amount(view.value,amount)
            embed = discord.Embed(description = f"**{view.value}** has claimed **{amount}** {self.settings[str(message.guild.id)]['emoji']}!\nTheir total balance is **{balance}** {self.settings[str(message.guild.id)]['emoji']}",color = discord.Color.green())
            await event.reply(embed = embed)
        elif type == "sentence":
            response = requests.get("https://zenquotes.io/api/random/")
            response = response.content
            response = response.decode("UTF-8")
            response = ast.literal_eval(response)
            phrase = html.unescape(response[0]["q"])
            author = response[0]["a"]
            whiteblankimage = 255 * np.ones(shape=[512, 512, 3], dtype=np.uint8)
            cv2.putText(whiteblankimage, text='Python with OpenCV', org=(100,200),
                        fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0,0,0),
                        thickness=2, lineType=cv2.LINE_AA)
            embed = discord.Embed(title = f"Event Spawn!",description = f"Type the sentence to pick it up!",color = discord.Color.random())
            embed.set_image(url = await self.process_sentence(phrase))
            embed.set_footer(text = f"Quote From {author}")
            event = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == event.channel.id and i.content.lower() == phrase.lower():
                    return True
                else:
                    return False

            try:
                message = await self.client.wait_for("message",timeout = 45.0,check = check)
            except asyncio.TimeoutError:
                return await event.edit(content = "This drop has timed out!")
            
            amount = random.randint(125,175)
            balance = await self.process_amount(message.author,amount)
            embed = discord.Embed(description = f"**{message.author}** has claimed **{amount}** {self.settings[str(message.guild.id)]['emoji']}!\nTheir total balance is **{balance}** {self.settings[str(message.guild.id)]['emoji']}",color = discord.Color.green())
            await message.reply(embed = embed)
        elif type == "math":
            difficulty = random.randint(1,3)
            type2 = random.randint(0,3)
            if difficulty == 1:
                num1,num2 = random.randint(0,10),random.randint(0,10)
            elif difficulty == 2:
                num1,num2 = random.randint(10,100),random.randint(10,100)
            elif difficulty == 3:
                num1,num2 = random.randint(100,1000),random.randint(100,1000)
            
            if type2 == 0:
                result = num1 + num2
                display = f"{num1} + {num2} = ?"
            elif type2 == 1:
                result = num1 - num2
                display = f"{num1} - {num2} = ?"
            elif type2 == 2:
                result = num1 * num2
                display = f"{num1} x {num2} = ?"
            elif type2 == 3:
                if num1 >= num2:
                    result = num1 // num2
                    display = f"{num1} / {num2} = ?\nDrop the decimals and answer with an integer."
                else:
                    result = num2 // num1
                    display = f"{num2} / {num1} = ?\nDrop the decimals and answer with an integer."
            embed = discord.Embed(title = f"Event Spawn!",description = f"Solve this problem to pick it up!\n\n{display}",color = discord.Color.random())
            event = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == event.channel.id and i.content.lower() == str(result):
                    return True
                else:
                    return False  

            try:
                message = await self.client.wait_for("message",timeout = 45.0,check = check)
            except asyncio.TimeoutError:
                return await event.edit(content = "This drop has timed out!")

            amount = random.randint(50*difficulty,75*difficulty)
            balance = await self.process_amount(message.author,amount)
            embed = discord.Embed(description = f"**{message.author}** has claimed **{amount}** {self.settings[str(message.guild.id)]['emoji']}!\nTheir total balance is **{balance}** {self.settings[str(message.guild.id)]['emoji']}",color = discord.Color.green())
            await message.reply(embed = embed)
        elif type == "trivia":
            type2 = random.randint(1,3)
            if type2 == 1:
                response = requests.get("https://opentdb.com/api.php?amount=1&difficulty=easy")
            elif type2 == 2:
                response = requests.get("https://opentdb.com/api.php?amount=1&difficulty=medium")
            elif type2 == 3:
                response = requests.get("https://opentdb.com/api.php?amount=1&difficulty=hard")
            
            response = response.content
            response = response.decode("utf-8")
            response = ast.literal_eval(response)
            if response["response_code"] == 0:
                category = response["results"][0]["category"]
                mcotf = response["results"][0]["type"]
                difficulty = response["results"][0]["difficulty"]
                question = html.unescape(response["results"][0]["question"])
                correct = html.unescape(response["results"][0]["correct_answer"])
                incorrect = response["results"][0]["incorrect_answers"]
                if mcotf == "boolean":
                    embed = discord.Embed(title = "It's Trivia Time!",description = f"Answer the question correctly to win!",color = discord.Color.random())
                    embed.add_field(name = "Category",value = category)
                    embed.add_field(name = "Difficulty",value = difficulty)
                    embed.add_field(name = "Question",value = question,inline = False)
                    view = TrueFalseView(correct)
                    event = await message.channel.send(embed = embed,view = view)
                    view.message = event
                    response = await view.wait()
                    if response:
                        return await event.edit(content = "This drop has timed out!")
                    for child in view.children:
                        child.disabled = True
                    await event.edit(view = view)
                    amount = random.randint(75*type2,125*type2)
                    balance = await self.process_amount(view.value,amount)
                    embed = discord.Embed(description = f"**{view.value}** has claimed **{amount}** {self.settings[str(message.guild.id)]['emoji']}!\nTheir total balance is **{balance}** {self.settings[str(message.guild.id)]['emoji']}",color = discord.Color.green())
                    await event.reply(embed = embed)
                else:
                    embed = discord.Embed(title = "It's Trivia Time!",description = f"Answer the question correctly to win!",color = discord.Color.random())
                    embed.add_field(name = "Category",value = category)
                    embed.add_field(name = "Difficulty",value = difficulty)
                    embed.add_field(name = "Question",value = question,inline = False)
                    view = MultipleChoiceView(correct)
                    position = random.randint(0,3)
                    view.children[position].label = correct
                    for index,child in enumerate(view.children):
                        if index == position:
                            continue
                        child.label = incorrect.pop()
                    event = await message.channel.send(embed = embed,view = view)
                    view.message = event
                    response = await view.wait()
                    if response:
                        return await event.edit(content = "This drop has timed out!")
                    for child in view.children:
                        child.disabled = True
                    await event.edit(view = view)
                    amount = random.randint(100*type2,150*type2)
                    balance = await self.process_amount(view.value,amount)
                    embed = discord.Embed(description = f"**{view.value}** has claimed **{amount}** {self.settings[str(message.guild.id)]['emoji']}!\nTheir total balance is **{balance}** {self.settings[str(message.guild.id)]['emoji']}",color = discord.Color.green())
                    await event.reply(embed = embed)
        elif type == "boss":
            chance = random.randint(1,200)
            if chance <= 1:
                rarity = "mythic"
                title = "🌟 Mythic Boss 🌟"
                description = "No idea where you found this but...seems to have some good stuff. Are you hacking?"
                footer = f"Kill the boss to receieve 10000 {self.settings[str(message.guild.id)]['name']}s! This boss has a 0.5% Chance of Spawning."
                final = 10000
                multiplier = 100
                health = 5000
            elif chance <= 10:
                rarity = "legendary"
                title = "🟨 Legendary Boss"
                description = "The legends are true! Take it down and become the hero of the story!"
                footer = f"Kill the boss to receieve 4000 {self.settings[str(message.guild.id)]['name']}s! This boss has a 4.5% Chance of Spawning."
                final = 4000
                multiplier = 60
                health = 2000
            elif chance <= 30:
                rarity = "epic"
                title = "🟪 Epic Boss"
                description = "Very epic indeed, we better take it down for its items."
                footer = f"Kill the boss to receieve 2000 {self.settings[str(message.guild.id)]['name']}s! This boss has a 10% Chance of Spawning."
                final = 2000
                multiplier = 12
                health = 400
            elif chance <= 70:
                rarity = "rare"
                title = "🟦 Rare Boss"
                description = "It says it is rare, it must have some good drops right?"
                footer = f"Kill the boss to receieve 500 {self.settings[str(message.guild.id)]['name']}s! This boss has a 20% Chance of Spawning."
                final = 500
                multiplier = 3
                health = 200
            elif chance <= 130:
                rarity = "uncommon"
                title = "🟩 Uncommon Boss"
                description = "Well at least is isn't a common boss I suppose."
                footer = f"Kill the boss to receieve 100 {self.settings[str(message.guild.id)]['name']}s! This boss has a 30% Chance of Spawning."
                final = 100
                multiplier = 1
                health = 150
            else:
                rarity = "common"
                title = "⬜ Common Boss"
                description = "Bad luck today huh? Or just normal luck I guess."
                footer = f"Kill the boss to receieve 100 {self.settings[str(message.guild.id)]['name']}s! This boss has a 45% Chance of Spawning."
                final = 50
                multiplier = 0.5
                health = 100

            edescription = description + f"\n\n**Boss Health 😡:** {health}/{health}"
            embed = discord.Embed(title = title,description = edescription,color = discord.Color.random())
            embed.set_footer(text = footer)
            view = BossView(health,description,embed)
            event = await message.channel.send(embed = embed,view = view)
            view.message = event
            response = await view.wait()
            if response:
                return await event.edit(content = "This drop has timed out!")
            pot = len(view.hitters) * 100 * multiplier
            description = ""
            for hitter,kicked in view.hitters.items():
                if hitter == view.value:
                    given = int(final + pot * (kicked/health))
                    msg = f"**{hitter.name}** got the final hit! They got **{given} {self.settings[str(message.guild.id)]['emoji']}**\n"
                    await self.process_amount(hitter,given)
                else:
                    given = int(pot * (kicked/health))
                    msg = f"**{hitter.name}** got **{given} {self.settings[str(message.guild.id)]['emoji']}**\n"
                    await self.process_amount(hitter,given)
                description += msg
            embed = discord.Embed(description = description,color = discord.Color.gold())
            await event.reply(embed = embed)

    async def process_amount(self,member,amount):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        current = ref.child("drops").child(str(member.guild.id)).child(str(member.id)).child("amount").get() or 0
        ref.child("drops").child(str(member.guild.id)).child("members").child(str(member.id)).child("amount").set(current + amount)
        return current + amount
    
    @commands.hybrid_group(name = "drops")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def drops(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help drops` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)
    
    @drops.command(name = "balance",help = "Check your own balance, or someone else's.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The message to be displayed if someone mentions you.")
    async def balance(self, ctx: commands.Context, member: discord.Member = None) -> None:
        member = member or ctx.author
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        current = ref.child("drops").child(str(member.guild.id)).child("members").child(str(member.id)).child("amount").get() or 0
        team = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(member.id)).child("team").get() or None
        embed = discord.Embed(title = f"{member}'s Balance", description = f"**{current}** {self.settings[str(ctx.guild.id)]['emoji']}\n**Team Affiliation:** `{team}`")

        embed.timestamp = datetime.datetime.now()
        await ctx.reply(embed = embed)
    
    @drops.command(name = "share",help = "Share some drops items with another user.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The member to give the items to.")
    @app_commands.describe(amount = "The number of items to give to them.")
    async def balance(self, ctx: commands.Context, member: discord.Member, amount: int) -> None:
        if amount <= 0:
            return await ctx.reply(embed = discord.Embed(description = f"How are you planning to share **{amount}**? Try a positive number.",color = discord.Color.red()))
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        current = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("amount").get() or 0
        if current < amount:
            return await ctx.reply(embed = discord.Embed(description = f"You currently have **{current}** {self.settings[str(ctx.guild.id)]['emoji']}, how are you planning to share **{amount}**?",color = discord.Color.red()))
        other = ref.child("drops").child(str(member.guild.id)).child("members").child(str(member.id)).child("amount").get() or 0
        ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("amount").set(current-amount)
        ref.child("drops").child(str(member.guild.id)).child("members").child(str(member.id)).child("amount").set(other + amount)
        await ctx.reply(embed = discord.Embed(description = f"**{ctx.author}** gave **{member}** **{amount}** {self.settings[str(ctx.guild.id)]['emoji']}\n**{ctx.author}** has **{current-amount}** {self.settings[str(ctx.guild.id)]['emoji']}\n**{member}** has **{other + amount}** {self.settings[str(ctx.guild.id)]['emoji']}",color = discord.Color.green()))
    
    @drops.command(name = "leaderboard",help = "Check the leaderboard")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(type = "The leaderboard type you want to view.")
    async def leaderboard(self, ctx: commands.Context, type: Literal['member','team']) -> None:
        message = await ctx.reply(embed = discord.Embed(description = "<a:OB_Loading:907101653692456991> Generating leaderboard, please standby.",color = discord.Color.random()))
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        if type == 'member':
            data = ref.child("drops").child(str(ctx.guild.id)).child("members").get() or {}
            memberdata = {}
            def check(a):
                try:
                    memberdata[a] = data[a].get("amount",0)
                    return data[a].get("amount",0)
                except:
                    return 0
            if data:
                dsorted = sorted(data, key= lambda a: check(a), reverse=True)
            else:
                dsorted = []
            formatter = LeaderboardPageSource(dsorted,memberdata,type,self.settings[str(ctx.guild.id)]['emoji'])
        if type == 'team':
            data = ref.child("drops").child(str(ctx.guild.id)).get() or {}
            teams = data.get("teams",{})
            teamdata = {}
            def check(a):
                total = 0
                try:
                    for member in teams[a].get("members",[]):
                        total += data.get("members",{}).get(str(member),{}).get("amount",0)
                    teamdata[a] = total
                    return total
                except:
                    return 0
            if data:
                dsorted = sorted(teams, key= lambda a: check(a), reverse=True)
            else:
                dsorted = []
            formatter = LeaderboardPageSource(dsorted,teamdata,type,self.settings[str(ctx.guild.id)]['emoji'],teams)
        menu = LeaderboardPages(formatter, delete_message_after=True)
        await menu.start(ctx,message)
    
    @drops.command(name = "generate",help = "Generate currency and give it to the selected member.")
    @commands.has_permissions(administrator = True)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The member you wish to give the currency to.")
    @app_commands.describe(amount = "The amount to generate and give to the member.")
    async def generate(self, ctx: commands.Context, member:discord.Member,amount:int) -> None:
        if amount <= 0:
            return await ctx.reply(embed = discord.Embed(description = "Your generated amount must be greater than 0.",color = discord.Color.red()))
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        current = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("amount").get() or 0
        ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("amount").set(current + amount)
        await ctx.reply(embed = discord.Embed(description = f"Generated **{amount}** {self.settings[str(ctx.guild.id)]['emoji']} for **{member}**!\nThey now have **{current + amount}** {self.settings[str(ctx.guild.id)]['emoji']}",color = discord.Color.green()))

    @drops.command(name = "reset",help = "Reset currency or all team data. Does not reset settings.")
    @commands.has_permissions(administrator = True)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(type = "The type you need to reset/clear.")
    async def reset(self, ctx: commands.Context, type: Literal['currency','teams']) -> None:
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        message = await ctx.reply(embed = discord.Embed(description = f"Resetting **{type}** for **{ctx.guild}**, please standby.",color = discord.Color.random()))
        if type == "currency":
            data = ref.child("drops").child(str(ctx.guild.id)).child("members").get() or {}
            for member in data:
                if "amount" in data[member]:
                    data[member].pop("amount")
            ref.child("drops").child(str(ctx.guild.id)).child("members").set(data)
            await message.edit(embed = discord.Embed(description = f"Reset all currency for **{ctx.guild}**!",color = discord.Color.green()))
        elif type == "teams":
            data = ref.child("drops").child(str(ctx.guild.id)).get() or {}
            if "teams" in data:
                data.pop("teams")
            for member in data.get("members",{}):
                if "team" in data["members"][member]:
                    data["members"][member].pop("team")
            ref.child("drops").child(str(ctx.guild.id)).set(data)
            await message.edit(embed = discord.Embed(description = f"Reset all team data for **{ctx.guild}**!",color = discord.Color.green()))
    
    @drops.group(name = "team",help = "Commands dealing with teams in drops.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def team(self, ctx: commands.Context) -> None:
       if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help drops team` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)
    
    @team.command(name = "create",help = "Create a team!")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(name = "The name for your team!")
    @app_commands.describe(visibility = "Whether you require applications, or allow anyone to join.")
    async def create(self, ctx: commands.Context, visibility: Literal['public','private'],name:str) -> None:
        ref = db.reference("/",app = firebase_admin._apps['elead'])

        current = ref.child("drops").child(str(ctx.guild.id)).child("members").child("team").get()
        if current:
            return await ctx.reply(embed = discord.Embed(description = f"You are already on a team with id of `{current}`! Please leave this team before joining another one.",color = discord.Color.red()))
        
        teamid = int(str(uuid.uuid4().int)[0:11])
        view = ConfirmationView(ctx)
        message = await ctx.reply(embed = discord.Embed(title = "Pending Confirmation",description = f"You are attempting to make a team with the following parameters:\n\n**Team Name:** {name}\n**Team Captain:** {ctx.author.mention}\n**Team Visibility:** {visibility}",color = discord.Color.random()),view = view)
        view.message = message
        response = await view.wait()
        if response or not view.value:
            return message.reply(embed = discord.Embed(description = "Guess we aren't doing this today.",color = discord.Color.red()))
        ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("team").set(teamid)
        ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).set({"name":name,"members":[ctx.author.id],"visibility":visibility})
        await message.reply(embed = discord.Embed(title = "Team Created!",description = f"**Team ID:** {teamid}\n**Team Name:** {name}\n**Team Captain:** {ctx.author.mention}\n**Team Visibility:** {visibility}",color = discord.Color.random()),view = view)

    @team.command(name = "join",help = "Join a team!")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(teamid = "The ID of the team to join")
    async def join(self, ctx: commands.Context, teamid:int) -> None:
        ref = db.reference("/",app = firebase_admin._apps['elead'])

        current = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("team").get()
        if current:
            return await ctx.reply(embed = discord.Embed(description = f"You are already on a team with id of `{current}`! Please leave this team before joining another one.",color = discord.Color.red()))

        team = ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).get()
        if not team:
            return await ctx.reply(embed = discord.Embed(description = f"That team id does not exsist!",color = discord.Color.red()))

        if len(team['members']) >= 5:
            return await ctx.reply("This team is already at the limit of 5 members! Find another team to join")

        def check(i):
            if i.channel.id == ctx.channel.id and i.author.id == ctx.message.author.id:
                return True
            else:
                return False
        if team["visibility"] == "public":
            otherapps = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("applications").get() or {}
            for teamid,appid in otherapps.items():
                ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).child("applications").child(str(appid)).delete()
            ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("applications").delete()
            ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("team").set(teamid)
            team["members"].append(ctx.author.id)
            ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).set(team)
            await ctx.reply(embed = discord.Embed(title = "Join Success!",description = f"You have successfully joined: {team['name']}!\nAny other exsisting applications have been deleted.",color = discord.Color.green()))
        else:
            status = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("applications").child(str(teamid)).get()
            if status:
                return await ctx.reply(embed = discord.Embed(description = f"Your application to `{teamid}` is pending! Please await their decision.",color = discord.Color.red()))
            requestid = int(str(uuid.uuid4().int)[0:11])
            embed = discord.Embed(description = f"**{team['name']}** is a private team! Type a quick explanation on why you should be able to join the team.",color = discord.Color.random())
            embed.set_footer(text = "You application, along with your short response, will be sent to the team leader for review.")
            message = await ctx.reply(embed = embed)
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                return await message.reply(embed = discord.Embed(description = "You took too to respond. Try again when you can type faster.",color = discord.Color.random()))

            requestdata = {"applicant":ctx.author.id,"reason":msg.content,"status":"🟨 Pending"}
            ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).child("applications").child(str(requestid)).set(requestdata)
            ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("applications").child(str(teamid)).set(requestid)
            embed = discord.Embed(description = f"Thank you for your application! You can view your application while it is pending with `[prefix]drops team application {requestid}`",color = discord.Color.green())
            await message.reply(embed = embed)

            try:
                host = ctx.guild.get_member(int(team['members'][0]))
                embed = discord.Embed(title = f"You have a new team application in {ctx.guild.name}!",description = f"View the application with `[prefix]drops team application {requestid}`",color = discord.Color.random())
                dm = host.dm_channel
                if dm == None:
                    dm = await host.create_dm()
                await dm.send(embed = embed)
            except:
                pass
    
    @team.command(name = "application",help = "View your own application, or view team applications as a team leader.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(applicationid = "The ID of the application to view")
    async def application(self, ctx: commands.Context, applicationid:int) -> None:
        ref = db.reference("/",app = firebase_admin._apps['elead'])

        team = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("team").get()
        if team:
            teamdata = ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(team)).get()

            if int(teamdata['members'][0]) != ctx.author.id:
                return await ctx.reply(embed = discord.Embed(description = "Only the team leader can view applications!",color = discord.Color.red()))
            
            if str(applicationid) not in teamdata.get("applications",{}):
                return await ctx.reply(embed = discord.Embed(description = f"An application with id `{applicationid}` does not exsist for your team!",color = discord.Color.red()))

            application = teamdata["applications"][str(applicationid)]
            if not application['status'] == "🟨 Pending":
                embed = discord.Embed(title = f"Application #{applicationid}",color = discord.Color.green())
                embed.add_field(name = "Applicant",value = f"<@{application['applicant']}> (`{application['applicant']}`)",inline = False)     
                embed.add_field(name = "Status",value = application['status'],inline = False)
                embed.add_field(name = "Application Reason",value = application['reason'])
                if application['status'] == "🟥 Rejected":
                    embed.add_field(name = "Rejection Reason",value = application['rreason'],inline = False)
                    embed.color = discord.Color.red()
                await ctx.reply(embed = embed)
            else:
                embed = discord.Embed(title = f"Application #{applicationid}",color = discord.Color.gold())
                embed.add_field(name = "Applicant",value = f"<@{application['applicant']}> (`{application['applicant']}`)",inline = False)     
                embed.add_field(name = "Status",value = application['status'],inline = False)
                embed.add_field(name = "Application Reason",value = application['reason'])
                embed.set_footer(text = "Accept or deny this application with the buttons below!")
                view = ConfirmationView(ctx)
                message = await ctx.reply(embed = embed,view = view)
                view.message = message
                response = await view.wait()
                if response:
                    return message.reply(embed = discord.Embed(description = "Guess we aren't doing this today.",color = discord.Color.red()))
                
                if not view.value:
                    def check(i):
                        if i.channel.id == ctx.channel.id and i.author.id == ctx.message.author.id:
                            return True
                        else:
                            return False
                    await message.reply(embed = discord.Embed(description = "Enter a reason for rejecting this application:",color = discord.Color.random()))
                    try:
                        msg = await self.client.wait_for("message",timeout = 60.0,check=check)
                    except asyncio.TimeoutError:
                        return await message.reply(embed = discord.Embed(description = "You took too to respond. Try again when you can type faster.",color = discord.Color.random()))
                    
                    application['status'] = "🟥 Rejected"
                    application['rreason'] = msg.content
                    ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(application['applicant'])).child("applications").child(str(team)).delete()
                    ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(team)).child("applications").child(str(applicationid)).set(application)
                    embed = discord.Embed(title = f"Rejected Application #{applicationid}",description = f"You rejected <@{application['applicant']}> from {teamdata['name']}.",color = discord.Color.red())
                    await msg.reply(embed = embed)
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
                else:
                    otherapps = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(application['applicant'])).child("applications").get() or {}
                    for teamid,appid in otherapps.items():
                        ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).child("applications").child(str(appid)).delete()
                    ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(application['applicant'])).child("applications").delete()
                    ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(application['applicant'])).child("team").set(teamid)
                    teamdata["members"].append(str(application['applicant']))
                    ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).set(teamdata)
                    application['status'] = "🟩 Accepted"
                    ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).child("applications").child(str(applicationid)).set(application)
                    embed = discord.Embed(title = f"Accepted Application #{teamid}",description = f"You accepted <@{application['applicant']}> to {teamdata['name']}.",color = discord.Color.green())
                    await message.reply(embed = embed)
        else:
            apps = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("applications").get()
            if not apps:
                return await ctx.reply(embed = discord.Embed(description = "You don't have any applications!",color = discord.Color.red()))
            application = None
            for teamid,appid in apps.items():
                if appid == applicationid:
                    application = ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).child("applications").child(str(appid)).get()
            if application:
                embed = discord.Embed(title = f"Application #{applicationid}",color = discord.Color.green())
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
                return await ctx.reply(embed = discord.Embed(description = "That isn't your application, or that application does not exsist!",color = discord.Color.red()))

    @team.command(name = "applicationlist",help = "View the list of application you have, or as a team leader.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def applicationlist(self, ctx: commands.Context) -> None:
        ref = db.reference("/",app = firebase_admin._apps['elead'])

        team = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("team").get()
        if team:
            teamdata = ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(team)).get()
            teammembers = teamdata['members']

            if int(teamdata['members'][0]) != ctx.author.id:
                return await ctx.reply(embed = discord.Embed(description = "Only the team leader can view applications!",color = discord.Color.red()))
            message = await ctx.reply(embed = discord.Embed(description = "<a:OB_Loading:907101653692456991> Gathering team data, please wait.",color = discord.Color.random()))
            applications = teamdata.get("applications",{})
            formatter = ApplicationPageSource(list(applications.keys()),applications)
            menu = LeaderboardPages(formatter, delete_message_after=True)
            await menu.start(ctx,message)
        else:
            applications = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("applications").get()

            if not applications:
                return await ctx.reply(embed = discord.Embed(description = "You have no active applications!",color = discord.Color.red()))
            
            description = "**Team ID:Application ID**\n"
            for teamid, appid in applications.items():
                description += f"{teamid}:{appid}\n"
            embed = discord.Embed(title = "Pending Applications",description = description, color = discord.Color.random())
            embed.set_footer(text = "Use [prefix]drops team application <appid> to view the application!")
            await ctx.reply(embed = embed)

    @team.command(name = "kick",help = "As a team leader, kick a member off your team.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The member you want to kick off your team.")
    async def kick(self, ctx: commands.Context, member: discord.Member) -> None:
        ref = db.reference("/",app = firebase_admin._apps['elead'])

        team = ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(ctx.author.id)).child("team").get()
        if team:
            teamdata = ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(team)).get()
            teammembers = teamdata['members']

            if int(teammembers[0]) != ctx.author.id:
                await ctx.reply(embed = discord.Embed(description = "You are not the leader for your team! Only team leaders can kick.",color = discord.Color.red()))

            if member.id not in teammembers:
                await ctx.reply(embed = discord.Embed(description = "This person is not on your team!",color = discord.Color.red()))

            teamdata['members'].remove(member.id)
            ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(team)).set(teamdata)
            ref.child("drops").child(str(ctx.guild.id)).child("members").child("team").delete()

            await ctx.reply(embed = discord.Embed(description = f"Successfully kicked **{member}** from your team!",color = discord.Color.green()))

            try:
                embed = discord.Embed(description = f"You were kicked from {teamdata['name']}",color = discord.Color.red())
                dm = member.dm_channel
                if dm == None:
                    dm = await member.create_dm()
                await dm.send(embed = embed)
            except:
                pass
        else:
            await ctx.reply(embed = discord.Embed(description = "You aren't even on a team, how you planning to kick someone?",color = discord.Color.red()))

    @team.command(name = "info",help = "View the information for a team with the specified id.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(teamid = "The team you want to view information for.")
    async def info(self, ctx: commands.Context, teamid: int) -> None:
        ref = db.reference("/",app = firebase_admin._apps['elead'])

        teamdata = ref.child("drops").child(str(ctx.guild.id)).child("teams").child(str(teamid)).get()
        if not teamdata:
            return await ctx.reply(embed = discord.Embed(description = f"The team with id `{teamid}` does not exsist!",color = discord.Color.red()))
        
        embed = discord.Embed(title = f"Team Info for {teamdata['name']}",description = f"ID: {teamid}",color = discord.Color.random())
        embed.add_field(name = "Team Members",value = "\n ".join([f"<:replycont:913966803263291422> <@" + str(i) + ">" for i in teamdata['members'] if i != teamdata['members'][-1]]) + f"\n<:replyend:913967325429002302> <@{teamdata['members'][-1]}>",inline = False)
        embed.add_field(name = "Team Visibility",value = teamdata['visibility'],inline = False)
        total = 0
        for member in teamdata['members']:
            total += ref.child("drops").child(str(ctx.guild.id)).child("members").child(str(member)).child("amount").get() or 0 
        embed.add_field(name = "Total Items",value = f"`{total}` {self.settings[str(ctx.guild.id)]['emoji']}",inline = False)
        await ctx.reply(embed = embed)
            
class ConfirmationView(discord.ui.View):
    def __init__(self,ctx):
        super().__init__(timeout = 60)
        self.ctx = ctx
        self.value = None
        self.message = None

    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
    
    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        await interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False

    @discord.ui.button(emoji = "✅",style = discord.ButtonStyle.green)
    async def confirm(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = True
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()
    
    @discord.ui.button(emoji = "✖",style = discord.ButtonStyle.red)
    async def deny(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = False
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()

class ButtonPressView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 30)
        self.message = None
        self.value = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    @discord.ui.button(label = "Claim!",style = discord.ButtonStyle.green)
    async def confirm(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = interaction.user
        self.stop()

class ReactionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 60)
        self.message = None
        self.value = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    @discord.ui.button(emoji = "<:GrayButton:904112302918369301>",style = discord.ButtonStyle.gray,disabled = True)
    async def button1(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = interaction.user
        self.stop()
    
    @discord.ui.button(emoji = "<:GrayButton:904112302918369301>",style = discord.ButtonStyle.gray,disabled = True)
    async def button2(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = interaction.user
        self.stop()
    
    @discord.ui.button(emoji = "<:GrayButton:904112302918369301>",style = discord.ButtonStyle.gray,disabled = True)
    async def button3(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = interaction.user
        self.stop()
    
    @discord.ui.button(emoji = "<:GrayButton:904112302918369301>",style = discord.ButtonStyle.gray,disabled = True)
    async def button4(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = interaction.user
        self.stop()
    
    @discord.ui.button(emoji = "<:GrayButton:904112302918369301>",style = discord.ButtonStyle.gray,disabled = True)
    async def button5(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.value = interaction.user
        self.stop()

class TrueFalseView(discord.ui.View):
    def __init__(self,answer):
        super().__init__(timeout = 30)
        self.message = None
        self.value = None
        self.answer = answer
        self.wrong = []
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction):
        if interaction.user in self.wrong:
            await interaction.response.send_message(embed = discord.Embed(description = "You have already answered incorrectly!",color = discord.Color.red()), ephemeral = True)
            return False
        return True

    @discord.ui.button(label = "True",style = discord.ButtonStyle.green)
    async def true(self,interaction:discord.Interaction,button:discord.ui.Button):
        if button.label == self.answer:
            await interaction.response.defer()
            self.value = interaction.user
            self.stop()
        else:
            self.wrong.append(interaction.user)
            await interaction.response.send_message(embed = discord.Embed(description = "You answered incorrectly! Better luck next time.",color = discord.Color.red()), ephemeral = True)
    
    @discord.ui.button(label = "False",style = discord.ButtonStyle.red)
    async def false(self,interaction:discord.Interaction,button:discord.ui.Button):
        if button.label == self.answer:
            await interaction.response.defer()
            self.value = interaction.user
            self.stop()
        else:
            self.wrong.append(interaction.user)
            await interaction.response.send_message(embed = discord.Embed(description = "You answered incorrectly! Better luck next time.",color = discord.Color.red()), ephemeral = True)

class MultipleChoiceView(discord.ui.View):
    def __init__(self,answer):
        super().__init__(timeout = 30)
        self.message = None
        self.value = None
        self.answer = answer
        self.wrong = []
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction):
        if interaction.user in self.wrong:
            await interaction.response.send_message(embed = discord.Embed(description = "You have already answered incorrectly!",color = discord.Color.red()), ephemeral = True)
            return False
        return True

    @discord.ui.button(label = ".",style = discord.ButtonStyle.gray)
    async def answer1(self,interaction:discord.Interaction,button:discord.ui.Button):
        if button.label == self.answer:
            await interaction.response.defer()
            self.value = interaction.user
            self.stop()
        else:
            self.wrong.append(interaction.user)
            await interaction.response.send_message(embed = discord.Embed(description = "You answered incorrectly! Better luck next time.",color = discord.Color.red()), ephemeral = True)
    
    @discord.ui.button(label = ".",style = discord.ButtonStyle.gray)
    async def answer2(self,interaction:discord.Interaction,button:discord.ui.Button):
        if button.label == self.answer:
            await interaction.response.defer()
            self.value = interaction.user
            self.stop()
        else:
            self.wrong.append(interaction.user)
            await interaction.response.send_message(embed = discord.Embed(description = "You answered incorrectly! Better luck next time.",color = discord.Color.red()), ephemeral = True)
    
    @discord.ui.button(label = ".",style = discord.ButtonStyle.gray)
    async def answer3(self,interaction:discord.Interaction,button:discord.ui.Button):
        if button.label == self.answer:
            await interaction.response.defer()
            self.value = interaction.user
            self.stop()
        else:
            self.wrong.append(interaction.user)
            await interaction.response.send_message(embed = discord.Embed(description = "You answered incorrectly! Better luck next time.",color = discord.Color.red()), ephemeral = True)
    
    @discord.ui.button(label = ".",style = discord.ButtonStyle.gray)
    async def answer4(self,interaction:discord.Interaction,button:discord.ui.Button):
        if button.label == self.answer:
            await interaction.response.defer()
            self.value = interaction.user
            self.stop()
        else:
            self.wrong.append(interaction.user)
            await interaction.response.send_message(embed = discord.Embed(description = "You answered incorrectly! Better luck next time.",color = discord.Color.red()), ephemeral = True)

class BossView(discord.ui.View):
    def __init__(self,health,description,embed):
        super().__init__(timeout = 60)
        self.message = None
        self.value = None
        self.health = health
        self.current = health
        self.description = description
        self.embed = embed
        self.hitters = {}
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    @discord.ui.button(label = "Hit!",style = discord.ButtonStyle.green)
    async def confirm(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            await interaction.response.defer()
            damage = random.randint(5,30)
            self.current -= damage
            self.hitters[interaction.user] = self.hitters.get(interaction.user,0) + damage
            if self.current <= 0:
                self.current = 0
                self.embed.description = self.description + f"\n\n**Boss Health 😡:** {self.current}/{self.health}"
                self.children[0].disabled = True
                await self.message.edit(content = "The boss has been defeated!",embed = self.embed,view = self)
                self.value = interaction.user
                self.stop()
            self.embed.description = self.description + f"\n\n**Boss Health 😡:** {self.current}/{self.health}"
            await self.message.edit(embed = self.embed)
        except:
            pass
        
class LeaderboardPages(ui.View, menus.MenuPages):
    def __init__(self, source, *, delete_message_after=False):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def start(self, ctx, message):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx,message)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value
    
    async def send_initial_message(self, ctx,message):
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await message.edit(**kwargs)
    
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
    
class LeaderboardPageSource(menus.ListPageSource):
    def __init__(self, data, log, type,emoji, teamdata = None):
        super().__init__(data, per_page=5)
        self.log = log
        self.type = type
        self.emoji = emoji
        self.teamdata = teamdata
    def format_leaderboard_entry(self, no, user):
        if self.type == "member":
            return f"**{no}. <@{user}>** `{self.log[user]}` {self.emoji} Collected"
        else:
            return f"**{no}. {self.teamdata[user]['name']}**\n<:replycont:913966803263291422> **Team ID:** {user}\n<:replyend:913967325429002302> `{self.log[user]}` {self.emoji} Collected"
    async def format_page(self, menu, users):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_leaderboard_entry, enumerate(users, start=starting_number))
        page_content = "\n".join(iterator)
        embed = discord.Embed(
            title=f"Drops Leaderboard [{page + 1}/{max_page}]", 
            description=page_content,
            color= discord.Color.random()
        )
        embed.set_footer(text=f"Use the buttons below to navigate pages!") 
        return embed

class ApplicationPageSource(menus.ListPageSource):
    def __init__(self, data, log):
        super().__init__(data, per_page=5)
        self.log = log

    def format_leaderboard_entry(self, no, application):
        return f"**{no}.** <@{self.log[application]['applicant']}>\n<:replycont:913966803263291422> Application ID: {application}\n<:replyend:913967325429002302> Status: {self.log[application]['status']}"
        
    async def format_page(self, menu, users):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_leaderboard_entry, enumerate(users, start=starting_number))
        page_content = "\n".join(iterator)
        embed = discord.Embed(
            title=f"Application List [{page + 1}/{max_page}]", 
            description=page_content,
            color= discord.Color.random()
        )
        embed.set_footer(text=f"Use the buttons below to navigate pages!") 
        return embed

async def setup(client):
    await client.add_cog(DropsGame(client))