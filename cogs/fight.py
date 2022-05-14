from operator import itemgetter
import discord
from discord.ext import commands
from discord import ui
import random
import firebase_admin
from firebase_admin import db
import asyncio
import json
import datetime


class Fight(commands.Cog):
    """
        Fight command and its relevant helper commands
    """

    def __init__(self,client):
        self.client = client
        self.short = "🥊 | Fight Time!"
        self.fighters = []
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Fight Cog Loaded.')

    
    async def get_items(self,ctx,member):
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        current = ref.child(str(member)).child("badges").get()

        if current:
            return "fighter1" in current,"fighter2" in current
        else:
            return False,False
    
    async def get_fight_lb(self,ctx,category):
        if category not in ["total","win","lose"]:
            return await ctx.reply("You only got 3 choices: total, win, or lose. Gotta pick one.")
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        profiles = ref.get()

        def check(a,category):
            if category == "total":
                try:
                    return profiles[a]["fight"].get("win",0) + profiles[a]["fight"].get("lose",0)
                except:
                    return 0
            try:
                return profiles[a]["fight"].get(category,0)
            except:
                return 0
            

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

        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)

        await ctx.reply(embed = emb)

    @commands.command(help = "That fight command break again? Run this to fix your problems.",brief = "Note that this can't fix your life problems...sorry about that.")
    async def fixfight(self,ctx):
        try:
            self.fighters.remove(ctx.author.id)
            await ctx.reply("You were removed from the fighters list.")
        except:
            await ctx.reply("You sure you were in the fighters list anyways?")

    @commands.command(help = "View the global fight leaderboard!",brief = "There are 3 categories: total, win, and lose.")
    async def fightlb(self,ctx,category = "total"):
        await self.get_fight_lb(ctx,category)
    
    @commands.command(help = "Fight another user...for fun of couse.")
    async def fight(self,ctx,user:discord.Member):
        if ctx.author.id in self.fighters or user.id in self.fighters:
            return await ctx.reply(embed = discord.Embed(description = "Hold up, either you or your opponent is in a fight already. Take a chill pill and relax buddy.\nTip: Fight broke because of interaction? Try `[prefix]fixfight`!",color = discord.Color.red()))
        elif ctx.author.id == user.id:
            return await ctx.reply(embed = discord.Embed(description = "Hey, you can't fight yourself. Find another person to fight instead.",color = discord.Color.red()))
        elif user.bot:
            return await ctx.reply(embed = discord.Embed(description = "Hmmm...bots can't respond to your fight request. No free win for you.",color = discord.Color.red()))
        self.fighters.append(ctx.author.id)
        self.fighters.append(user.id)
        embed = discord.Embed(description = f"Hey **{user}**, **{ctx.author}** is challenging you to a fight! Do you accept?",color = discord.Color.random())
        view = Confirm(user)
        message = await ctx.reply(embed = embed,view = view)
        view.message = message
        timeout = await view.wait()
        if timeout:
            self.fighters.remove(ctx.author.id)
            self.fighters.remove(user.id)
            return await message.reply(embed = discord.Embed(description = "Seems your opponent did not respond. Try someone that isn't afk.",color = discord.Color.red()))
        if not view.value:
            self.fighters.remove(ctx.author.id)
            self.fighters.remove(user.id)
            return await message.reply(embed = discord.Embed(description = f"**{user}** has denied your fight request. Sad.",color = discord.Color.red()))

        embed=discord.Embed(title = "The fight begins!",description=f"First, it is time to pick your item. Both of you will choose one item. You have 30 seconds to choose.", color=discord.Color.random())
        embed.add_field(name = "Passive Items",value = "These items give passive boosts, meaning that they are active during the entire fight.")
        embed.add_field(name = "Active Items",value = "These items open up an option during the fight, depending on what you choose. Using these items will be your turn in the fight.")
        embed.add_field(name = "Choosen Weapons",value = f"<a:OB_Loading:907101653692456991> **{ctx.author}**: None\n<a:OB_Loading:907101653692456991> **{user}**: None",inline = False)
        embed.set_footer(text = "Both fighters should pick items now!")
        view = DropdownView([ctx.author,user])
        message = await message.reply(embed = embed,view = view)
        view.message = message
        view.children[1].message = message
        check = await view.wait()
        if check:
            self.fighters.remove(ctx.author.id)
            self.fighters.remove(user.id)
            return
        items = view.children[0].chosen
        names = []
        for item in items:
            names.append(" ".join(item.split()[:-1]))
        users = [[ctx.author,names[0]],[user,names[1]]]
        choice = random.choice(users)
        if choice == users[0]:
            view = FightView(ctx,users,ctx.author,user)
            for child in view.children[:-1]:
                child.style = discord.ButtonStyle.blurple
            view.children[-2].label = names[0]
            if names[0] not in ["Sword","Axe","Armor","Crossbow","Rocket Launcher"]:
                view.children[-2].disabled = True
            embed = discord.Embed(title = "The fight begins!",description = f"**{ctx.author}** is fighting **{user}**",color = discord.Color.random())
            embed.set_footer(text = f"It is currently {ctx.author}'s turn to choose! They have 30 seconds.")
        else:
            view = FightView(ctx,users,user,ctx.author)
            for child in view.children[:-1]:
                child.style = discord.ButtonStyle.red
            view.children[-2].label = names[1]
            if names[1] not in ["Sword","Axe","Armor","Crossbow","Rocket Launcher"]:
                view.children[-2].disabled = True
            embed = discord.Embed(title = "The fight begins!",description = f"**{user}** is fighting **{ctx.author}**",color = discord.Color.random())
            embed.set_footer(text = f"It is currently {user}'s turn to choose! They have 30 seconds.")
        
        embed.add_field(name = ctx.author,value = f"**Current Health:** `100`\n**Current Defense:** `0`\n**Selected Item:** `{names[0]}`")
        embed.add_field(name = user,value = f"**Current Health:** `100`\n**Current Defense:** `0`\n**Selected Item:** `{names[1]}`")
        message = await ctx.send(embed = embed,view = view)
        view.message = message
        self.fighters.remove(ctx.author.id)
        self.fighters.remove(user.id)

