import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import db
import datetime
import asyncio
import random
import time
from discord import ui

battles = {}

class War(commands.Cog):
    '''
        A fun multiplayer game
        \n**Setup for this Category**
        Invite Log: `o!settings set invitelog <channel>` 
    '''
    def __init__(self, client):
        self.short = "⚔ | War"
        self.client = client

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
    
    @commands.command(help = "Start a fun multiplayer battle game!")
    @eman_role_check()
    async def war(self,ctx):
        if ctx.channel.id in battles:
            return await ctx.reply(embed = discord.Embed(description = "There is an ongoing war in this channel!",color = discord.Color.red()))
        battles[ctx.channel.id] = None
        players = []
        embed = discord.Embed(title = "Sign up for war!",description = "Click the button below to sign up!",color = discord.Color.random())
        embed.set_footer(text = "30 seconds to sign up")
        view = SignUp()
        message = await ctx.send(embed = embed,view = view)
        await asyncio.sleep(7)
        view.stop()
        view.children[0].disabled = True
        await message.edit(view = view)
        players = view.value
        if len(players) <= 1:
            battles.pop(ctx.channel.id)
            return await message.reply(embed = discord.Embed(description = "There were below one signups for the war! Cancelling event...",color = discord.Color.red()))
        
        view = DropdownView(players)
        embed = discord.Embed(title = "Now it is time to choose your item!",color = discord.Color.random())
        embed.add_field(name = "Passive Items",value = "These items give passive boosts, meaning that they are active during the entire fight.")
        embed.add_field(name = "Active Items",value = "These items open up an option during the fight, depending on what you choose. Using these items will be your turn in the fight.")
        embed.set_footer(text = "You have 30 seconds to make a decision!")
        res = "__**Chosen Items**__\n"
        for player in players:
            res += f"**{player}:** None\n"
        embed.description = res
        message = await ctx.send(embed = embed,view = view)
        view.children[0].message = message
        await asyncio.sleep(10)
        view.stop()
        view.children[0].disabled = True
        await message.edit(view = view)
        dplayers = view.children[0].players
        battles[ctx.channel.id] = [dplayers,list(players.keys()),[]]
        view = Selection(players)
        embed = discord.Embed(title = "Current War Statistics",description = "Real time stats updated below every 3 seconds!",color = discord.Color.random())
        for player,data in battles[ctx.channel.id][0].items():
            if data['hp'] > 0:
                embed.add_field(name = player,value = f"**Current Health:** `{data['hp']}`\n**Current Defense:** `{data['def']}`\n**Selected Item:** `{data['item']}`\n**Latest Action:** {data['latest']}",inline = False)
            else:
                embed.add_field(name = player,value = f"**Current Health:** <a:PB_eliminated:881701893305425980> Eliminated!`\n**Current Defense:** `{data['def']}`\n**Selected Item:** `{data['item']}`\n**Latest Action:** {data['latest']}",inline = False)
        message = await ctx.send(embed = embed,view = view)
        while True:
            if len(battles[ctx.channel.id]) > 3:
                view.children[0].disabled = True
                battles.pop(ctx.channel.id)
                await message.edit(view = view)
                return
            embed.clear_fields()
            for player,data in battles[ctx.channel.id][0].items():
                if data['hp'] > 0:
                    embed.add_field(name = player,value = f"**Current Health:** `{data['hp']}`\n**Current Defense:** `{data['def']}`\n**Selected Item:** `{data['item']}`\n**Latest Action:** {data['latest']}",inline = False)
                else:
                    embed.add_field(name = player,value = f"**Current Health:** <a:PB_eliminated:881701893305425980> Eliminated!\n**Current Defense:** `{data['def']}`\n**Selected Item:** `{data['item']}`\n**Latest Action:** {data['latest']}",inline = False)
            embed.color = discord.Color.random()
            if len(battles[ctx.channel.id][1]) <= 1:
                break
            view = Selection(battles[ctx.channel.id][1])
            await message.edit(embed = embed,view = view)
            await asyncio.sleep(3)
        embed = discord.Embed(title = "We have a winner!",description = f"{battles[ctx.channel.id][1][0].mention} was the last one standing!",color = discord.Color.gold())
        view.children[0].disabled = True
        await message.edit(embed = embed,view = view)
        await ctx.send(embed = embed)
        battles.pop(ctx.channel.id)
    
    @commands.command(help = "End the war game currently occuring in the channel. Will only work if the battle is ongoing.")
    @eman_role_check()
    async def abortwar(self,ctx):
        if battles.get(ctx.channel.id,False):
            battles[ctx.channel.id].append("abort")
            await ctx.reply(embed = discord.Embed(description = "Aborting the current battle in this channel...please wait.",color = discord.Color.green()))
        else:
            await ctx.reply(embed = discord.Embed(description = "I do not have a registered battle in this channel!",color = discord.Color.red()))

