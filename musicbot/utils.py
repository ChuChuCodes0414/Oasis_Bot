import asyncio
from musicbot import config
import discord
# A dictionary that remembers which guild belongs to which audiocontroller
guild_to_audiocontroller = {}


def get_guild(bot, command):
    """Gets the guild a command belongs to. Useful, if the command was sent via pm."""
    if command.guild is not None:
        return command.guild
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            if command.author in channel.members:
                return guild
    return None


async def connect_to_channel(guild, dest_channel_name, ctx, switch=False, default=True):
    """Connects the bot to the specified voice channel.

        Args:
            guild: The guild for witch the operation should be performed.
            switch: Determines if the bot should disconnect from his current channel to switch channels.
            default: Determines if the bot should default to the first channel, if the name was not found.
    """
    for channel in guild.voice_channels:
        if str(channel.name).strip() == str(dest_channel_name).strip():
            if switch:
                try:
                    await guild.voice_client.disconnect()
                except:
                    await ctx.send(embed = discord.Embed(description = config.NOT_CONNECTED_MESSAGE,color = discord.Color.red()))

            await channel.connect()
            return

    if default:
        try:
            await guild.voice_channels[0].connect()
        except:
            await ctx.send(embed = discord.Embed(description = config.DEFAULT_CHANNEL_JOIN_FAILED,color = discord.Color.red()))
    else:
        await ctx.send(embed = discord.Embed(description = config.CHANNEL_NOT_FOUND_MESSAGE + str(dest_channel_name),color = discord.Color.red()))


async def is_connected(ctx):
    try:
        voice_channel = ctx.guild.voice_client.channel
        return voice_channel
    except:
        return None


async def play_check(ctx):
    author_voice = ctx.message.author.voice
    bot_vc = ctx.guild.voice_client
    if not bot_vc:
        await ctx.send(embed = discord.Embed(description = "The bot is not in a voice channel!",color = discord.Color.red()))
        return False
    bot_vc = ctx.guild.voice_client.channel
    if author_voice == None:
        await ctx.send(embed = discord.Embed(description = config.USER_NOT_IN_VC_MESSAGE,color = discord.Color.red()))
        return False
    elif ctx.message.author.voice.channel != bot_vc:
        await ctx.send(embed = discord.Embed(description = config.USER_NOT_IN_VC_MESSAGE,color = discord.Color.red()))
        return False


class Timer:
    def __init__(self, callback):
        self._callback = callback
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        await asyncio.sleep(config.VC_TIMEOUT)
        await self._callback()

    def cancel(self):
        self._task.cancel()