class FightView(discord.ui.View):
    def __init__(self,ctx,users,start, oppose):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.value = False
        self.message = None
        self.current = start
        self.oppose = oppose
        self.fightstats = {users[0][0]:[users[0][1],100,0],users[1][0]:[users[1][1],100,0]}

    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(f"**{self.current}** did not respond! The fight has timedout",view=self)

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

    async def process_action(self,interaction, damage, kickback, defense, description):
        if self.fightstats[self.oppose][0] == "Potion":
            self.fightstats[self.oppose][1] -= int(damage * 0.8)
        else:
            self.fightstats[self.oppose][1] -= damage
        if self.fightstats[self.oppose][0] == "Shield" and random.randint(1,100) <= 30:
            description = f"**{self.current}** tried to damage **{self.oppose}**, but **{self.oppose}'s** shield blocked the hit!"
        if self.fightstats[self.oppose][0] == "Armor":
            self.fightstats[self.oppose][1] -= int(damage * (1-(self.fightstats[self.oppose][2]/100))) 
        self.fightstats[self.current][1] -= kickback
        self.fightstats[self.current][2] += defense

        if self.fightstats[self.current][1] <= 0:
            self.fightstats[self.current][1] = 0
            wins = await self.add_fight_stat(self.ctx,self.oppose.id,"win")
            losses = await self.add_fight_stat(self.ctx,self.current.id,"lose")
            if wins >= 50:
                    await self.grant_badge(self.ctx,self.oppose.id,"fighter1")
            elif wins >= 100:
                await self.grant_badge(self.ctx,self.oppose.id,"fighter2")
            embed = discord.Embed(title = "🏆 The fight is now over!",description = f"**{self.current}** was fighting **{self.oppose}**",color = discord.Color.gold())
            for user,data in self.fightstats.items():
                embed.add_field(name = user,value = f"**Current Health:** `{data[1]}`\n**Current Defense:** `{data[2]}`\n**Selected Item:** `{data[0]}`")
            embed.add_field(name = "Last Action",value = description,inline = False)
            embed.set_footer(text = f"{self.oppose} has won {wins} fights | {self.current} has lost {losses} fights")
            for child in self.children: 
                child.disabled = True   
            await interaction.response.edit_message(embed = embed,view = self)
            self.stop()
        elif self.fightstats[self.oppose][1] <= 0:
            self.fightstats[self.oppose][1] = 0
            wins = await self.add_fight_stat(self.ctx,self.current.id,"win")
            losses = await self.add_fight_stat(self.ctx,self.oppose.id,"lose")
            if wins >= 50:
                    await self.grant_badge(self.ctx,self.current.id,"fighter1")
            elif wins >= 100:
                await self.grant_badge(self.ctx,self.current.id,"fighter2")
            embed = discord.Embed(title = "🏆 The fight is now over!",description = f"**{self.current}** was fighting **{self.oppose}**",color = discord.Color.gold())
            for user,data in self.fightstats.items():
                embed.add_field(name = user,value = f"**Current Health:** `{data[1]}`\n**Current Defense:** `{data[2]}`\n**Selected Item:** `{data[0]}`")
            embed.add_field(name = "Last Action",value = description,inline = False)
            embed.set_footer(text = f"{self.current} has won {wins} fights | {self.oppose} has lost {losses} fights")
            for child in self.children: 
                child.disabled = True   
            await interaction.response.edit_message(embed = embed,view = self)
            self.stop()
        else:
            embed = discord.Embed(title = "The fight continues on!",description = f"**{self.current}** is fighting **{self.oppose}**",color = discord.Color.random())
            for user,data in self.fightstats.items():
                embed.add_field(name = user,value = f"**Current Health:** `{data[1]}`\n**Current Defense:** `{data[2]}`\n**Selected Item:** `{data[0]}`")
            embed.add_field(name = "Last Action",value = description,inline = False)

            embed.set_footer(text = f"It is currently {self.oppose}'s turn to choose! They have 30 seconds.")
            temp = self.current
            self.current = self.oppose
            self.oppose = temp
            item = self.fightstats[self.current][0]
            self.children[-2].label = item
            if item not in ["Sword","Axe","Armor","Crossbow","Rocket Launcher"]:
                self.children[-2].disabled = True
            else:
                self.children[-2].disabled = False
            if self.current == list(self.fightstats.keys())[0]:
                for button in self.children[:-1]:
                    button.style = discord.ButtonStyle.blurple
            else:
                for button in self.children[:-1]:
                    button.style = discord.ButtonStyle.red
            await interaction.response.edit_message(embed = embed,view = self)
    
    async def check_current(self,interaction):
        if interaction.user == self.current:
            return True
        elif interaction.user == self.oppose:
            await interaction.response.send_message(embed = discord.Embed(description = "It is not your turn!",color = discord.Color.red()),ephemeral = True)
            return False
        else:
            await interaction.response.send_message(embed = discord.Embed(description = "This is not your fight!",color = discord.Color.red()),ephemeral = True)
            return False

    @ui.button(label= 'Punch',row = 0)
    async def punch(self, interaction, button):
        if not await self.check_current(interaction):
            return
        if self.fightstats[self.current][0] == "Clover":
            failrate = random.randint(1,301)
        else:
            failrate = random.randint(1,101)
        
        if failrate <= 5:
            damage = 0
            description = f"**{self.current}** tried to use **punch**, but they failed! Tough luck."
        else:
            damage = random.randint(5,15)
            description = f"**{self.current}** uses **punch**, dealing `{damage}` to **{self.oppose}**"
        await self.process_action(interaction,damage,0,0,description)

    @ui.button(label= 'Smack',row = 0)
    async def smack(self, interaction, button):
        if not await self.check_current(interaction):
            return
        if self.fightstats[self.current][0] == "Clover":
            failrate = random.randint(1,301)
        else:
            failrate = random.randint(1,101)
        
        if failrate <= 20:
            damage = 0
            description = f"**{self.current}** tried to use **smack**, but they failed! Must suck to suck."
        else:
            damage = random.randint(10,30)
            description = f"**{self.current}** uses **smack**, dealing `{damage}` to **{self.oppose}**"
        await self.process_action(interaction,damage,0,0,description)

    @ui.button(label= 'Kick',row = 0)
    async def kick(self, interaction, button):
        if not await self.check_current(interaction):
            return
        if self.fightstats[self.current][0] == "Clover":
            failrate = random.randint(1,301)
        else:
            failrate = random.randint(1,101)
        
        if failrate <= 40:
            damage = 0
            kickback = random.randint(5,20)
            description = f"**{self.current}** tried to **kick**, but they failed and fell over instead, causing them to take `{kickback}` damage."
        else:
            damage = random.randint(30,40)
            kickback = 0
            description = f"**{self.current}** landed a powerful **kick**, dealing `{damage}` to **{self.oppose}**"
        await self.process_action(interaction,damage,kickback,0,description)

    @ui.button(label= 'Item',row = 0)
    async def item(self, interaction, button):
        if not await self.check_current(interaction):
            return
        if self.fightstats[self.current][0] == "Clover":
            failrate = random.randint(1,301)
        else:
            failrate = random.randint(1,101)
        
        if button.label == "Sword":
            if failrate <= 40:
                damage = 0
                description = f"**{self.current}** tried to use their **sword**, but they missed their parry. Perhaps they are missing some much-needed lessons."
            else:
                damage = random.randint(30,50)
                description = f"**{self.current}** used their **sword**, and landed a powerful parry! They dealt `{damage}` to **{self.oppose}**"
            await self.process_action(interaction,damage,0,0,description)
        elif button.label == "Axe":
            if failrate <= 25:
                damage = 0
                description = f"**{self.current}** tried to use their **axe**, but they missed and hit a tree. Perhaps this is not what the axe is meant for."
            else:
                damage = random.randint(20,30)
                description = f"**{self.current}** used their **axe**, and landed a powerful hit! They dealt `{damage}` to **{self.oppose}**"
            await self.process_action(interaction,damage,0,0,description)
        elif button.label == "Armor":
            if failrate <= 10:
                defense = 0
                description = f"**{self.current}** tried to put some **armove** on, but the armor was too big lol."
            else:
                defense = random.randint(5,15)
                description = f"**{self.current}** put on some **armove**, and improved their defense by `{defense}`"
            await self.process_action(interaction,0,0,defense,description)
        elif button.label == "Crossbow":
            if failrate <= 5:
                damage = 0
                description = f"**{self.current}** tried to use their **crossbow**, but they missed a hit an apple on a tree. They thought it was a reliable weapon though..."
            else:
                damage = random.randint(25,35)
                description = f"**{self.current}** aimed and hit a shot with their **crossbow**, desling `{damage}` **{self.oppose}**"
            await self.process_action(interaction,damage,0,0,description)
        elif button.label == "Rocket Launcher":
            if failrate <= 45:
                kickback = random.randint(20,30)
                damage = 0
                description = f"**{self.current}** tried to use their **rocket launcher**, but they it blew up in their face, dealing `{kickback}`. Karma hurts, doesn't it?"
            else:
                kickback = 0
                damage = random.randint(40,60)
                description = f"**{self.current}** launched their rocket, and it blew up next to **{self.oppose}**! The explosion dealt `{damage}`, is this weapon broken?"
            await self.process_action(interaction,damage,kickback,0,description)
        
    @ui.button(label= 'End Fight', style=discord.ButtonStyle.gray,row = 0)
    async def end(self, interaction, button):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(f"**{interaction.user}** ended the fight! What a coward.",view=self) 
        await interaction.response.send_message(embed = discord.Embed(description = f"**{interaction.user}** ended the fight! What a coward.",color = discord.Color.red()))
        self.stop()
    