class SignUp(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 30)
        self.value = {}
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
    
    async def interaction_check(self, interaction):
        if interaction.user in self.value:
            await interaction.response.send_message(embed = discord.Embed(description = "You are already signed up!",color = discord.Color.red()),ephemeral = True)
            return False
        return True
    
    @ui.button(emoji='⚔', style=discord.ButtonStyle.green)
    async def sign_up(self, interaction, button):
        self.value[interaction.user] = {"item":None,"hp": 100,"def": 0,"latest":None}
        await interaction.response.send_message(embed = discord.Embed(description = "You are now signed up!",color = discord.Color.green()),ephemeral = True)

class Action(discord.ui.View):
    def __init__(self,attacker,defender):
        super().__init__(timeout=60)
        self.attacker = attacker
        self.defender = defender

    async def process_action(self,interaction, damage, kickback, defense, description):
        battles[interaction.channel_id][0][self.attacker]["hp"] -= kickback
        battles[interaction.channel_id][0][self.defender]["hp"] -= damage
        battles[interaction.channel_id][0][self.attacker]["def"] += defense
        battles[interaction.channel_id][0][self.attacker]["latest"] = description
        battles[interaction.channel_id][0][self.defender]["latest"] = description
        if battles[interaction.channel_id][0][self.attacker]["hp"] <= 0:
            battles[interaction.channel_id][0][self.attacker]["hp"] = 0
            battles[interaction.channel_id][1].remove(self.attacker)
            battles[interaction.channel_id][2].append(self.attacker)
            description += "\nYou are now eliminated! Thank you for playing."
        if battles[interaction.channel_id][0][self.defender]["hp"] <= 0 :
            battles[interaction.channel_id][0][self.defender]["hp"] = 0
            battles[interaction.channel_id][1].remove(self.defender)
            battles[interaction.channel_id][2].append(self.defender)
            description += "\nYour opponent is now eliminated!"
        
        embed = discord.Embed(title = f"Your turn against {self.defender}",description = f"Your turn was against {self.defender}",color = discord.Color.red())
        embed.add_field(name = self.attacker,value = f"**Current Health:** `{battles[interaction.channel_id][0][self.attacker]['hp']}`\n**Current Defense:** `{battles[interaction.channel_id][0][self.attacker]['def']}`\n**Selected Item:** `{battles[interaction.channel_id][0][self.attacker]['item']}`")
        embed.add_field(name = self.defender,value = f"**Current Health:** `{battles[interaction.channel_id][0][self.defender]['hp']}`\n**Current Defense:** `{battles[interaction.channel_id][0][self.defender]['def']}`\n**Selected Item:** `{battles[interaction.channel_id][0][self.defender]['item']}`")
        embed.add_field(name = "Action Result",value = description,inline = False)
        embed.set_footer(text = "Now choose someone else to target!")
        await interaction.response.edit_message(embed = embed,view = None)
    
    async def check_current(self,interaction):
        if battles[interaction.channel_id][0][self.attacker]["hp"] <= 0:
            await interaction.response.send_message(embed = discord.Embed(description = "You have been eliminated! You can no longer attack others.",color = discord.Color.red()),ephemeral = True)
            return False
        if battles[interaction.channel_id][0][self.defender]["hp"] <= 0:
            await interaction.response.send_message(embed = discord.Embed(description = "Your opponent was eliminated! Pick someone else to target.",color = discord.Color.red()),ephemeral = True)
            return False
        return True

    @ui.button(label= 'Punch',row = 0)
    async def punch(self, interaction, button):
        if not await self.check_current(interaction):
            return
        if battles[interaction.channel_id][0][self.attacker]["item"] == "Clover":
            failrate = random.randint(1,301)
        else:
            failrate = random.randint(1,101)
        
        if failrate <= 5:
            damage = 0
            description = f"**{self.attacker}** tried to use **punch**, but they failed! Tough luck."
        else:
            damage = random.randint(5,15)
            description = f"**{self.attacker}** uses **punch**, dealing `{damage}` to **{self.defender}**"
        await self.process_action(interaction,damage,0,0,description)

    @ui.button(label= 'Smack',row = 0)
    async def smack(self, interaction, button):
        if not await self.check_current(interaction):
            return
        if battles[interaction.channel_id][0][self.attacker]["item"] == "Clover":
            failrate = random.randint(1,301)
        else:
            failrate = random.randint(1,101)
        
        if failrate <= 20:
            damage = 0
            description = f"**{self.attacker}** tried to use **smack**, but they failed! Must suck to suck."
        else:
            damage = random.randint(10,30)
            description = f"**{self.attacker}** uses **smack**, dealing `{damage}` to **{self.defender}**"
        await self.process_action(interaction,damage,0,0,description)

    @ui.button(label= 'Kick',row = 0)
    async def kick(self, interaction, button):
        if not await self.check_current(interaction):
            return
        if battles[interaction.channel_id][0][self.attacker]["item"] == "Clover":
            failrate = random.randint(1,301)
        else:
            failrate = random.randint(1,101)
        
        if failrate <= 40:
            damage = 0
            kickback = random.randint(5,20)
            description = f"**{self.attacker}** tried to **kick**, but they failed and fell over instead, causing them to take `{kickback}` damage."
        else:
            damage = random.randint(30,40)
            kickback = 0
            description = f"**{self.attacker}** landed a powerful **kick**, dealing `{damage}` to **{self.defender}**"
        await self.process_action(interaction,damage,kickback,0,description)

    @ui.button(label= 'Item',row = 0)
    async def item(self, interaction, button):
        if not await self.check_current(interaction):
            return
        if battles[interaction.channel_id][0][self.attacker]["item"] == "Clover":
            failrate = random.randint(1,301)
        else:
            failrate = random.randint(1,101)
        
        if button.label == "Sword":
            if failrate <= 40:
                damage = 0
                description = f"**{self.attacker}** tried to use their **sword**, but they missed their parry. Perhaps they are missing some much-needed lessons."
            else:
                damage = random.randint(30,50)
                description = f"**{self.attacker}** used their **sword**, and landed a powerful parry! They dealt `{damage}` to **{self.defender}**"
            await self.process_action(interaction,damage,0,0,description)
        elif button.label == "Axe":
            if failrate <= 25:
                damage = 0
                description = f"**{self.attacker}** tried to use their **axe**, but they missed and hit a tree. Perhaps this is not what the axe is meant for."
            else:
                damage = random.randint(20,30)
                description = f"**{self.attacker}** used their **axe**, and landed a powerful hit! They dealt `{damage}` to **{self.defender}**"
            await self.process_action(interaction,damage,0,0,description)
        elif button.label == "Armor":
            if failrate <= 10:
                defense = 0
                description = f"**{self.attacker}** tried to put some **armove** on, but the armor was too big lol."
            else:
                defense = random.randint(5,15)
                description = f"**{self.attacker}** put on some **armove**, and improved their defense by `{defense}`"
            await self.process_action(interaction,0,0,defense,description)
        elif button.label == "Crossbow":
            if failrate <= 5:
                damage = 0
                description = f"**{self.attacker}** tried to use their **crossbow**, but they missed a hit an apple on a tree. They thought it was a reliable weapon though..."
            else:
                damage = random.randint(25,35)
                description = f"**{self.attacker}** aimed and hit a shot with their **crossbow**, desling `{damage}` **{self.defender}**"
            await self.process_action(interaction,damage,0,0,description)
        elif button.label == "Rocket Launcher":
            if failrate <= 45:
                kickback = random.randint(20,30)
                damage = 0
                description = f"**{self.attacker}** tried to use their **rocket launcher**, but they it blew up in their face, dealing `{kickback}`. Karma hurts, doesn't it?"
            else:
                kickback = 0
                damage = random.randint(40,60)
                description = f"**{self.attacker}** launched their rocket, and it blew up next to **{self.defender}**! The explosion dealt `{damage}`, is this weapon broken?"
            await self.process_action(interaction,damage,kickback,0,description)

