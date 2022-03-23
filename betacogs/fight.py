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
        Some fun commands! There are fun badges to unlock in this category, view yours using `o!profile`.
        \n**Setup for this Category**
        Giveaway Manager: `o!settings set giveawaymanager <role>` 
    """

    def __init__(self,client):
        self.client = client
        self.short = "🎈 | Fun Commands"
        self.fighters = []
    
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

        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)

        await ctx.reply(embed = emb)

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
    
    @commands.command(help = "Fight another user...for fun of couse.")
    async def fight(self,ctx,user:discord.Member):
        if ctx.author.id in self.fighters or user.id in self.fighters:
            return await ctx.reply(embed = discord.Embed(description = "Hold up, either you or your opponent is in a fight already. Take a chill pill and relax buddy.\nTip: Fight broke because of interaction? Try `[prefix]fixfight`!",color = discord.Color.red()))
        elif ctx.author.id == user.id:
            return await ctx.reply(embed = discord.Embed(description = "Hey, you can't fight yourself. Find another person to fight instead.",color = discord.Color.red()))
        elif user.bot:
            return await ctx.reply(embed = discord.Embed(description = "Hmmm...bots can't respond to your fight request. No free win for you.",color = discord.Color.red()))

        embed = discord.Embed(description = f"Hey **{user}**, **{ctx.author}** is challenging you to a fight! Do you accept?",color = discord.Color.random())
        view = Confirm(user)
        message = await ctx.reply(embed = embed,view = view)
        view.message = message
        timeout = await view.wait()
        if timeout:
            return await message.reply(embed = discord.Embed(description = "Seems your opponent did not respond. Try someone that isn't afk.",color = discord.Color.red()))
        if not view.value:
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
        await view.wait()
        await ctx.send("Done!")


class Items(ui.Select):
    def __init__(self,users):
        options = [
            discord.SelectOption(label='No Item', description='No Item? No problem. You got this.', emoji='❌'),
            discord.SelectOption(label='Shield (Passive)', description='With this trust shield, you can block your opponents attack.', emoji='<:PB_shield:865758696579006495>'),
            discord.SelectOption(label='Potion (Active)', description='Less damage taken by all hits.', emoji='<:PB_potion:865758671313174549>'),
            discord.SelectOption(label='Clover (Passive)', description='With luck on your side, you are more likely to suceed.', emoji='<:PB_clover:865759726961033288>'),
            discord.SelectOption(label='Sword (Active)', description='A fairly risky weapon, with high damage.', emoji='<:PB_sword:865758905220202506>'),
            discord.SelectOption(label='Axe (Active)', description='A decent weapon, with decent damage. What else?', emoji='<:PB_axe:865758717004742706>'),
            discord.SelectOption(label='Armor (Active)', description='Instead of attacking, put on some armor!', emoji='<:PB_armor:865759592259256361>'),
            discord.SelectOption(label='Crosssbow (Active)', description='A reliable ranged weapon, only for the worthy.', emoji='<:PB_crossbow:878828750811312138>'),
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
                return await interaction.response.send_message(embed = discord.Embed(description = "You have already confirmed your choice!",color = discord.Color.red()),emphemeral = True)
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
        self.add_item(Items(users))
        self.users = users

    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
    
    @ui.button(label='✅ Confirm', style=discord.ButtonStyle.green,row = 1)
    async def confirm(self, button, interaction):
        if interaction.user == self.users[0]:
            self.children[0].confirmed[0] = True
        elif interaction.user == self.users[1]:
            self.children[0].confirmed[1] = True
        await interaction.response.defer()
        await self.children[0].updateembed()
        
        if self.children[0].confirmed[0] and self.children[0].confirmed[1]:
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
    async def accept(self, button, interaction):
        self.value = True
        self.stop()

    @ui.button(emoji='✖', style=discord.ButtonStyle.red)
    async def reject(self, button, interaction):
        self.value = False
        self.stop()

def setup(client):
    client.add_cog(Fight(client))
