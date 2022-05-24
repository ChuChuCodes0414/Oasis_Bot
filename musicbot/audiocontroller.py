import discord
import yt_dlp

import asyncio
import concurrent.futures

from musicbot import linkutils
from musicbot import utils

from musicbot import config
from musicbot.playlist import Playlist
from musicbot.songinfo import Song
import time

class AudioController(object):
    """ Controls the playback of audio and the sequential playing of the songs.

            Attributes:
                bot: The instance of the bot that will be playing the music.
                playlist: A Playlist object that stores the history and queue of songs.
                current_song: A Song object that stores details of the current song.
                guild: The guild in which the Audiocontroller operates.
        """

    def __init__(self, bot, guild):
        self.bot = bot
        self.playlist = Playlist()
        self.current_song = None
        self.guild = guild
        self.skips = []
        self.voice_client = None

        self._volume = 100
        self.timer = utils.Timer(self.timeout_handler)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value
        try:
            self.voice_client.source.volume = float(value) / 100.0
        except Exception as e:
            pass

    async def register_voice_channel(self, channel):
        self.voice_client = await channel.connect(reconnect=True, timeout=None)

    def track_history(self):
        history_string = ""
        for trackname in self.playlist.trackname_history:
            history_string += "\n" + trackname
        return history_string

    def next_song(self, error):
        """Invoked after a song is finished. Plays the next song if there is one."""

        next_song = self.playlist.next(self.current_song)

        self.current_song = None
        self.skips = []

        if next_song is None:
            return

        coro = self.play_song(next_song)
        self.bot.loop.create_task(coro)

    async def play_song(self, song):
        """Plays a song object"""

        if self.playlist.loop != True: #let timer run thouh if looping
            self.timer.cancel()
            self.timer = utils.Timer(self.timeout_handler)

        if song.info.title == None:
            if song.host == linkutils.Sites.Spotify:
                conversion = self.search_youtube(await linkutils.convert_spotify(song.info.webpage_url))
                song.info.webpage_url = conversion

            downloader = yt_dlp.YoutubeDL(
                {'format': 'bestaudio', 'title': True, "cookiefile": config.COOKIE_PATH,'logtostderr': False,'quiet': True,'no_warnings': True,})
            r = downloader.extract_info(
                song.info.webpage_url, download=False)

            song.base_url = r.get('url')
            song.info.uploader = r.get('uploader')
            song.info.title = r.get('title')
            song.info.duration = r.get('duration')
            song.info.webpage_url = r.get('webpage_url')
            song.info.thumbnail = r.get('thumbnails')[0]['url']

        self.playlist.add_name(song.info.title)
        self.current_song = song

        self.playlist.playhistory.append(self.current_song)

        self.voice_client.play(discord.FFmpegPCMAudio(
            song.base_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after=lambda e: self.next_song(e))

        self.voice_client.source = discord.PCMVolumeTransformer(
            self.guild.voice_client.source)
        self.voice_client.source.volume = float(self.volume) / 100.0

        self.playlist.playque.popleft()

        await song.info.channel.send(embed = song.info.format_output(config.SONGINFO_NOW_PLAYING))

        for song in list(self.playlist.playque)[:config.MAX_SONG_PRELOAD]:
            asyncio.ensure_future(self.preload(song))

    async def process_song(self, track, channel):
        """Adds the track to the playlist instance and plays it, if it is the first song"""

        host = linkutils.identify_url(track)
        is_playlist = linkutils.identify_playlist(track)

        if is_playlist != linkutils.Playlist_Types.Unknown:

            result = await self.process_playlist(is_playlist, track,channel)

            if result == False:
                return False

            if self.current_song == None:
                await self.play_song(self.playlist.playque[0])
                #print("Playing {}".format(track))

            song = Song(linkutils.Origins.Playlist,
                        linkutils.Sites.Unknown,channel = channel)
            return song

        if host == linkutils.Sites.Unknown:
            if linkutils.get_url(track) is not None:
                return None

            track = self.search_youtube(track)

        if host == linkutils.Sites.Spotify:
            title = await linkutils.convert_spotify(track)
            track = self.search_youtube(title)

        if host == linkutils.Sites.YouTube:
            track = track.split("&list=")[0]

        try:
            downloader = yt_dlp.YoutubeDL(
               {'format': 'bestaudio', 'title': True, "cookiefile": config.COOKIE_PATH,'logtostderr': False,'quiet': True,'no_warnings': True,})
            r = downloader.extract_info(
                track, download=False)
        except:
            downloader = yt_dlp.YoutubeDL(
                {'title': True, "cookiefile": config.COOKIE_PATH,'logtostderr': False,'quiet': True,'no_warnings': True})
            r = downloader.extract_info(
                track, download=False)

        if r.get('thumbnails') is not None:
            thumbnail = r.get('thumbnails')[len(
                r.get('thumbnails')) - 1]['url']
        else:
            thumbnail = None

        song = Song(linkutils.Origins.Default, host, base_url=r.get('url'), uploader=r.get('uploader'), title=r.get(
            'title'), duration=r.get('duration'), webpage_url=r.get('webpage_url'), thumbnail=thumbnail,channel = channel)

        self.playlist.add(song)
        if self.current_song == None:
            #print("Playing {}".format(track))
            await self.play_song(song)

        return song

    async def process_playlist(self, playlist_type, url,channel):

        if playlist_type == linkutils.Playlist_Types.YouTube_Playlist:
            if ("playlist?list=" in url):
                listid = url.split('=')[1]
            else:
                video = url.split('&')[0]
                await self.process_song(video)
                return

            options = {
                'format': 'bestaudio/best',
                'extract_flat': True,
                "cookiefile": config.COOKIE_PATH,
                'logtostderr': False,
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                r = ydl.extract_info(url, download=False)

                for entry in r['entries']:

                    link = "https://www.youtube.com/watch?v={}".format(
                        entry['id'])

                    song = Song(linkutils.Origins.Playlist,
                                linkutils.Sites.YouTube, webpage_url=link,channel = channel)

                    self.playlist.add(song)

        if playlist_type == linkutils.Playlist_Types.Spotify_Playlist:
            '''
            links = await linkutils.get_spotify_playlist(url)
            for link in links:
                song = Song(linkutils.Origins.Playlist,
                            linkutils.Sites.Spotify, webpage_url=link,channel = channel)
                self.playlist.add(song)
            '''
            return False

        if playlist_type == linkutils.Playlist_Types.BandCamp_Playlist:
            options = {
                'format': 'bestaudio/best',
                'extract_flat': True,
                'logtostderr': False,
                'quiet': True,
                'no_warnings': True,
                'limit-rate':'20000'
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                r = ydl.extract_info(url, download=False)

                for entry in r['entries']:

                    link = entry.get('url')

                    song = Song(linkutils.Origins.Playlist,
                                linkutils.Sites.Bandcamp, webpage_url=link,channel = channel)

                    self.playlist.add(song)

        for song in list(self.playlist.playque)[:config.MAX_SONG_PRELOAD]:
            asyncio.ensure_future(self.preload(song))

    async def preload(self, song):

        if song.info.title != None:
            return

        def down(song):
            if song.host == linkutils.Sites.Spotify:
                song.info.webpage_url = self.search_youtube(song.info.title)
            downloader = yt_dlp.YoutubeDL(
                {
                    'format': 'bestaudio', 
                    'title': True, 
                    "cookiefile": config.COOKIE_PATH,
                    'logtostderr': False,
                    'quiet': True,
                    'no_warnings': True,
                    'limit-rate':'20000'
                    
                })
            r = downloader.extract_info(
                song.info.webpage_url, download=False)
            song.base_url = r.get('url')
            song.info.uploader = r.get('uploader')
            song.info.title = r.get('title')
            song.info.duration = r.get('duration')
            song.info.webpage_url = r.get('webpage_url')
            song.info.thumbnail = r.get('thumbnails')[0]['url']

        if song.host == linkutils.Sites.Spotify:
            song.info.title = await linkutils.convert_spotify(song.info.webpage_url)

        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=3)
        await asyncio.wait(fs={loop.run_in_executor(executor, down, song)}, return_when=asyncio.ALL_COMPLETED)

    def search_youtube(self, title):
        """Searches youtube for the video title and returns the first results video link"""

        # if title is already a link
        if linkutils.get_url(title) is not None:
            return title

        options = {
            'format': 'bestaudio/best',
            'default_search': 'auto',
            'noplaylist': True,
            "cookiefile": config.COOKIE_PATH,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'limit-rate':'1000000'
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            r = ydl.extract_info(title, download=False)

        videocode = r['entries'][0]['id']

        return "https://www.youtube.com/watch?v={}".format(videocode)

    async def stop_player(self):
        """Stops the player and removes all songs from the queue"""
        if self.guild.voice_client is None or (
                not self.guild.voice_client.is_paused() and not self.guild.voice_client.is_playing()):
            return

        self.playlist.loop = False
        self.skips = []
        self.playlist.next(self.current_song)
        self.clear_queue()
        self.guild.voice_client.stop()

    async def prev_song(self):
        """Loads the last song from the history into the queue and starts it"""

        self.timer.cancel()
        self.timer = utils.Timer(self.timeout_handler)

        if len(self.playlist.playhistory) == 0:
            return

        prev_song = self.playlist.prev(self.current_song)

        if not self.guild.voice_client.is_playing() and not self.guild.voice_client.is_paused():

            if prev_song == "Dummy":
                self.playlist.next(self.current_song)
                return None
            await self.play_song(prev_song)
        else:
            self.guild.voice_client.stop()

    async def timeout_handler(self):

        if len(self.guild.voice_client.channel.voice_states) == 1:
            await self.udisconnect()
            return

        if self.guild.voice_client.is_playing():
            self.timer = utils.Timer(self.timeout_handler)  # restart timer
            return

        self.timer = utils.Timer(self.timeout_handler)
        await self.udisconnect()

    async def uconnect(self, ctx):
        if not ctx.author.voice:
            await ctx.send(config.USER_NOT_IN_VC_MESSAGE)
            return False

        vchannel = await utils.is_connected(ctx)

        if vchannel is not None:
            await ctx.send(config.ALREADY_CONNECTED_MESSAGE)
            return

        await self.register_voice_channel(ctx.author.voice.channel)
        return True

    async def udisconnect(self):
        await self.stop_player()
        await self.guild.voice_client.disconnect(force=True)

    def clear_queue(self):
        self.playlist.playque.clear()