class Players(discord.ui.Select):
    def __init__(self,players):
        options = []
        self.players = players
        for player in self.players:
            options.append(discord.SelectOption(label = str(player),value = player.id))
        super().__init__(placeholder='Choose a player now...', min_values=1, max_values=1, options=options,row = 0)
    
    async def callback(self, interaction: discord.Interaction):
        defender = interaction.guild.get_member(int(interaction.data["values"][0]))
        view = Action(interaction.user,defender)
        view.children[-1].label = battles[interaction.channel_id][0][interaction.user]["item"] or "None"
        if battles[interaction.channel_id][0][interaction.user]["item"] not in ["Sword","Axe","Armor","Crossbow","Rocket Launcher"]:
            view.children[-1].disabled = True
        embed = discord.Embed(title = f"Your turn against {defender}",description = f"Your are targeting {defender}",color = discord.Color.red())
        embed.add_field(name = interaction.user,value = f"**Current Health:** `{battles[interaction.channel_id][0][interaction.user]['hp']}`\n**Current Defense:** `{battles[interaction.channel_id][0][interaction.user]['def']}`\n**Selected Item:** `{battles[interaction.channel_id][0][interaction.user]['item']}`")
        embed.add_field(name = defender,value = f"**Current Health:** `{battles[interaction.channel_id][0][defender]['hp']}`\n**Current Defense:** `{battles[interaction.channel_id][0][defender]['def']}`\n**Selected Item:** `{battles[interaction.channel_id][0][defender]['item']}`")
        embed.set_footer(text = "Select an option below now! You have 60 seconds before the buttons timeout.")
        await interaction.response.send_message(embed = embed,view = view,ephemeral = True)
    