class Items(ui.Select):
    def __init__(self,users):
        options = [
            discord.SelectOption(label='No Item', description='No Item? No problem. You got this.', emoji='❌'),
            discord.SelectOption(label='Shield (Passive)', description='With this trust shield, you can block your opponents attack.', emoji='<:PB_shield:865758696579006495>'),
            discord.SelectOption(label='Potion (Passive)', description='Less damage taken by all hits.', emoji='<:PB_potion:865758671313174549>'),
            discord.SelectOption(label='Clover (Passive)', description='With luck on your side, you are more likely to suceed.', emoji='<:PB_clover:865759726961033288>'),
            discord.SelectOption(label='Sword (Active)', description='A fairly risky weapon, with high damage.', emoji='<:PB_sword:865758905220202506>'),
            discord.SelectOption(label='Axe (Active)', description='A decent weapon, with decent damage. What else?', emoji='<:PB_axe:865758717004742706>'),
            discord.SelectOption(label='Armor (Active)', description='Instead of attacking, put on some armor!', emoji='<:PB_armor:865759592259256361>'),
            discord.SelectOption(label='Crossbow (Active)', description='A reliable ranged weapon, only for the worthy.', emoji='<:PB_crossbow:878828750811312138>'),
            discord.SelectOption(label='Rocket Launcher (Active)', description='A weapon ahead of its time, but where to get one?', emoji='<:PB_rocketlauncher:878829510294925362>'),
        ]
        self.message = None
        self.chosen = [None,None]
        self.confirmed = [None,None]
        self.users = users

        super().__init__(placeholder='Choose a weapon now...', min_values=1, max_values=1, options=options,row = 0)
    
    async def updateembed(self):
        embed = self.message.embeds[0]
        embed.remove_field(2)
        if self.confirmed[0]:
            status1 = "✅"
        else:
            status1 = "<a:OB_Loading:907101653692456991>"
        if self.confirmed[1]:
            status2 = "✅"
        else:
            status2 = "<a:OB_Loading:907101653692456991>"
        
        embed.add_field(name = "Chosen Items",value = f"{status1} **{self.users[0]}**: {self.chosen[0]}\n{status2} **{self.users[1]}**: {self.chosen[1]}",inline = False)
        await self.message.edit(embed = embed)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.users[0]:
            if self.confirmed[0]:
                return await interaction.response.send_message(embed = discord.Embed(description = "You have already confirmed your choice!",color = discord.Color.red()),ephemeral = True)
            self.chosen[0] = self.values[0]
        elif interaction.user == self.users[1]:
            if self.confirmed[1]:
                return await interaction.response.send_message(embed = discord.Embed(description = "You have already confirmed your choice!",color = discord.Color.red()),ephemeral = True)
            self.chosen[1] = self.values[0]
        else:
            return
        await self.updateembed()
        await interaction.response.defer()

