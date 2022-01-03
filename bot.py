from re import L
import discord
import random
import json
import os
import inspect
from discord.ext import commands, tasks
from itertools import cycle
import firebase_admin
from firebase_admin import db
from discord_components import DiscordComponents
import sensitive
import asyncio
from discord.embeds import EmptyEmbed
import time

beta = True

firebase_admin.initialize_app()


cred_obj_eleaderboard = sensitive.CRED_OBJECT_ELEADERBOARD
eleaderboard_app = firebase_admin.initialize_app(cred_obj_eleaderboard , {
    'databaseURL': sensitive.ELEADERBOARD_LINK
    },name="elead")

cred_obj_modlogs = sensitive.CRED_OBJECT_MODLOGS
modlogs_app = firebase_admin.initialize_app(cred_obj_modlogs , {
    'databaseURL':sensitive.MODLOGS_LINK
    },name="modlogs")

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

cred_obj_freeloader = sensitive.CRED_OBJ_FREELOADER
freeloader_app = firebase_admin.initialize_app(cred_obj_freeloader , {
    'databaseURL':sensitive.FREELOADER_LINK
    },name="freeloader")

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

def get_prefix(client,message):   
    if beta:
        return ',' 
    ref = db.reference("/",app = firebase_admin._apps['settings'])
    return (ref.child(str(message.guild.id)).child('prefix').get())


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = get_prefix, intents = intents)
client.remove_command('help')

if not beta:
    status = cycle(['with your feelings','o!help | @Oasis Bot setup'])
else:
    status = cycle(['with new code!',',help | @Serenity Bot setup'])



@client.event
async def on_ready():
    change_status.start()
    check_status.start()
    DiscordComponents(client)
    print('Bot is online.')
    

# prefix handling
@client.event
async def on_guild_join(guild):
    ref = db.reference("/",app = firebase_admin._apps['settings'])
    
    serverconf = {'dj': None, 'event': None, 'giveaway': None, 'mod': [None], 'modtrack': [None], 'pchannels': [None], 'prefix': 'o!'}

    ref.child(str(guild.id)).set(serverconf)

@client.event
async def on_guild_remove(guild):
    ref = db.reference("/",app = firebase_admin._apps['settings'])

    ref.child(str(guild.id)).delete()

# status looping
@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

