import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import asyncio

from musicbot import utils
from musicbot import linkutils
from musicbot import config
from musicbot.audiocontroller import AudioController
from musicbot.utils import guild_to_audiocontroller

import datetime


class Music(commands.Cog):
    """ A collection of the commands related to music playback.

        Attributes:
            bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.register(guild)
            #print("Joined {}".format(guild.name))

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        await self.register(guild)

    async def register(self,guild):
        guild_to_audiocontroller[guild] = AudioController(self.bot, guild)

    # logic is split to uconnect() for wide usage
    @commands.command(name='connect', brief=config.HELP_CONNECT_LONG, description=config.HELP_CONNECT_SHORT, aliases=['c','join'],help = "connect")
    async def _connect(self, ctx):  # dest_channel_name: str
        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        if await audiocontroller.uconnect(ctx):
            await ctx.send(embed = discord.Embed(description = f"Connected to `{ctx.author.voice.channel}`",color = discord.Color.random()))

    @commands.command(name='disconnect', brief=config.HELP_DISCONNECT_LONG, description=config.HELP_DISCONNECT_SHORT, aliases=['dc'],help = "disconnect")
    async def _disconnect(self, ctx):
        if not ctx.guild.voice_client:
            await ctx.send(embed = discord.Embed(description = "The bot is not in a voice channel!",color = discord.Color.red()))
            return
        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        await audiocontroller.udisconnect()
        await ctx.send(embed = discord.Embed(description = f"Disconnected Successfully!",color = discord.Color.random()))

    @commands.command(name='reset', brief=config.HELP_DISCONNECT_LONG, description=config.HELP_DISCONNECT_SHORT, aliases=['rs', 'restart'],help = "reset")
    async def _reset(self, ctx):
        if not ctx.guild.voice_client:
            await ctx.send(embed = discord.Embed(description = "The bot is not in a voice channel!",color = discord.Color.red()))
            return
        current_guild = utils.get_guild(self.bot, ctx.message)

        await utils.guild_to_audiocontroller[current_guild].stop_player()
        await current_guild.voice_client.disconnect(force=True)

        guild_to_audiocontroller[current_guild] = AudioController(
            self.bot, current_guild)
        await guild_to_audiocontroller[current_guild].register_voice_channel(ctx.author.voice.channel)

        await ctx.send(embed = discord.Embed(description = f"Connected to `{ctx.author.voice.channel}`",color = discord.Color.random()))

    @commands.command(name='changechannel', brief=config.HELP_CHANGECHANNEL_LONG, description=config.HELP_CHANGECHANNEL_SHORT, aliases=['cc'],help = "changechannel")
    async def _change_channel(self, ctx):
        if not ctx.guild.voice_client:
            await ctx.send(embed = discord.Embed(description = "The bot is not in a voice channel!",color = discord.Color.red()))
            return

        current_guild = utils.get_guild(self.bot, ctx.message)

        vchannel = await utils.is_connected(ctx)
        if vchannel == ctx.author.voice.channel:
            await ctx.send("{} Already connected to {}".format(":white_check_mark:", vchannel.name))
            return

        await utils.guild_to_audiocontroller[current_guild].stop_player()
        await current_guild.voice_client.disconnect(force=True)

        guild_to_audiocontroller[current_guild] = AudioController(
            self.bot, current_guild)
        await guild_to_audiocontroller[current_guild].register_voice_channel(ctx.author.voice.channel)

        await ctx.send(embed = discord.Embed(description = f"Switched to `{ctx.author.voice.channel}`",color = discord.Color.random()))

    @commands.command(name='play', brief=config.HELP_YT_LONG, description=config.HELP_YT_SHORT, aliases=['p', 'yt', 'pl'],help = "play <song>")
    async def _play_song(self, ctx, *, track: str):
        async with ctx.typing():
            current_guild = utils.get_guild(self.bot, ctx.message)
            audiocontroller = utils.guild_to_audiocontroller[current_guild]

            if(await utils.is_connected(ctx) == None):
                if await audiocontroller.uconnect(ctx) == False:
                    return

            if track.isspace() or not track:
                return

            if await utils.play_check(ctx) == False:
                return

            # reset timer
            audiocontroller.timer.cancel()
            audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

            if audiocontroller.playlist.loop == True:
                await ctx.send("Loop is enabled! Use [prefix]loop to disable")
                return

            song = await audiocontroller.process_song(track,ctx.channel)
            if song == False:
                embed = discord.Embed(description = "Currently not supporting spotify playlists!",color = discord.Color.red())
                return await ctx.send(embed = embed)

            if song is None:
                await ctx.send(config.SONGINFO_UNKNOWN_SITE)
                return

            if song.origin == linkutils.Origins.Default:
                if audiocontroller.current_song != None and len(audiocontroller.playlist.playque) == 0:
                    pass
                else:
                    await ctx.send(embed=song.info.format_output(config.SONGINFO_QUEUE_ADDED))
            elif song.origin == linkutils.Origins.Playlist:
                await ctx.send(embed = discord.Embed(description = f"Playlist Queued",color = discord.Color.random()))

    @commands.command(name='loop', brief=config.HELP_LOOP_LONG, description=config.HELP_LOOP_SHORT, aliases=['l'],help = "loop")
    async def _loop(self, ctx):

        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]

        if await utils.play_check(ctx) == False:
            return

        if len(audiocontroller.playlist.playque) < 1 and current_guild.voice_client.is_playing() == False:
            await ctx.send("No songs in queue!")
            return

        if audiocontroller.playlist.loop == False:
            audiocontroller.playlist.loop = True
            await ctx.send(embed = discord.Embed(description = f"Loop Enabled! 🔃",color = discord.Color.random()))
        else:
            audiocontroller.playlist.loop = False
            await ctx.send(embed = discord.Embed(description = f"Loop Disabled! ❌",color = discord.Color.random()))

    @commands.command(name='shuffle', brief=config.HELP_SHUFFLE_LONG, description=config.HELP_SHUFFLE_SHORT, aliases=["sh"],help = "shuffle")
    async def _shuffle(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]

        if await utils.play_check(ctx) == False:
            return

        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            await ctx.send(embed = discord.Embed(description = f"Queue is Empty! ❌",color = discord.Color.random()))
            return

        audiocontroller.playlist.shuffle()
        await ctx.send(embed = discord.Embed(description = f"Shuffled Playlist! 🔀",color = discord.Color.random()))

        for song in list(audiocontroller.playlist.playque)[:config.MAX_SONG_PRELOAD]:
            asyncio.ensure_future(audiocontroller.preload(song))
        
    @commands.command(name = 'remove',brief = "Remove a song, by index, from the playlist.",description = "Remove a song.",aliases = ["re"],help = "remove <index>")
    async def _remove(self,ctx,index:int):
        if index < 1:
            return await ctx.send(embed = discord.Embed(description = "Index must be at least one!",color = discord.Color.red()))
        current_guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[current_guild]

        if await utils.play_check(ctx) == False:
            return
        
        queuelen = len(audiocontroller.playlist.playque)

        if queuelen < index:
            await ctx.send(embed = discord.Embed(description = f"There are only `{queuelen}` songs in your playlist!",color = discord.Color.red()))
            return

        track = audiocontroller.playlist.remove(index)
        title = track.info.title
        if title:
            await ctx.send(embed = discord.Embed(description = f"Removed `{title}` from the playlist",color = discord.Color.random()))
        else:
            await ctx.send(embed = discord.Embed(description = f"Removed `{index}` from the playlist",color = discord.Color.random()))

    @commands.command(name='pause', brief=config.HELP_PAUSE_LONG, description=config.HELP_PAUSE_SHORT,help = "pause")
    async def _pause(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            return await ctx.send(embed = discord.Embed(description = f"There is no music playing!",color = discord.Color.random()))
        current_guild.voice_client.pause()
        await ctx.send(embed = discord.Embed(description = f"Audio Paused! ⏸",color = discord.Color.random()))

    @commands.command(name='queue', brief=config.HELP_QUEUE_LONG, description=config.HELP_QUEUE_SHORT, aliases=['playlist', 'q'],help = "queue")
    async def _queue(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            await ctx.send(embed = discord.Embed(description = f"The queue is empty! ❌",color = discord.Color.random()))
            return

        playlist = utils.guild_to_audiocontroller[current_guild].playlist

        # Embeds are limited to 25 fields
        if config.MAX_SONG_PRELOAD > 25:
            config.MAX_SONG_PRELOAD = 25

        embed = discord.Embed(title=":scroll: Queue [{}]".format(
            len(playlist.playque)), color=config.EMBED_COLOR, inline=False)
        description = ""
        for counter, song in enumerate(list(playlist.playque)[:config.MAX_SONG_PRELOAD], start=1):
            if song.info.title is None:
                description += f"**{counter}**. [{song.info.webpage_url}]({song.info.webpage_url})\n"
            else:
                description += f"**{counter}**. [{song.info.title}]({song.info.webpage_url})\n"
        embed.description = description
        await ctx.send(embed=embed)

    @commands.command(name='stop', brief=config.HELP_STOP_LONG, description=config.HELP_STOP_SHORT, aliases=['st'],help = "stop")
    async def _stop(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.playlist.loop = False
        
        await utils.guild_to_audiocontroller[current_guild].stop_player()
        await ctx.send(embed = discord.Embed(description = f"Music stopped and queue cleared!",color = discord.Color.random()))

    @commands.command(name='skip', brief=config.HELP_SKIP_LONG, description=config.HELP_SKIP_SHORT, aliases=['s'],help = "skip")
    async def _skip(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.playlist.loop = False

        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        if current_guild.voice_client is None or (
                not current_guild.voice_client.is_paused() and not current_guild.voice_client.is_playing()):
            await ctx.send(embed = discord.Embed(description = f"Not playing a song currently! ❌",color = discord.Color.random()))
        current_guild.voice_client.stop()
        await ctx.send(embed = discord.Embed(description = f"Current song skipped! ⏩",color = discord.Color.random()))

    @commands.command(name='clear', brief=config.HELP_CLEAR_LONG, description=config.HELP_CLEAR_SHORT,help = "clear")
    async def _clear(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.clear_queue()
        current_guild.voice_client.stop()
        audiocontroller.playlist.loop = False
        await ctx.send(embed = discord.Embed(description = f"Queue Cleared! 🚫",color = discord.Color.random()))

    @commands.command(name='prev', brief=config.HELP_PREV_LONG, description=config.HELP_PREV_SHORT, aliases=['back'],help = "prev")
    async def _prev(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.playlist.loop = False

        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        await utils.guild_to_audiocontroller[current_guild].prev_song()
        await ctx.send(embed = discord.Embed(description = f"Playing previous song! ⏮",color = discord.Color.random()))

    @commands.command(name='resume', brief=config.HELP_RESUME_LONG, description=config.HELP_RESUME_SHORT,help = "resume")
    async def _resume(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return

        current_guild.voice_client.resume()
        await ctx.send(embed = discord.Embed(description = f"Resumed Audio ⏯",color = discord.Color.random()))

    @commands.command(name='songinfo', brief=config.HELP_SONGINFO_LONG, description=config.HELP_SONGINFO_SHORT, aliases=["np"],help = "songinfo")
    async def _songinfo(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return
        
        song = utils.guild_to_audiocontroller[current_guild].current_song
        if song is None:
            return
        await ctx.send(embed=song.info.format_output(config.SONGINFO_SONGINFO))

    @commands.command(name='history', brief=config.HELP_HISTORY_LONG, description=config.HELP_HISTORY_SHORT,help = "history")
    async def _history(self, ctx):
        current_guild = utils.get_guild(self.bot, ctx.message)

        if await utils.play_check(ctx) == False:
            return
        await ctx.send(embed = discord.Embed(titple = "Recent Songs Played",description = utils.guild_to_audiocontroller[current_guild].track_history(),color = discord.Color.random()))

    @commands.command(name='volume', aliases=["vol"], brief=config.HELP_VOL_LONG, description=config.HELP_VOL_SHORT,help = "volume <volume>")
    async def _volume(self, ctx, *args):
        if await utils.play_check(ctx) == False:
            return

        if len(args) == 0:
            await ctx.send(embed = discord.Embed(description = f"🔉 Current Volume: {utils.guild_to_audiocontroller[ctx.guild]._volume}%",color = discord.Color.random()))         
            return

        try:
            volume = args[0]
            volume = int(volume)
            if volume > 100 or volume < 0:
                raise Exception('')
            current_guild = utils.get_guild(self.bot, ctx.message)

            if utils.guild_to_audiocontroller[current_guild]._volume >= volume:
                await ctx.send(embed = discord.Embed(description = f"🔉 Volume Set: {volume}%",color = discord.Color.random()))         
            else:
                await ctx.send(embed = discord.Embed(description = f"🔊 Volume Set: {volume}%",color = discord.Color.random()))         
            utils.guild_to_audiocontroller[current_guild].volume = volume
        except:
            await ctx.send(embed = discord.Embed(description = f"Volume must be between 0 and 100!",color = discord.Color.random()))         


def setup(bot):
    bot.add_cog(Music(bot))
