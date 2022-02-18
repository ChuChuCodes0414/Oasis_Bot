from tkinter import NONE
import discord
from discord.ext import commands
import asyncio
import random
from discord import channel
import discord_components
from discord_components import Button
import requests
import fontstyle
import ast
import html
import cv2
import numpy as np
import matplotlib.pyplot as plt
import textwrap
#db organised as:
#DANKTRADES
#inventories , stock , settings

class HelpRewrite(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.tracking = {}
        self.events = {
            'normal' : 1,
            'rare' : 5,
            'legendary' : 15,
        }
        self.active = False
        self.eventtypes = ["button","reaction","sentence","math","trivia"]
        self.sentences = ["abc sux"] # list of sentences to be given out
        self.dump_channel = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.dump_channel = self.client.get_channel(870127759526101032)
        self.active = True
        print('Event Cog Loaded.')
    
    async def give_item(self,user,rarity):
        return "an item lol"
    
    async def process_sentence(self,sentence):
        wrapped_text = textwrap.wrap(sentence, width=35)
        height, width = len(wrapped_text) * 32 + 50, 590
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

    async def spawn_event(self,message,rarity:str,type:str = None):
        """
        Handle the spawning of the events. Also gives out the items to people.
        """
        type = type or self.eventtypes[random.randint(0,len(self.eventtypes)-1)]

        if type == "button":
            embed = discord.Embed(title = f"{rarity.capitalize()} Event Spawn!",description = "Be the first to click the button to claim the prize.",color = discord.Color.random())
            message = await message.channel.send(embed = embed,components = [Button(label = f"Claim!",style = 3)])
            # it is possible to add a check here that ensures that author has talked recently. however, it is commented out
            def check(i):
                # if i.user.id not in self.tracking[message.channel.id]
                if i.message.id == message.id:
                    return True
                else:
                    return False
            try:
                interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
            except asyncio.TimeoutError:
                return await message.edit("The drop timed out and can no longer be claimed",embed = embed, components = [Button(label = f"Claim!",style = 3,disabled = True)])
            
            await message.edit("Drop Claimed!",embed = embed, components = [Button(label = f"Claim!",style = 2,disabled = True)])

            # need to check on this
            item = await self.give_item(interaction.user.id,rarity)

            embed = discord.Embed(description = f"**{interaction.user}** has claimed `{item}`!",color = discord.Color.green())
            return await interaction.respond(embed = embed,ephemeral = False)
        elif type == "reaction":
            # these emojis are just the colors of the buttons to give the illusion of the button being blank. you can change it as you please.
            buttons = [[Button(emoji = self.client.get_emoji(904112302918369301),disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),disabled = True),Button(emoji = self.client.get_emoji(904112302918369301),disabled = True)]]
            selected = random.randint(0,3)
            
            embed = discord.Embed(title = "Think Fast! Let's see your reaction time.",description = f"Once the buttons are opened, click the green one first to claim!",color = discord.Color.random())
            message = await message.channel.send(embed = embed,components = buttons)
            buttons[0][selected] = Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = False)

            time = random.randint(3,10)
            await asyncio.sleep(time)
            await message.edit(components = buttons)

            # it is possible to add a check here that ensures that author has talked recently. however, it is commented out
            def check(i):
                # if i.user.id not in self.tracking[message.channel.id]
                if i.message.id == message.id:
                    return True
                else:
                    return False
            try:
                interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
            except asyncio.TimeoutError:
                buttons[0][selected] = Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = True)
                return await message.edit("The drop timed out and can no longer be claimed.", components = buttons)
            buttons[0][selected] = Button(emoji = self.client.get_emoji(904112314393968740),style = 3,disabled = True)
            await message.edit(components = buttons)

            item = await self.give_item(interaction.user.id,rarity)

            embed = discord.Embed(description = f"**{interaction.user}** has claimed `{item}`!",color = discord.Color.green())
            return await interaction.respond(embed = embed,ephemeral = False)
        elif type == "sentence":
            if random.randint(0,1) == 0:
                phrase = self.sentences[random.randint(0,len(self.sentences)-1)]
                author = "Dank Trades Team"
            else:
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

            embed = discord.Embed(title = f"{rarity.capitalize()} Event Spawn!",description = f"Type the sentence to pick it up!",color = discord.Color.random())
            embed.set_image(url = await self.process_sentence(phrase))
            embed.set_footer(text = f"Quote From {author}")
            message = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == message.channel.id and i.content.lower() == phrase.lower():
                    return True
                else:
                    return False
            
            while True:
                try:
                    message = await self.client.wait_for("message",timeout = 45.0,check = check)
                except asyncio.TimeoutError:
                    return await message.edit("The drop timed out. Are yall dead?")

                else:
                    break
            item = await self.give_item(message.author.id,rarity)
            embed = discord.Embed(description = f"**{message.author}** has claimed `{item}`!",color = discord.Color.green())
            await message.reply(embed = embed,mention_author = False)
        elif type == "trivia":
            if rarity == "normal":
                response = requests.get("https://opentdb.com/api.php?amount=1&difficulty=easy")
            elif rarity == "rare":
                response = requests.get("https://opentdb.com/api.php?amount=1&difficulty=medium")
            elif rarity == "legendary":
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
                dumbs = [] # who has answered already and can no longer answer again
                if mcotf == "boolean":
                    embed = discord.Embed(title = "It's Trivia Time!",description = f"{rarity.capitalize()} Event",color = discord.Color.random())
                    embed.add_field(name = "Category",value = category)
                    embed.add_field(name = "Difficulty",value = difficulty)
                    embed.add_field(name = "Question",value = question,inline = False)
                    message = await message.channel.send(embed = embed,components = [[Button(label = "True",style = 3),Button(label = "False",style = 4)]])

                    # it is possible to add a check here that ensures that author has talked recently. however, it is commented out
                    def check(i):
                        # if i.user.id not in self.tracking[message.channel.id]
                        if i.message.id == message.id and not i.user.id in dumbs:
                            return True
                        else:
                            return False
                    while True: # small catch any wrong answer resets 30 second timer
                        try:
                            interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
                        except asyncio.TimeoutError:
                            return await message.edit("The drop timed out and can no longer be claimed.", components = [[Button(label = "True",style = 3,disabled = True),Button(label = "False",style = 4,disabled = True)]])
                        if interaction.component.label != correct:
                            await interaction.respond(content = "Wrong answer loser!") # a bit harsh maybe should be changed lol
                            dumbs.append(interaction.user.id)
                            continue
                        break
                    await message.edit("Drop Claimed!", components = [[Button(label = "True",style = 3,disabled = True),Button(label = "False",style = 4,disabled = True)]])
                    
                    item = await self.give_item(interaction.user.id,rarity)
                    embed = discord.Embed(description = f"**{interaction.user}** has claimed `{item}`!\nThe answer was **{correct}**",color = discord.Color.green())
                    return await interaction.respond(embed = embed,ephemeral = False)
                else:
                    embed = discord.Embed(title = "It's Trivia Time!",description = f"{rarity.capitalize()} Event",color = discord.Color.random())
                    embed.add_field(name = "Category",value = category)
                    embed.add_field(name = "Difficulty",value = difficulty)
                    embed.add_field(name = "Question",value = question,inline = False)
                    pos = random.randint(0,3)
                    buttons = []
                    dbuttons = []
                    count = 0
                    for i in range(0,4):
                        if i == pos:
                            buttons.append(Button(label = correct))
                            dbuttons.append(Button(label = correct,disabled = True))
                        else:
                            formatted = html.unescape(incorrect[count])
                            buttons.append(Button(label = formatted))
                            dbuttons.append(Button(label = formatted,disabled = True))
                            count += 1

                    message = await message.channel.send(embed = embed,components = [buttons])

                    # it is possible to add a check here that ensures that author has talked recently. however, it is commented out
                    def check(i):
                        # if i.user.id not in self.tracking[message.channel.id]
                        if i.message.id == message.id and not i.user.id in dumbs:
                            return True
                        else:
                            return False
                    while True: # small catch any wrong answer resets 30 second timer
                        try:
                            interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
                        except asyncio.TimeoutError:
                            return await message.edit("The drop timed out and can no longer be claimed.", components = [dbuttons])
                        if interaction.component.label != correct:
                            await interaction.respond(content = "Wrong answer loser!") # a bit harsh maybe should be changed lol
                            dumbs.append(interaction.user.id)
                            continue
                        break
                    await message.edit("Drop Claimed!", components = [dbuttons])
                    
                    item = await self.give_item(interaction.user.id,rarity)
                    embed = discord.Embed(description = f"**{interaction.user}** has claimed `{item}`!\nThe answer was **{correct}**",color = discord.Color.green())
                    return await interaction.respond(embed = embed,ephemeral = False)

    @commands.command()
    async def spawn(self,ctx,event:str = None):
        await ctx.send("spawning")
        await self.spawn_event(ctx.message,"normal",event)

    @commands.command()
    async def debug(self,ctx):
        embed = discord.Embed(tite = "Stored data for this channel",description = self.tracking.get(ctx.channel.id,None))
        await ctx.send(embed = embed)
    
def setup(client):
    client.add_cog(HelpRewrite(client))