class DropdownView(discord.ui.View):
    def __init__(self,users):
        super().__init__(timeout=60)
        # Adds the dropdown to our view object.
        self.message = None
        self.items = Items(users)
        self.add_item(self.items)
        self.users = users

    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        await self.message.channel.reply(embed = discord.Embed(description = "Your fight timed out, sad",color = discord.Color.red()))
    
    @ui.button(label='✅ Confirm', style=discord.ButtonStyle.green,row = 1)
    async def confirm(self, interaction, button):
        if interaction.user == self.users[0]:
            if self.items.chosen[0] == None:
                return await interaction.response.send_message(embed = discord.Embed(description = "You must select an item before confirming!",color = discord.Color.red()),ephemeral = True)
            self.items.confirmed[0] = True
        elif interaction.user == self.users[1]:
            if self.items.chosen[1] == None:
                return await interaction.response.send_message(embed = discord.Embed(description = "You must select an item before confirming!",color = discord.Color.red()),ephemeral = True)
            self.items.confirmed[1] = True
        await interaction.response.defer()
        await self.items.updateembed()
        
        if self.items.confirmed[0] and self.items.confirmed[1]:
            for child in self.children: 
                child.disabled = True   
            await self.message.edit(view=self) 
            self.stop()

class Confirm(ui.View):
    def __init__(self,user):
        super().__init__(timeout=60)
        self.ctx = None
        self.message = None
        self.user = user
        self.value = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.user

    @ui.button(emoji='✅', style=discord.ButtonStyle.green)
    async def accept(self, interaction, button):
        await interaction.response.defer()
        self.value = True
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()
        

    @ui.button(emoji='✖', style=discord.ButtonStyle.red)
    async def reject(self, interaction, button):
        await interaction.response.defer()
        self.value = False
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()

async def setup(client):
    await client.add_cog(Fight(client))
