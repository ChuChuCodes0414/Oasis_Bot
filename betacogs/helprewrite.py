import discord
from discord.ext import commands
from firebase_admin import db
from discord.abc import Messageable

class MyHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        channel = self.get_destination()
        embed = discord.Embed(title = "Bot Help",description = "Categories Listed Below",color = discord.Color.random())
        for cog, commands in mapping.items():
            if cog and cog.qualified_name not in ['HelpRewrite','BetaReload','Jishaku']:
                embed.add_field(name = cog.qualified_name,value = cog.short + "\n" + f"`{len(commands)} Commands`")
        await channel.send(embed = embed)
    
    async def send_cog_help(self, cog):
        channel = self.get_destination()
        embed = discord.Embed(title = cog.qualified_name,description = cog.get_commands(),color = discord.Color.random())
        await channel.send(embed = embed)

    async def send_command_help(self, command):
        channel = self.get_destination()
        embed = discord.Embed(title = command.name,description = command.help,color = discord.Color.random())
        embed.add_field(name = "Command Syntax",value = f"`{self.get_command_signature(command)}`",inline = False)
        embed.add_field(name = "Aliases",value = f'`{", ".join(command.aliases)}`',inline = False)
        await channel.send(embed = embed)

    async def send_group_help(self, group):
        return await super().send_group_help(group)

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Error", description=str(error))
            await ctx.send(embed=embed)
        else:
            raise error

class HelpRewrite(commands.Cog):
    def __init__(self,client):
        self.client = client
        help_command = MyHelp()
        help_command.cog = self # Instance of YourCog class
        client.help_command = help_command
    

def setup(client):
    client.add_cog(HelpRewrite(client))