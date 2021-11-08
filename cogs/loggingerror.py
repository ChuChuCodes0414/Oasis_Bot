import discord
from discord.ext import commands
import json
import sys
import traceback
import math
import datetime

class LoggingError(commands.Cog):
    '''
        Hey you found an easter egg! But not really. This module is used for backend stuff, so there's really nothing here.
    '''

    def __init__(self,client):
        self.client = client
    

    async def send_error_embed(self,ctx,message):
        embed = discord.Embed(description = message,color = discord.Color.red())
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.guild.icon_url)
        try:
            await ctx.reply(embed= embed)
        except:
            try:
                await ctx.send(embed= embed)
            except:
                pass

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logging Error Cog Loaded.')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # if command has local error handler, return
        if hasattr(ctx.command, 'on_error'):
            return

        # get the original exception
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
            await self.send_error_embed(ctx,_message)
            return

        if isinstance(error, commands.DisabledCommand):
            await self.send_error_embed(ctx,"Seems like this command was disabled. This is most likely due to a bug in the command, which will be fixed soon.\n"+
                "If you have any questions, feel free to join the [support server](https://discord.com/invite/9pmGDc8pqQ) to ask!")
            return

        if isinstance(error, commands.CommandOnCooldown):
            await self.send_error_embed(ctx,"This command is on cooldown, please retry in `{}` seconds.".format(math.ceil(error.retry_after)))
            return

        if isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
            await self.send_error_embed(ctx,_message)
            return

        if isinstance(error, commands.UserInputError):
            embed = discord.Embed(title = f'⚠ Invalid Input',description = f'**Command Usage:** {ctx.command.help}\n**Command Information:** {ctx.command.description}',color = discord.Color.red())
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed = embed)
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            await self.send_error_embed(ctx,"Looks like you don't have permission to do that here.")
            return

        if isinstance(error,discord.Forbidden):
            await self.send_error_embed(ctx,"Looks like I am missing permissions to complete your command.")
            return

        await self.send_error_embed(ctx,"I have no idea how you got here, but it seems your error was not traced! If this occurs frequently, please feel free to join the [support server](https://discord.com/invite/9pmGDc8pqQ) and report the bug!")

        # ignore all other exception types, but print them to stderr
        channel = self.client.get_channel(int(850553146421149756))

        embed = discord.Embed(title = f'⚠ There was an error that was not traced!',description = f'On Command: {ctx.command.name}',color = discord.Color.red())
        embed.add_field(name = "Command Invoke Details",value = f'**Guild ID:** {ctx.guild.id}\n**User Information:** {ctx.author.mention} ({ctx.author.id})\n**Jump URL:** {ctx.message.jump_url}\n**Command Used:** {ctx.message.content}',inline = False)
        errordetails = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        #embed.add_field(name = "Command Error Log",value = f'```{errordetails}```')

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'Oasis Bot Dev Logging',icon_url = channel.guild.icon_url)

        await channel.send(embed = embed)

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)



def setup(client):
    client.add_cog(LoggingError(client))