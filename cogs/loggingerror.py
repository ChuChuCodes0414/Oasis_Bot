import discord
from discord.ext import commands
import json
import sys
import traceback
import math
import datetime
import uuid
import os

class LoggingError(commands.Cog):
    def __init__(self,client):
        self.client = client

    async def send_error_embed(self,ctx,message):
        embed = discord.Embed(description = message,color = discord.Color.red())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.guild.icon)
        try:
            await ctx.reply(embed= embed)
        except:
            try:
                await ctx.send(embed= embed)
            except:
                pass

    def get_command_signature(self, command,context):
        parent = command.parent
        entries = []
        while parent is not None:
            if not parent.signature or parent.invoke_without_command:
                entries.append(parent.name)
            else:
                entries.append(parent.name + ' ' + parent.signature)
            parent = parent.parent
        parent_sig = ' '.join(reversed(entries))

        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent_sig:
                fmt = parent_sig + ' ' + fmt
            alias = fmt
        else:
            alias = command.name if not parent_sig else parent_sig + ' ' + command.name

        return f'{context.clean_prefix}{alias} {command.signature}'

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
        
        errorid = uuid.uuid4()

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
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_permissions]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
            await self.send_error_embed(ctx,_message)
            return

        if isinstance(error, commands.UserInputError):
            embed = discord.Embed(title = f'⚠ Invalid Input',description = f'**Command Usage:** {self.get_command_signature(ctx.command,ctx)}\n**Command Information:** {ctx.command.help}',color = discord.Color.red())
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
            try:
                await ctx.reply(embed = embed)
            except:
                await ctx.send(embed = embed)
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


        embed = discord.Embed(title = "Uh oh! Seems like you got an uncaught excpetion.",description = "I have no idea how you got here, but it seems your error was not traced! If this occurs frequently, please feel free to join the [support server](https://discord.com/invite/9pmGDc8pqQ) and report the bug!",color = discord.Color.red())
        if len(''.join(traceback.format_exception_only(type(error), error))) < 4000:
            embed.add_field(name = "Error Details:",value = f"```{''.join(traceback.format_exception_only(type(error), error))}```")
        else:
            embed.add_field(name = "Error Details:",value = f"```Error details are too long to display! Join the support server with your error code for more details.```")
        embed.add_field(name = "Error ID",value = errorid,inline = False)
        try:
            await ctx.reply(embed = embed)
        except:
            try:
                await ctx.send(embed = embed)
            except:
                pass

        # ignore all other exception types, but print them to stderr
        if self.client.user.id == 830817370762248242:
            channel = self.client.get_channel(int(850553146421149756))
        else:
            channel = self.client.get_channel(int(975508813929119764))
            

        embed = discord.Embed(title = f'⚠ There was an error that was not traced!',description = f'On Command: {ctx.command.name}',color = discord.Color.red())
        embed.add_field(name = "Command Invoke Details",value = f'**Guild Info:** {ctx.guild.name} ({ctx.guild.id})\n**User Information:** {ctx.author.name} | {ctx.author.mention} ({ctx.author.id})\n**Jump URL:** {ctx.message.jump_url}\n**Command Used:** {ctx.message.content}\n**Error ID:** {errorid}',inline = False)
        errordetails = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        if len(errordetails) < 1000:
            embed.add_field(name = "Command Error Log",value = f'```{errordetails}```')
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.guild.icon)
            embed.timestamp = datetime.datetime.now()
            await channel.send(embed = embed)
        else:
            f =  open(f'errorlogging\{errorid}.txt', 'w')
            f.write(errordetails)
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.guild.icon)
            embed.timestamp = datetime.datetime.now()
            f.close()
            await channel.send(embed = embed,file = discord.File("errorlogging\\" + str(errorid) + ".txt"))
            os.remove(f"errorlogging\{errorid}.txt")
        
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)



async def setup(client):
    await client.add_cog(LoggingError(client))