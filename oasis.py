from re import L
import discord
import os
from discord.ext import commands, tasks
from itertools import cycle
import firebase_admin
from firebase_admin import db
import sensitive
import aiohttp
#from discord_components import DiscordComponents, ComponentsBot, Button

firebase_admin.initialize_app()

cred_obj_eleaderboard = sensitive.CRED_OBJECT_ELEADERBOARD
eleaderboard_app = firebase_admin.initialize_app(cred_obj_eleaderboard , {
    'databaseURL': sensitive.ELEADERBOARD_LINK
    },name="elead")

cred_obj = sensitive.CRED_OBJECT_PCHANNEL
channels_app = firebase_admin.initialize_app(cred_obj , {
    'databaseURL': sensitive.PCHANNEL_LINK
    },name='pepegabot')

cred_obj_modtracking = sensitive.CRED_OBJ_MODTRACKING
modtracking_app = firebase_admin.initialize_app(cred_obj_modtracking , {
    'databaseURL': sensitive.MODTRACKING_LINK
    },name="modtracking")

cred_obj_settings = sensitive.CRED_OBJ_SETTINGS
settings_app = firebase_admin.initialize_app(cred_obj_settings , {
    'databaseURL': sensitive.SETTINGS_LINK
    },name="settings")

cred_obj_profile = sensitive.CRED_OBJ_PROFILE
profile_app = firebase_admin.initialize_app(cred_obj_profile , {
    'databaseURL':sensitive.PROFILE_LINK
    },name="profile")

cred_obj_invites = sensitive.CRED_OBJ_INVITES
invites_app = firebase_admin.initialize_app(cred_obj_invites , {
    'databaseURL':sensitive.INVITES_LINK
    },name="invites")

cred_obj_lottery = sensitive.CRED_OBJ_LOTTERY
lottery_app = firebase_admin.initialize_app(cred_obj_lottery , {
    'databaseURL':sensitive.LOTTERY_LINK
    },name="lottery")

cred_obj_bans = sensitive.CRED_OBJ_BANS
bans_app = firebase_admin.initialize_app(cred_obj_bans , {
    'databaseURL':sensitive.BANS_LINK
    },name="bans")

class Client(commands.Bot):
    def __init__(self):
        self.beta = False
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix = self.get_prefix,intents = intents)
        
        if self.beta:
            self.change = cycle(['with your feelings',',help'])
        else:
            self.change = cycle(['with your feelings!','o!help | @Oasis Bot setup'])
    
    async def get_prefix(self,message):  
        ref = db.reference("/",app = firebase_admin._apps['settings']) 
        if self.beta:
            return (",")
        return (ref.child(str(message.guild.id)).child('prefix').get())

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        self._BotBase__cogs  = commands.core._CaseInsensitiveDict()
        await self.load_extension("jishaku")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        self.change_status.start()
    
    @tasks.loop(seconds = 10)
    async def change_status(self):
        await client.change_presence(activity=discord.Game(next(self.change)))
    
    @change_status.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  

    async def on_ready(self):
        print('Bot is online.')

client = Client()

@client.check
def global_check(ctx):
    ref = db.reference("/",app = firebase_admin._apps['settings'])
    settings = ref.child(str(ctx.guild.id)).child("rules").child(ctx.command.name).get()
    if not settings:
        return True
    else:
        aroles = settings.get("aroles",None)
        droles = settings.get("droles",None)
        achannels = settings.get("achannels",None)
        dchannels = settings.get("dchannels",None)
        ausers = settings.get("ausers",None)
        dusers = settings.get("dusers",None)
        aall = settings.get("aall",None)
        dall = settings.get("dall",None)

        channel = ctx.channel.id
        roles = [(r.id) for r in ctx.author.roles]
        user = ctx.author.id

        if aall:
            return True
        if aroles:
            if any(item in aroles for item in roles):
                return True
        if achannels:
            if channel in achannels:
                return True
        if ausers:
            if user in ausers:
                return True
        if dall:
            return False
        if droles:
            if any(item in aroles for item in roles):
                return False
        if dchannels:
            if channel in dchannels:
                return False
        if dusers:
            if user in dusers:
                return False
        
        return True

# prefix handling    

if client.beta:
    client.run(sensitive.DEVELOPMENT_BOT_TOKEN)
else:
    client.run(sensitive.BOT_TOKEN)
