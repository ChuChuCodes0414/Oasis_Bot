import discord
from discord.ext import commands
import json
import firebase_admin
from firebase_admin import db
import asyncio
import datetime

class Help(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.cogs_short = {
            "channels":"Quick channel management commands.",
            "eventlogging":"Event manager logging, with leaderboard and event embeds.",
            "freeloader":"Checking for dank memer heist freeloaders.",
            "fun":"Fun commands, like fight and iq.",
            "invites":"Tracking invites and logging them.",
            "lottery":"Lottery/raffle for using dank memer items.",
            "mod":"Standard and simple mod commands.",
            "modtracking":"Tracking moderator's actions, with leaderboards and logging.",
            "music":"Simple music commands to play music in vc.",
            "privatechannels":"Private channel management for a private channel.",
            "settings":"Configure all aspects of the bot in your server.",
            "sniper":"Powerful snipe commands to see what is being deleted/edited.",
            "status":"Bot information commands.",
            "utility":"Server utility commands, like whois.",
            "winter":"❄ Winter drops of gingerbread!",
            "war":"Multiplayer fight, battle to the last one standing!"
        }
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Help Cog Loaded.')

    async def get_subcommand(self,subcommand,command):
        try:
            if command.walk_commands():
                for candidate in command.walk_commands():
                    if candidate.name == subcommand:
                        return candidate
            return False
        except:
            return False

    async def helpemb(self, ctx, input):
        dm = False
        # !SET THOSE VARIABLES TO MAKE THE COG FUNCTIONAL!
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        prefix = ref.child(str(ctx.message.guild.id)).child('prefix').get()
        version =  "Python 3.9.6, Discord.py 1.7.1"
        
        # setting owner name - if you don't wanna be mentioned remove line 49-60 and adjust help text (line 88) 
        owner = 	570013288977530880
        owner_name = 	"ChuGames#0001"

        input = input.split()
        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        if len(input) == 1:
            # iterating trough cogs
            for cog in self.client.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower() and not cog.lower() in ["jishaku","loggingerror","dev","hellping"]:

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'{cog} - Commands', description=f'{self.client.cogs[cog].__doc__}\nUse `{prefix}help <command>` to gain more information about that command',
                                        color=discord.Color.green())

                    # getting commands from cog
                    for command in self.client.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            emb.add_field(name=f"`{prefix}{command.name}`", value=command.description, inline=False)
                    # found cog - breaking loop
                    dm = True
                    break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                for command in self.client.commands:
                    if command.name.lower() == input[0].lower() or input[0].lower() in command.aliases:
                        emb = discord.Embed(title=f"{command.name}",
                                            description=f"{command.description}",
                                            color=discord.Color.green())
                        emb.add_field(name = 'Command Usage',value = f"`{prefix}{command.help}`",inline = False)    

                        build = ""
                        try:
                            if command.walk_commands():
                                for subcommand in command.walk_commands():
                                    if subcommand.parents[0] == command:
                                        build += f'> {subcommand.name}\n'
                                emb.add_field(name = 'Subcommands',value = build,inline = False)
                        except:
                            pass

                        if command.aliases:
                            emb.add_field(name = "Aliases",value = "`" + '\n'.join(command.aliases) + "`")
                        else:
                            emb.add_field(name = "Aliases",value = "`None`")

                        if command.brief:
                            emb.add_field(name = "Documentation",value = command.brief,inline = False)
                        break
                else:
                    emb = discord.Embed(title="Invalid Module or Command",
                                            description=f"I've never heard about something called `{input[0]}` before",
                                            color=discord.Color.orange())

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            command = None
            for a in self.client.commands:
                if a.name  == input[0]:
                    command = a

            if not command:
                emb = discord.Embed(title="Invalid Subcommand",
                                                description=f"I've never heard about something called `{' '.join(input)}` before",
                                                color=discord.Color.orange())
            else:
                for subcommand in input[1:]:
                    command = await self.get_subcommand(subcommand,command)
                    if command:
                        continue
                    else:
                        break
                if command:
                    emb = discord.Embed(title=f"{command.name}",
                                                description=f"{command.description}",
                                                color=discord.Color.green())
                    emb.add_field(name = 'Command Usage',value = f"`{prefix}{command.help}`",inline = False)    
                    build = ""
                    try:
                        if command.walk_commands():
                            for subcommand in command.walk_commands():
                                if subcommand.parents[0] == command:
                                    build += f'> {subcommand.name}\n'
                            emb.add_field(name = 'Subcommands',value = build,inline = False)
                    except:
                        pass

                    if command.aliases:
                        emb.add_field(name = "Aliases",value = "`" + '\n'.join(command.aliases) + "`")
                    else:
                        emb.add_field(name = "Aliases",value = "`None`")

                    if command.brief:
                            emb.add_field(name = "Documentation",value = command.brief,inline = False)
                else:
                    emb = discord.Embed(title="Invalid Subcommand",
                                                    description=f"I've never heard about something called `{' '.join(input)}` before",
                                                    color=discord.Color.orange())


        else:
            emb = discord.Embed(title="It's a magical place.",
                                description="I don't know how you got here. But I didn't see this coming at all.\n"
                                            ,
                                color=discord.Color.red())

        # sending reply embed using our own function defined above

        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        return emb

    @commands.command(description = "Literally this command...why you looking at this.",help = "help [command or cog]")
    async def help(self,ctx,*,input = None):
        def check(i):
            if i.message.id == message.id:
                return True
            else:
                return False
        if not input:
            selectslist = []
            for cog in self.cogs_short:
                selectslist.append(SelectOption(value = cog,label = cog.capitalize(),description = self.cogs_short[cog]))
            embed = discord.Embed(title = "Oasis Bot Help Command",description = "Hello! You can use the selects list below to navigate through the categories.",color = discord.Color.random())
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text = f'Choose a category below to get started!',icon_url = ctx.guild.icon)
            message = await ctx.send(embed = embed,components = [Select(options =selectslist )])

            while True:
                try:
                    interaction = await self.client.wait_for("select_option", timeout = 60.0,check = check)
                except asyncio.TimeoutError:
                    return await message.edit("Message Inactive",components = [Select(options =selectslist,disabled = True)])

                if not (interaction.user.id == ctx.author.id):
                    embed=discord.Embed(description=f"This isn't your help message.", color=discord.Color.red())
                    if not interaction.responded:
                        await interaction.respond(embed = embed)
                    continue

                specificembed = await self.helpemb(ctx,interaction.values[0].lower())

                await interaction.respond(embed = specificembed)

        else:
            embed = await self.helpemb(ctx,input)
            await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Help(client))