class Selection(discord.ui.View):
    def __init__(self,players):
        super().__init__(timeout = 90)
        self.add_item(Players(players))
        self.players = players
    
    async def interaction_check(self, interaction):
        if interaction.user in self.players and battles[interaction.channel_id][0][interaction.user]["hp"] > 0:
            return True
        else:
            return await interaction.response.send_message(embed = discord.Embed(description = "You are either not in this battle, or no longer alive!",color = discord.Color.red()),ephemeral = True)

class Items(discord.ui.Select):
    def __init__(self,players):
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
        self.players = players
        self.message = None
        super().__init__(placeholder='Choose a weapon now...', min_values=1, max_values=1, options=options,row = 0)
    
    async def updateembed(self):
        embed = self.message.embeds[0]
        res = "__**Chosen Items**__\n"
        for player,data in self.players.items():
            res += f"**{player}:** {data['item']}\n"
        embed.description = res
        await self.message.edit(embed = embed)

    async def callback(self, interaction: discord.Interaction):
        self.players[interaction.user]["item"] = " ".join(self.values[0].split()[:-1])
        await self.updateembed()
        await interaction.response.defer()

class DropdownView(discord.ui.View):
    def __init__(self,players):
        super().__init__()
        self.add_item(Items(players))
        self.players = players
    
    async def interaction_check(self, interaction):
        if interaction.user in self.players:
            return True
        return await interaction.response.send_message(embed = discord.Embed(description = "You are not signed up for this war!",color = discord.Color.red()))

async def setup(client):
    await client.add_cog(War(client))