@tasks.loop(minutes = 30,reconnect = True)
async def check_status():
    errors = ""
    apiping = round(client.latency*1000)
    if apiping >= 1000:
        errors += f"⚠ API Ping Alert: {apiping}ms\n"
    channel = client.get_channel(908473269219373127)
    initial = await channel.send(embed = discord.Embed(description = "Starting Bot Check"))
    status = f"API Ping: `{apiping}ms`\n"
    embed = discord.Embed(title = "Checking Bot Status <a:OB_Loading:907101653692456991>",description = status,color = discord.Color.random())
    embed.set_footer(text = "Checking Real Ping...")
    message = await channel.send(embed = embed)
    latency = initial.created_at - message.created_at
    status += f"Read Ping: `{latency.microseconds*0.001}ms`\n"
    embed = discord.Embed(title = "Checking Bot Status <a:OB_Loading:907101653692456991>",description = status,color = discord.Color.random())
    await message.edit(embed = embed)
    if latency.microseconds*0.001 >= 10000:
        errors += f"⚠ Realtime Ping Alert: {latency.microseconds*0.001}ms\n"

    embed = discord.Embed(title = "Checking Database Status <a:OB_Loading:907101653692456991>",color = discord.Color.random())
    databases = {"elead":"Event","modlogs":"Mod Logs","pepegabot":"Private Channels","modtracking":"Mod Tracking","settings":"Settings","freeloader":"Freeloader","profile":"Profile","invites":"Invites","lottery":"Lottery"}
    message = await channel.send(embed = embed)
    for database,name in databases.items():
        embed.add_field(name = f"{name} Database",value = f"Upload: <a:OB_Loading:907101653692456991>\nDownload: <a:OB_Loading:907101653692456991>\nDelete: <a:OB_Loading:907101653692456991>")
        embed.set_footer(text = f"Checking {name} Database...")
        await message.edit(embed = embed)

        ref = db.reference("/",app = firebase_admin._apps[database])
        try:
            ref.child("test").set("test")
            set1 = "<a:PB_greentick:865758752379240448>"
        except:
            set1 = "<a:PB_redtick:873384525202350090>"
            errors += f"⚠ Database Upload Alert: {name}\n"
        await asyncio.sleep(2)
        embed.remove_field(-1)
        embed.add_field(name = f"{name} Database",value = f"Upload: {set1}\nDownload: <a:OB_Loading:907101653692456991>\nDelete: <a:OB_Loading:907101653692456991>")
        await message.edit(embed = embed)
        try:
            value = ref.child("test").get()
            get1 = "<a:PB_greentick:865758752379240448>"
        except:
            get1 = "<a:PB_redtick:873384525202350090>"
            errors += f"⚠ Database Download Alert: {name}\n"
        await asyncio.sleep(2)
        embed.remove_field(-1)
        embed.add_field(name = f"{name} Database",value = f"Upload: {set1}\nDownload: {get1}\nDelete: <a:OB_Loading:907101653692456991>")
        await message.edit(embed = embed)
        try:
            ref.child("test").delete()
            delete1 = "<a:PB_greentick:865758752379240448>"
        except:
            delete1 = "<a:PB_redtick:873384525202350090>"
            errors += f"⚠ Database Delete Alert: {name}\n"
        await asyncio.sleep(2)
        embed.remove_field(-1)
        embed.add_field(name = f"{name} Database",value = f"Upload: {set1}\nDownload: {get1}\nDelete: {delete1}")
        await message.edit(embed = embed)
    embed.title = "Check Complete!"
    embed.set_footer(text = EmptyEmbed)
    await message.edit(embed = embed)

    timestamp = "<t:" + str(int(time.time())) + ":F>"
    timestamp2 = "<t:" + str(int(time.time())) + ":R>"
    
    if errors == "":
        await channel.send(embed = discord.Embed(description = f"No errors found! Checking again in: 30 minutes\nCompleted At: {timestamp} | {timestamp2}"))
    else:
        await channel.send("<@&847289699487580161>",embed = discord.Embed(title = "Bot has dectected errors!",description = errors + f"\nCompleted At: {timestamp} | {timestamp2}"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.guild: # message is not DM
        mention = f'<@!{client.user.id}>'
        if mention == message.content:
            prefix = get_prefix(client,message)
            if prefix:
                embed = discord.Embed(title="Hello!",description=f"The prefix in this server is: `{prefix}`", color=discord.Color.green())
            else:
                embed = discord.Embed(title="Hello!",description=f"It seems like this server is not set up! Run `@Oasis Bot setup` to get started.", color=discord.Color.green())
            await message.reply(embed =embed,mention_author = False)
        elif message.content == mention + " setup":
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            if not ref.child(str(message.guild.id)).get():
                serverconf = {'dj': None, 'event': None, 'giveaway': None, 'mod': [None], 'modtrack': [None], 'pchannels': [None], 'prefix': 'o!'}

                ref.child(str(message.guild.id)).set(serverconf)
                embed = discord.Embed(title="All set up!",description=f"You are all set up! The default prefix is `o!`", color=discord.Color.green())
            else:
                embed = discord.Embed(title="Uh oh",description=f"It looks like this server is already set up!", color=discord.Color.green())
            await message.reply(embed =embed,mention_author = False)
        else:
            await client.process_commands(message)
    else:
        await message.reply("Commands are not allowed in dms!",mention_author = False)


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

# cogs loading on startup
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
'''
if beta:
    for filename in os.listdir('./betacogs'):
        if filename.endswith('.py'):
            client.load_extension(f'betacogs.{filename[:-3]}')
'''


client.load_extension("jishaku")

if beta:
    client.run(sensitive.BETA_BOT_TOKEN)
else:
    client.run(sensitive.BOT_TOKEN)
