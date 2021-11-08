import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption, Interaction
import datetime
import math
import firebase_admin
from firebase_admin import db
import random
import asyncio

class War(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.war_registering = {}
        self.war_item_choosing = {}
        self.war_items = {}
        self.war_active = {}
        self.war_stats = {}
        self.button_menus = {}
        self.cooldown_brrr = {}
        self.debuff_bypass = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print('War Cog Loaded.')

    @commands.Cog.listener()
    async def on_button_click(self,interaction: Interaction):
        if (interaction.message.id) in self.war_registering:
            if interaction.component.label == "Register":
                if interaction.user.id in self.war_registering[(interaction.message.id)]:
                    return await interaction.respond(content = "You already registered for this war! Please wait for the battle to start.")
                elif len(self.war_registering[(interaction.message.id)]) >= 10:
                    return await interaction.respond(content = "The maximum limit for this battle has been reached! Please try again another time.")
                self.war_registering[(interaction.message.id)].append(interaction.user.id)
                await interaction.respond(content = "Thank you for registering! Good luck.")
            elif interaction.component.label == "Instructions":
                embed = discord.Embed(title = "Oasis Bot War Command Help",description = "Fight to the death! The last one who is standing wins!")
                embed.add_field(name = "Choose an Item!",value = "Before the battle, you will choose an item. This item can be either passive or active, and you can use it to aid you in your battle!",inline = False)
                embed.add_field(name = "Select a Player",value = "Once the war starts, you will be presented with a select menu of players. Select one to hit, and the bot will respond with an embed showing your opponent's statistics. From there, take action with the buttons on that embed!" + 
                    "\nNote that you must select another player after every hit, and there is a cooldown period of 5 seconds after each hit. To select the same player, you must first select the reset option, and then the same player again! Targeting the same player more than once will grant you a debuff of 20 percent on your damage to that player.",inline = False)
                embed.add_field(name = "Statistics Embed",value = "Every 3 seconds, an embed will be updated showing all player stats, including their health, defense, and last affected action. Use this to figure out who to target next!",inline = False)
                embed.add_field(name= "Eliminated?",value = "If the statistics embed shows you are out, then the game is over for you! Sit back and watch while the rest of the players battle it out.",inline = False)
                embed.set_footer(text = "Hope you enjoy! Get ready to select your weapon.")
                await interaction.respond(embed = embed)

    @commands.Cog.listener()
    async def on_select_option(self,interaction:Interaction):
        if (interaction.message.id) in self.war_item_choosing:
            if interaction.user.id in self.war_item_choosing[interaction.message.id]:
                self.war_items[(interaction.message.id)][(interaction.user.id)] = interaction.values[-1]
                await interaction.respond(content = f"You chose {interaction.values[-1]}!")
            else:
                await interaction.respond(content = f"You did not register for this battle!")
        elif interaction.message.channel.id in self.war_active:
            if interaction.message.id == self.war_active[interaction.message.channel.id].id:
                if interaction.values[-1] == "reset":
                    return await interaction.respond(type = 6)
                if interaction.user.id in self.cooldown_brrr[interaction.message.channel.id]:
                    return await interaction.respond(content = "You are on cooldown! There is a 5 second cooldown imposed inbetween actions.")
                player_against = self.war_stats[interaction.message.channel.id][int(interaction.values[-1])]
                player = self.war_stats[interaction.message.channel.id][interaction.user.id]
                hp = player["hp"]
                if hp <= 0:
                    return await interaction.respond(content = "You are already eliminated!")
                defense = player["defense"]
                item = player["item"]
                player_name = player["name"]
                against_name = player_against["name"]
                against_hp = player_against["hp"]
                against_defense = player_against["defense"]
                against_item = player_against["item"]
                against_id = interaction.values[-1]
                if against_name == player_name:
                    return await interaction.respond(content = "Seems kind of dumb to target yourself, doesn't it?")
                if against_hp <= 0:
                    return await interaction.respond(content = "This person is already eliminated!")

                embed = discord.Embed(title = f"Taking action against: {against_name}",color = discord.Color.random())
                embed.add_field(name = player["name"],value = f"**Player Health:** `{hp}`\n**Player Defense:** `{defense}\n`**Player Item:** `{item}`")
                embed.add_field(name = against_name,value = f"**Player Health:** `{against_hp}`\n**Player Defense:**`{against_defense}\n`**Player Item:** `{against_item}`")
                

                if not self.debuff_bypass[interaction.message.channel.id] and player.get("prevtar","") == against_name:
                    embed.set_footer(text = "You have 20 seconds to choose! | Note that since you are targeting the same person, your damage is debuffed by 20 percent.")
                    debuff = True
                else:
                    embed.set_footer(text = "You have 20 seconds to choose!")
                    debuff = False

                message = await interaction.send(embed = embed,components = [self.button_menus[interaction.message.channel.id][interaction.user.id]])
                await interaction.respond(type = 6)

                def check(i):
                    if i.message.id == message.id:
                        return True
                    else:
                        return False

                try:
                    interaction = await self.client.wait_for("button_click", timeout = 20.0,check = check)
                except asyncio.TimeoutError:
                    await message.edit("Well you took too long to respond. Go back to the selects menu to get someone else.",components = None)
                    return

                choice = interaction.component.label
                failmax = 101
                if item == "Clover":
                    failmax = 350

                failrate = random.randint(1,failmax)
                fail = False
                knockback = 0
                damage = 0
                buffdef = 0
                description = ""
                if choice == "Sword":
                    damage = random.randint(30,40)
                    if failrate <= 40:
                        fail = True
                        description = f"**{player_name}** tried to use their sword on **{against_name}**, but they missed the stab!"
                elif choice == "Axe":
                    damage = random.randint(20,30)
                    if failrate <= 25:
                        fail = True
                        description = f"**{player_name}** tried to use their axe on **{against_name}**, but they hit a tree instead. How unfortunate"
                elif choice == "Punch":
                    damage = random.randint(5,15)
                    if failrate <= 5:
                        fail = True
                        description = f"**{player_name}** tried to punch **{against_name}**, but somehow they missed! How unlucky."
                elif choice == "Smack":
                    damage = random.randint(10,30)
                    if failrate <= 20:
                        fail = True
                        description = f"**{player_name}** tried smack **{against_name}** but missed the opponent. Someone needs a lesson in smacking"
                elif choice == "Kick":
                    damage = random.randint(30,50)
                    if failrate <= 50:
                        fail = True
                        knockback = random.randint(5,20)
                        description = f"**{player_name}** tried to kick **{against_name}** but failed and fell down! \nThis caused **{player_name}** to suffer `{knockback}` points of damage!"
                elif choice == "Armor":
                    buffdef = random.randint(15,40)
                    description = f"**{player_name}** used a bit of armor! They protect themselves, increasing their defense by `{buffdef}`"
                

                if against_item == "Shield" and damage > 0:
                    shield = random.randint(1,100)
                    if shield <= 25:
                        description = description or f"**{player_name}** had a successful hit of `{damage}` damage, however {against_name}'s `shield` blocked the hit!"
                if fail:
                    hp = player["hp"]
                    hp -= knockback
                else:
                    if against_item == "Potion":
                        realdamage = int(damage * 0.8)
                        description = description or f"**{player_name}** used `{choice}` against **{against_name}**! It caused their opponent to take `{realdamage}` damage after {against_name}'s `potion` effect!"
                    elif against_item == "Armor":
                        realdamage = int(damage * (1-(against_defense/100)))
                        description = description or f"**{player_name}** used `{choice}` against **{against_name}**! It caused their opponent to take `{realdamage}` damage after {against_name}'s `armor`!"
                    else:
                        realdamage = damage
                    defense += buffdef

                    against_hp = player_against["hp"]
                    if not debuff:
                        against_hp -= realdamage
                    else:
                        against_hp -= int(realdamage * 0.8)

                    if defense > 100:
                        defense = 100
                    
                if description == "":
                    description = f"**{player_name}** used `{choice}` against **{against_name}**! It caused their opponent to take `{damage}` damage!"

                if against_hp <= 0:
                    against_hp = 0
                if hp  <= 0:
                    hp = 0
                
                embed = discord.Embed(title = f"Taking action against: {against_name}",description = description,color = discord.Color.random())
                embed.add_field(name = player["name"],value = f"**Player Health:** `{hp}`\n**Player Defense:** `{defense}\n`**Player Item:** `{item}`")
                embed.add_field(name = against_name,value = f"**Player Health:** `{against_hp}`\n**Player Defense:**`{against_defense}\n`**Player Item:** `{against_item}`")
                
                if debuff:
                    embed.set_footer(text = "Now, go select someone else to target! | A 20 percent debuff was applied to your damage, since you targeted the same person more than once.")
                else:
                    embed.set_footer(text = "Now, go select someone else to target!")
                player_against["hp"] = against_hp
                player_against["defense"] = against_defense
                player_against["latest"] = description
                self.war_stats[interaction.message.channel.id][int(against_id)] = player_against

                player["hp"] = hp
                player["defense"] = defense
                player["latest"] = description
                player["prevtar"] = against_name
                self.war_stats[interaction.message.channel.id][interaction.user.id] = player

                await interaction.edit_origin(embed = embed, components = [])

                self.cooldown_brrr[interaction.message.channel.id].append(interaction.user.id)

                await asyncio.sleep(5)

                self.cooldown_brrr[interaction.message.channel.id].remove(interaction.user.id)


    async def generate_stats_embed(self,ctx,message):
        while self.war_active.get(ctx.channel.id,False):
            alive = 0
            embed = discord.Embed(title = "Current Statistics",color = discord.Color.random())
            for player in self.war_stats[ctx.channel.id]:
                player = self.war_stats[ctx.channel.id][player]
                hp = player["hp"]
                if hp <= 0:
                    hp = "Eliminated <a:PB_eliminated:881701893305425980>"
                else:
                    hp = "`" + str(hp) + "`"
                    alive += 1
                defense = player["defense"]
                latest = player.get("latest","No action taken against yet!")
                embed.add_field(name = player["name"],value = f"**Player Health:** {hp}\n**Player Defense:** `{defense}`\n**Latest Change:** {latest}",inline = False)
            await message.edit(embed = embed)
            if alive == 1:
                self.war_active.pop(ctx.channel.id)
                break
            elif alive == 2:
                self.debuff_bypass[ctx.channel.id] = True
            await asyncio.sleep(3)
        winner = None
        for player in self.war_stats[ctx.channel.id]:
            if self.war_stats[ctx.channel.id][player]["hp"] > 0:
                winner = player
                break
        if not winner:
            return await ctx.send("Something really fucked up, and I can't find a winner!")
        embed = discord.Embed(title = "🏆 The war is over! 💥",description = f"The last one standing was <@{player}>!",color = discord.Color.gold())
        await ctx.send(embed = embed)

        self.war_stats.pop(ctx.channel.id)
        self.button_menus.pop(ctx.channel.id)


    @commands.command(description = "Let's go to war! Up to 10 players can play in this gamemode.",help = "war",brief = "Open up a battle for multiple people!")
    async def war(self,ctx):
        embed = discord.Embed(title = f"{ctx.author} is starting a war",description = "Click the button below to register! This battle automatically begin setup in 30 seconds, this server has a battle limit of `10` players.",color = discord.Color.red())

        message = await ctx.send(embed = embed,components = [[Button(label = "Register",style = 4),Button(label = "Instructions",style = 3)]])
        self.war_registering[message.id] = []

        await asyncio.sleep(30)

        players = self.war_registering.pop((message.id))

        if len(players) <= 1:
            embed = discord.Embed(title = f"{ctx.author} is starting a war",description = f"Well, only one or zero people showed up! Cancelling war...",color = discord.Color.red())
            return await message.edit(embed = embed,components = [Button(label = "Register",style = 4,disabled = True)])
        embed = discord.Embed(title = f"{ctx.author} is starting a war",description = f"Registration is now over! Setting up with `{len(players)}` players!",color = discord.Color.red())

        await message.edit(embed = embed,components = [[Button(label = "Register",style = 4,disabled = True),Button(label = "Instructions",style = 3,disabled = True)]])

        async with ctx.typing():
            playerdict = {}

            for player in players:
                playerdict[player] = {}
                playerdict[player]['object'] = ctx.guild.get_member(int(player))

            selectslist = [
                SelectOption(value = "Shield",label = "Shield (passive)",description = "Gives chance to block your opponent's attack.",emoji = self.client.get_emoji(865758696579006495)),
                SelectOption(value = "Clover",label = "Clover (passive)",description = "A higher chance to have a successful hit.",emoji = self.client.get_emoji(865759726961033288)),
                SelectOption(value = "Potion",label = "Potion (passive)",description = "Less damage taken by all hits.",emoji = self.client.get_emoji(865758671313174549)),
                SelectOption(value = "Sword",label = "Sword (active)",description = "High damage but a high chance of failure.",emoji = self.client.get_emoji(865758905220202506)),
                SelectOption(value = "Axe",label = "Axe (active)",description = "Medium damage, but a less chance of fail against sword.",emoji = self.client.get_emoji(865758717004742706)),
                SelectOption(value = "Armor",label = "Armor (active)",description = "Opens option to defend, decreases the atk from attacker.",emoji = self.client.get_emoji(865759592259256361)),
                ]

            embed = discord.Embed(title = f"The war is beginning!",description = f"But first, you have to choose your weapon. Use the selects list below to choose now! If you do not select, you will use the default attacks. You have 30 seconds.",color = discord.Color.orange())
            embed.add_field(name = "Passive Items",value = "These items give passive boosts, meaning that they are active during the entire fight.")
            embed.add_field(name = "Active Items",value = "These items open up an option during the fight, depending on what you choose. Using these items will be your turn in the fight.")
            message = await ctx.send(embed = embed,components = [Select(options =selectslist)])
            self.war_item_choosing[message.id] = players
            build = {}
            for player in players:
                build[player] = None
            self.war_items[message.id] = build

        await asyncio.sleep(30)

        self.war_item_choosing.pop(message.id)
        items = self.war_items.pop((message.id))
        async with ctx.typing():
            embed = discord.Embed(title = f"Setting up!",description = f"Selection time is up! Completing setup now, please wait...",color = discord.Color.green())
            await message.edit(embed = embed,components = [Select(options =selectslist,disabled = True)])

            targetselects = [SelectOption(value = "reset",label = f"Reset Select (Hit Same Person)",description = "If you want to hit the same person, pick this first.")]
            buttonmenus = {}
            self.war_stats[ctx.channel.id] = {}

            for player in players:
                member = ctx.guild.get_member(int(player))
                targetselects.append(SelectOption(value = player,label = f"{member}"))
                buttons = []
                buttons.append(Button(label = "Punch",style = 3))
                buttons.append(Button(label = "Smack",style = 3))
                buttons.append(Button(label = "Kick",style = 3))
                
                if items[(player)]:
                    if items[player] in ["Sword","Axe","Armor"]:
                        buttons.append(Button(label = items[(player)],style = 3))
                buttonmenus[player] = buttons

                self.war_stats[ctx.channel.id][int(player)] = {"hp":100,"defense":0,"name":str(member),"item":items[player]}
                #await ctx.send(str(self.war_stats))
            self.button_menus[ctx.channel.id] = buttonmenus
            self.cooldown_brrr[ctx.channel.id] = []

        await message.delete()

        embed = discord.Embed(title = f"Setup Complete!",description = f"In 10 seconds, an embed will have a selects menu with all players. Pick one to target, and take action against them! Last one standing wins.",color = discord.Color.green())

        message = await ctx.send(embed = embed)

        await asyncio.sleep(10)
        await message.delete()
        embed = discord.Embed(title = "Current Statistics",color = discord.Color.random())
        for player in self.war_stats[ctx.channel.id]:
            player = self.war_stats[ctx.channel.id][player]
            hp = player["hp"]
            if hp <= 0:
                hp = "Eliminated <a:PB_eliminated:881701893305425980>"
            defense = player["defense"]
            latest = player.get("latest","No action taken against yet!")
            embed.add_field(name = player["name"],value = f"**Player Health:** `{hp}`\n**Player Defense:** `{defense}`\n**Latest Change:** {latest}",inline = False)
        message1 = await ctx.send(embed = embed)

        embed = discord.Embed(title = f"It's War Time!",description = f"Use the selects below to target another player! The last player standing wins!\nWant to target the same person again? Reset the select first.",color = discord.Color.green())
        message = await ctx.send(embed = embed,components = [Select(options =targetselects)])
        self.war_active[ctx.channel.id] = message
        self.debuff_bypass[ctx.channel.id] = False

        await self.generate_stats_embed(ctx,message1)
    
def setup(client):
    client.add_cog(War(client))