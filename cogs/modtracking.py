import discord
from itertools import starmap, chain
from discord.ext import commands, menus
from discord import ui
import firebase_admin
from firebase_admin import db
import datetime

if not 'modtracking' in firebase_admin._apps:
    cred_obj = firebase_admin.credentials.Certificate('modtracking-dc79b-firebase-adminsdk-dhnil-6e2c14fbb0.json')
    default_app = firebase_admin.initialize_app(cred_obj , {
        'databaseURL':'https://modtracking-dc79b-default-rtdb.firebaseio.com/'
        },name="modtracking")

class ModTracking(commands.Cog):
    """
        Tracking mod actions, are your mods slacking? This will allow mods to log their actions so you can view them. Includes a cool leaderboard to see how you stack up against the other mods.
        \n**Setup for this Category**
        Mod Tracking Role: `o!settings add modtrack <role>` 
    """
    def __init__(self,client):
        self.client = client
        self.short = "<:modbadge:949857487341879396> | Mod Tracking"
    
    def modtrack_role_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            modroles = ref.child(str(ctx.message.guild.id)).child('modtrack').get()
            if modroles == None:
                return False
            for role in modroles:
                role_ob = ctx.message.guild.get_role(role)
                if role_ob in ctx.message.author.roles:
                    return True
            else:
                return False
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Mod Traking Cog Loaded.')

    async def post_log(self,ctx,channel,action):
        emb = discord.Embed(title=f"Mod Action Recorded for {ctx.message.author.name}",description = f"{ctx.message.author.mention}",
                                color=discord.Color.green())

        emb.add_field(name = "Action Recorded:",value = f"[Link to Command]({ctx.message.jump_url})\nAction Details: {action}")

        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'Oasis Bot Mod Logging',icon_url = ctx.message.channel.guild.icon)

        await channel.send(embed = emb)

    async def remove_data(self,ctx,member):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        ref.child(str(ctx.guild.id)).child(str(member)).delete()
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Removed mod tracking data for <@{member}>',color = discord.Color.green())
        await ctx.reply(embed = embed)
        return True

    async def pull_data(self,guild,member):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        modtracking = ref.child(str(guild)).child(str(member)).get()
        modtracking.reverse()
        return modtracking

    async def set_data(self,ctx,guild,member,action):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        modtracking = ref.child(str(guild)).child(str(member)).get()

        if modtracking == None:
            modtracking = []

        now = datetime.datetime.now()
        formatnow = str(now.month) + "-" + str(now.day) + "-" + str(now.year) + " " + str(now.hour) + ":" + str(now.minute)

        modtracking.append([action,formatnow])

        ref.child(str(guild)).child(str(member)).set(modtracking)

        ref = db.reference("/",app = firebase_admin._apps['settings'])
        logchannel = ref.child(str(ctx.message.guild.id)).child('mlogging').get()
        if logchannel:
            channel = ctx.guild.get_channel(logchannel)
            if channel:
                await self.post_log(ctx,channel,action)

    async def pull_leaderboard(self,guild):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        guildtracking = ref.child(str(guild)).get()

        build = {}
        if not guildtracking:
            return [],build
        for person in guildtracking:
            build[person] = len(guildtracking[person])

        return sorted(build, key=build.get, reverse=True) , build

    async def edit_log(self,ctx,guild,member,index,action):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        modtracking = ref.child(str(guild)).child(str(member)).get()
        index = int(index)

        try:
            edit = modtracking[index-1]
            edit[0] = action
            modtracking[index-1] = edit
        except:
            return await ctx.send("Does not look like that is a valid index.")

        ref.child(str(guild)).child(str(member)).set(modtracking)
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully Edited **{index}** to **{action}**!',color = discord.Color.green())
        await ctx.reply(embed = embed)

    async def remove_log(self,ctx,guild,member,index):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        modtracking = ref.child(str(guild)).child(str(member)).get()
        index = int(index)

        try:
            modtracking.pop(index-1)
        except:
            return await ctx.send("Does not look like that is a valid index.")

        ref.child(str(guild)).child(str(member)).set(modtracking)
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully Removed action **{index}**!',color = discord.Color.green())
        return await ctx.reply(embed = embed)

    @commands.command(help = "Log an action that you have completed")
    @modtrack_role_check()
    async def logaction(self,ctx,*,action):
        await self.set_data(ctx,ctx.guild.id,ctx.message.author.id,action)
        embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully logged **{action}**!",color = discord.Color.green())
        await ctx.reply(embed = embed)

    @commands.group(help = "Some shortcuts for `[prefix]logaction`")
    async def log(self,ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a shortcut!\nUse `[prefix]help log` to see what you can log.",color = discord.Color.red())
            await ctx.reply(embed = embed)
    
    @log.command(help = "Log alt blacklist")
    async def alt(self,ctx,*,ids):
        await self.set_data(ctx,ctx.guild.id,ctx.message.author.id,f"Blacklisted Alt: {ids}")
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully logged alt blacklist of  **{ids}**!',color = discord.Color.green())
        await ctx.reply(embed = embed)

    @log.command(help = "Log freeloader ban")
    async def free(self,ctx,*,ids):
        await self.set_data(ctx,ctx.guild.id,ctx.message.author.id,f"Banned for Freeloading: {ids}")
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully logged freeloder ban of  **{ids}**!',color = discord.Color.green())
        await ctx.reply(embed = embed)

    @log.command(help = "Log donation role/managerment")
    async def dono(self,ctx,*,ids):
        await self.set_data(ctx,ctx.guild.id,ctx.message.author.id,f"Did donations for: {ids}")
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully logged donations for  **{ids}**!',color = discord.Color.green())
        await ctx.reply(embed = embed)

    @commands.command(help = "Edit an action that you had, with the index of the action")
    @modtrack_role_check()
    async def editaction(self,ctx,index,*,action):
        await self.edit_log(ctx,str(ctx.guild.id), str(ctx.message.author.id),index, action)

    @commands.command(help =  "Remove one of your logs")
    @modtrack_role_check()
    async def removeaction(self,ctx,index):
        await self.remove_log(ctx,str(ctx.guild.id),str(ctx.message.author.id),index)

    @commands.command(help =  "Remove all mod tracking data for a member")
    @commands.has_permissions(administrator= True)
    async def removeactiondata(self,ctx,member:discord.Member):
        await self.remove_data(ctx,member.id)

    @commands.command(help = "Shows the amount of logs you or another person has")
    @modtrack_role_check()
    async def actionamount(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        logs = await self.pull_data(ctx.guild.id,member.id)
        embed=discord.Embed(description=f"{member.mention}: `{len(logs)}` actions logged", color=discord.Color.random())
        await ctx.reply(embed=embed)
    
    @commands.command(help = "View the details of logged actions")
    @modtrack_role_check()
    async def actiondetail(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        logs = await self.pull_data(ctx.guild.id,member.id)
        formatter = ModPageSource(member, logs)
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(ctx)
    
    @commands.command(aliases = ['modlb','mlb'],help = "Show the mod actions leaderboard")
    @modtrack_role_check()
    async def mleaderboard(self,ctx):
        users,log = await self.pull_leaderboard(ctx.guild.id)
        formatter = ModLBPageSource(users, log)
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(ctx)
    
class MyMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source, *, delete_message_after=False):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.message)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value
    
    async def send_initial_message(self, ctx, message):
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await message.reply(**kwargs)
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author

    @ui.button(emoji='<:doubleleft:930948763885899797>', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_page(0)

    @ui.button(emoji='<:arrowleft:930948708458172427>', style=discord.ButtonStyle.blurple)
    async def before_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page - 1)

    @ui.button(emoji='<:arrowright:930948684718432256>', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page + 1)

    @ui.button(emoji='<:doubleright:930948740557193256>', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_page(self._source.get_max_pages() - 1)
    
    @ui.button(label='End Interaction', style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction, button):
        await interaction.response.defer()
        self.stop()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

class ModPageSource(menus.ListPageSource):
    def __init__(self,user,logs):
        super().__init__(logs,per_page=9)
        self.user = user
        self.amount = len(logs)
    def format_action_detail(self,no, log):
        return f"{log[1]}\n{log[0]}"
    async def format_page(self,menu,logs):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_action_detail, enumerate(logs, start=starting_number))
        embed = discord.Embed(title = f"Mod Action Details for {self.user}",description = f"`{self.amount} Actions Logged`",color = discord.Color.random())
        for count,item in enumerate(iterator):
            embed.add_field(name = f"Action {self.amount-(count + starting_number) + 1}",value = item)
        embed.set_footer(text=f"Use the buttons below to navigate pages! | Page {page + 1}/{max_page}") 
        return embed

class ModLBPageSource(menus.ListPageSource):
    def __init__(self, data, log):
        super().__init__(data, per_page=10)
        self.log = log
    def format_leaderboard_entry(self, no, user):
        return f"**{no}. <@{user}>** `{self.log[user]} Actions Logged`"
    async def format_page(self, menu, users):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_leaderboard_entry, enumerate(users, start=starting_number))
        page_content = "\n".join(iterator)
        embed = discord.Embed(
            title=f"Mod Tracking Leaderboard [{page + 1}/{max_page}]", 
            description=page_content,
            color= discord.Color.random()
        )
        embed.set_footer(text=f"Use the buttons below to navigate pages!") 
        return embed


async def setup(client):
    await client.add_cog(ModTracking(client))