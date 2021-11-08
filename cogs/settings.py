
import discord
from discord.ext import commands
import json
import datetime
import firebase_admin
from firebase_admin import db
import re
if not 'settings' in firebase_admin._apps:
    cred_obj = firebase_admin.credentials.Certificate('settings-83ab4-firebase-adminsdk-n0tlg-10871c6e45.json')
    default_app = firebase_admin.initialize_app(cred_obj , {
        'databaseURL':'https://settings-83ab4-default-rtdb.firebaseio.com/'
        },name="settings")

class Configure(commands.Cog):
    """
        Settings for the bot. There is a lot of things to change and setup, so use help commands to navigate your way through. You need manage server perms to set anything up.
    """

    def __init__(self,client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Settings Cog Loaded.')

    

    async def add_modtrack_role(self,ctx,role):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        mods = ref.child(str(ctx.message.guild.id)).child('modtrack').get()
        if not mods == None:
            if len(mods) >= 5:
                await ctx.reply('You cannot have more than 5 mod roles!')
            elif int(role) in mods:
                await ctx.reply('It seems this role is already a mod track role.')
            else:
                mods.append(int(role))
                ref.child(str(ctx.message.guild.id)).child('modtrack').set(mods)
                emb = discord.Embed(title="Mod Track Role added",
                                    description=f"Sucessfully added <@&{role}> as a mod track role.",
                                    color=discord.Color.green())
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
                await ctx.reply(embed=emb)
        else:
            mods = [role]
            ref.child(str(ctx.message.guild.id)).child('modtrack').set(mods)
            emb = discord.Embed(title="Mod Track Role added",
                                description=f"Sucessfully added <@&{role}> as a mod track role.",
                                color=discord.Color.green())
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed=emb)

    async def remove_modtrack_role(self,ctx,role):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        mods = ref.child(str(ctx.message.guild.id)).child('modtrack').get()

        if not role in mods:
            await ctx.reply('That role is not a current mod track role.')
        else:
            mods.remove(int(role))
            ref.child(str(ctx.message.guild.id)).child('modtrack').set(mods)
            emb = discord.Embed(title="Mod Track Role added",
                                description=f"Sucessfully removed <@&{role}> from mod track roles.",
                                color=discord.Color.green())
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed=emb)

    async def add_mod_role(self,ctx,role):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        mods = ref.child(str(ctx.message.guild.id)).child('mod').get()

        if not mods == None:
            if len(mods) >= 5:
                await ctx.reply('You cannot have more than 5 mod roles!')
            elif int(role) in mods:
                await ctx.reply('It seems this role is already a mod role.')
            else:
                mods.append(int(role))
                ref.child(str(ctx.message.guild.id)).child('mod').set(mods)
                emb = discord.Embed(title="Mod Role added",
                                    description=f"Sucessfully added <@&{role}> as a mod role.",
                                    color=discord.Color.green())
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
                await ctx.reply(embed=emb)
        else:
            mods = [role]
            ref.child(str(ctx.message.guild.id)).child('mod').set(mods)
            
            emb = discord.Embed(title="Mod Role added",
                                description=f"Sucessfully added <@&{role}> as a mod role.",
                                color=discord.Color.green())
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed=emb)

    async def remove_mod_role(self,ctx,role):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        mods = ref.child(str(ctx.message.guild.id)).child('mod').get()

        if not role in mods:
            await ctx.reply('That role is not a current mod role.')
        else:
            mods.remove(int(role))
            ref.child(str(ctx.message.guild.id)).child('mod').set(mods)
            emb = discord.Embed(title="Mod Role remove",
                                description=f"Sucessfully removed <@&{role}> from mod roles.",
                                color=discord.Color.green())
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed=emb)

    async def add_snipe_role(self,ctx,role):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        snipers = ref.child(str(ctx.message.guild.id)).child('sniper').get()

        if not snipers == None:
            if len(snipers) >= 5:
                await ctx.reply('You cannot have more than 5 snipe roles!')
            elif int(role) in snipers:
                await ctx.reply('It seems this role is already a sniper role.')
            else:
                snipers.append(int(role))
                ref.child(str(ctx.message.guild.id)).child('sniper').set(snipers)
                emb = discord.Embed(title="Sniper Role added",
                                    description=f"Sucessfully added <@&{role}> as a sniper role.",
                                    color=discord.Color.green())
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
                await ctx.reply(embed=emb)
        else:
            snipers = [role]
            ref.child(str(ctx.message.guild.id)).child('sniper').set(snipers)
            emb = discord.Embed(title="Sniper Role added",
                                    description=f"Sucessfully added <@&{role}> as a sniper role.",
                                    color=discord.Color.green())
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed=emb)

    async def remove_snipe_role(self,ctx,role):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        snipers = ref.child(str(ctx.message.guild.id)).child('sniper').get()

        if not role in snipers:
            await ctx.reply('That role is not a current sniper role.')
        else:
            snipers.remove(int(role))
            ref.child(str(ctx.message.guild.id)).child('sniper').set(snipers)
            emb = discord.Embed(title="Sniper Role remove",
                                description=f"Sucessfully removed <@&{role}> from sniper roles.",
                                color=discord.Color.green())
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed=emb)

    async def set_snipe_cd(self,ctx,cd):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        ref.child(str(ctx.message.guild.id)).child('snipecd').set(cd)

        emb = discord.Embed(title="Sniper Cooldown Set",
                                description=f"Sucessfully set snipe cooldown to `{cd}` seconds.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_snipe_cd(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        ref.child(str(ctx.message.guild.id)).child('snipecd').set({})

        emb = discord.Embed(title="Sniper Cooldown Removed",
                                description=f"Sucessfully removed snipe cooldown.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_snipe_lookback(self,ctx,lookback):
        if lookback <= 0:
            return await ctx.reply("Hey, I think that number needs to be positive.")
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        ref.child(str(ctx.message.guild.id)).child('snipelb').set(lookback)

        emb = discord.Embed(title="Sniper Lookback Set",
                                description=f"Sucessfully set snipe lookback to `{lookback}` messages.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_snipe_lookback(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        ref.child(str(ctx.message.guild.id)).child('snipelb').set({})

        emb = discord.Embed(title="Sniper Lookback Removed",
                                description=f"Sucessfully removed snipe lookback.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def add_pchannel(self,ctx,category):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        categories = ref.child(str(ctx.message.guild.id)).child('pchannels').get()

        if categories:
            if len(categories) >= 5:
                await ctx.reply('You cannot have more than 5 private channel categories!')
            elif int(category) in categories:
                await ctx.reply('It seems this category is already a private channel category.')
            else:
                categories.append(int(category))
                ref.child(str(ctx.message.guild.id)).child('pchannels').set(categories)
                emb = discord.Embed(title="Private Channel Category added",
                                    description=f"Sucessfully added <#{category}> as a private channels category.",
                                    color=discord.Color.green())
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
                await ctx.reply(embed=emb)
        else:
            categories = [int(category)]
            ref.child(str(ctx.message.guild.id)).child('pchannels').set(categories)
            emb = discord.Embed(title="Private Channel Category added",
                                    description=f"Sucessfully added <#{category}> as a private channels category.",
                                    color=discord.Color.green())
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed=emb)

    async def remove_pchannel(self,ctx,category):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        categories = ref.child(str(ctx.message.guild.id)).child('pchannels').get()

        if not category in categories:
            await ctx.reply('That category is not a current private channels category.')
        else:
            categories.remove(int(category))
            ref.child(str(ctx.message.guild.id)).child('pchannels').set(categories)
            emb = discord.Embed(title="Mod Track Role remove",
                                description=f"Sucessfully removed <#{category}> from mod roles.",
                                color=discord.Color.green())
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed=emb)

    async def set_prefix(self,ctx,prefix):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        if len(prefix) >= 4:
            await ctx.reply('You cannot have a prefix longer than 3 characters!')
        else:
            ref.child(str(ctx.message.guild.id)).child('prefix').set(prefix)
            emb = discord.Embed(title="Bot prefix changed",
                                description=f"Sucessfully changed prefix to `{prefix}`.",
                                color=discord.Color.green())
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed=emb)

    async def set_dj(self,ctx,dj):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('dj').set(int(dj))
        emb = discord.Embed(title="Dj Role Set",
                                description=f"Sucessfully changed the dj role to <@&{dj}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_dj(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('dj').set({})
        emb = discord.Embed(title="Removed DJ Role",
                                description=f"Sucessfully removed the dj role.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_default(self,ctx,default):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('dheistdrole').set(int(default))
        emb = discord.Embed(title="Default Server Role Set",
                                description=f"Sucessfully changed the default role to <@&{default}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_default(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('dheistdrole').set({})
        emb = discord.Embed(title="Removed Default Server Role",
                                description=f"Sucessfully removed the default role.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_lottery(self,ctx,lottery):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('lottery').set(int(lottery))
        emb = discord.Embed(title="Lottery Mod Role Set",
                                description=f"Sucessfully changed the lottery mod role to <@&{lottery}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_lottery(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('lottery').set({})
        emb = discord.Embed(title="Removed Lottery Mod Role",
                                description=f"Sucessfully removed the lottery mod role.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_event(self,ctx,event):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('event').set(int(event))
        emb = discord.Embed(title="Event Manager Role Set",
                                description=f"Sucessfully changed the event manager role to <@&{event}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_event(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('event').set({})
        emb = discord.Embed(title="Removed Event Manager Role",
                                description=f"Sucessfully removed the event manager role.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_giveaway(self,ctx,giveaway):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('giveaway').set(int(giveaway))
        emb = discord.Embed(title="Event Manager Role Set",
                                description=f"Sucessfully changed the giveaway manager role to <@&{giveaway}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_giveaway(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('giveaway').set({})
        emb = discord.Embed(title="Removed Giveaway Manager Role",
                                description=f"Sucessfully removed the giveaway manager role.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_eping(self,ctx,eping):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('eping').set(int(eping))
        emb = discord.Embed(title="Event Ping Role Set",
                                description=f"Sucessfully changed the event ping role to <@&{eping}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_eping(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('eping').set({})
        emb = discord.Embed(title="Removed Event Ping Role",
                                description=f"Sucessfully removed the event ping role.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_echannel(self,ctx,echannel):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('echannel').set(int(echannel))
        emb = discord.Embed(title="Event Channel Set",
                                description=f"Sucessfully changed the event channel to <#{echannel}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_echannel(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('echannel').set({})
        emb = discord.Embed(title="Removed Event Channel Setting",
                                description=f"Sucessfully removed the event channel.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_flog(self,ctx,fchannel):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('flogging').set(int(fchannel))

        emb = discord.Embed(title="Freeloader Logging Channel Set",
                                description=f"Sucessfully changed the freeloading log channel to <#{fchannel}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_flog(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('flogging').set({})
        emb = discord.Embed(title="Removed Freeloader Logging Channel",
                                description=f"Sucessfully removed the freeloader logging channel.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_glog(self,ctx,gchannel):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('glogging').set(int(gchannel))

        emb = discord.Embed(title="Giveaway Logging Channel Set",
                                description=f"Sucessfully changed the giveaway log channel to <#{gchannel}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_glog(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('glogging').set({})
        emb = discord.Embed(title="Removed Giveaway Logging Channel",
                                description=f"Sucessfully removed the giveaway logging channel.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_elog(self,ctx,echannel):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('elogging').set(int(echannel))

        emb = discord.Embed(title="Event Manager Logging Channel Set",
                                description=f"Sucessfully changed the event logging channel to <#{echannel}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_elog(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('elogging').set({})
        emb = discord.Embed(title="Removed Event Manager Logging Channel",
                                description=f"Sucessfully removed the event logging channel.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_mlog(self,ctx,mchannel):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('mlogging').set(int(mchannel))

        emb = discord.Embed(title="Mod Tracking Logging Channel Set",
                                description=f"Sucessfully changed the mod track log channel to <#{mchannel}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_mlog(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('mlogging').set({})
        emb = discord.Embed(title="Removed Mod Tracking Logging Channel",
                                description=f"Sucessfully removed the mod track logging channel.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def set_ilog(self,ctx,ichannel):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('ilogging').set(int(ichannel))

        emb = discord.Embed(title="Invite Tracking Channel Set",
                                description=f"Sucessfully changed the invite track channel to <#{ichannel}>.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_ilog(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        ref.child(str(ctx.message.guild.id)).child('ilogging').set({})
        emb = discord.Embed(title="Removed Invite Tracking Channel",
                                description=f"Sucessfully removed the invite track channel.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def add_dono_role(self,ctx,amount,role):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        roles = ref.child(str(ctx.message.guild.id)).child('groles').get()

        if roles:
            roles[str(amount)] = role
        else:
            roles = {str(amount):role}

        roles = ref.child(str(ctx.message.guild.id)).child('groles').set(roles)

        emb = discord.Embed(title="Donation Role Added",
                                description=f"Sucessfully added <@&{role}> as the role for `{amount}`.",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def remove_dono_role(self,ctx,amount):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        roles = ref.child(str(ctx.message.guild.id)).child('groles').get()

        if roles:
            if str(amount) in roles:
                roles.pop(str(amount))
            else:
                return await ctx.reply("Doesn't seem like you have that donation amount set up.")
        else:
            return await ctx.reply("You do not have any donation roles set up. What are you trying to do?")

        roles = ref.child(str(ctx.message.guild.id)).child('groles').set(roles)

        emb = discord.Embed(title="Donation Role Removed",
                                description=f"Sucessfully removed the donation role for `{amount}`",
                                color=discord.Color.green())
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    async def view_settings(self,ctx,category):
        ref = db.reference("/",app = firebase_admin._apps['settings'])

        guild_settings = ref.child(str(ctx.message.guild.id)).get()
        emb = discord.Embed(title=f"{category.capitalize()} Settings for {ctx.message.guild.name}",
                                color=discord.Color.blue())

        if category == "event":
            try:
                store = guild_settings['event']
                eman = f'<@&{store}>'
            except:
                eman = None
            try:
                store = guild_settings['eping']
                eping = f'<@&{store}>'
            except:
                eping = None
            try:
                store = guild_settings['echannel']
                echannel = f'<#{store}>'
            except:
                echannel = None
            try:
                store = guild_settings['elogging']
                elog = f'<#{store}>'
            except:
                elog = None

            emb.add_field(name = "Event Manager Role",value = f'This role specifies an event manager, who can start events and use event commands.\n**Server Setting:** {eman}',inline = False)
            emb.add_field(name = "Event Ping Role",value = f'This role specifies a ping role on the use of `o!estart`\n**Server Setting:** {eping}',inline = False)
            emb.add_field(name = "Event Channel",value = f'This channel specifies where an event manager can use `o!estart`\n**Server Setting:** {echannel}',inline = False)
            emb.add_field(name = "Event Manager Logging",value = f'This channel specifies where embeds will be send on the use of `o!estart` (indicating a event).\n**Server Settings:** {elog}')
        elif category == "moderation":
            try:
                store = guild_settings['mod']
                mod = ""
                for role in store:
                    mod += "\n<@&" + str(role) + ">"
            except:
                mod = None
            try:
                store = guild_settings['modtrack']
                modtrack = ""
                for role in store:
                    modtrack += "\n<@&" + str(role) + ">"
            except:
                modtrack = None
            
            emb.add_field(name = "Mod Role",value = f'This role specifies a mod, who can use the modlogs and warn commands.\n**Server Setting:** {mod}',inline = False)
            emb.add_field(name = "Modtrack Role",value = f'This role specifies who can use the action tracking features.\n**Server Setting:** {modtrack}',inline = False)
        elif category == "music":
            try:
                store = guild_settings['dj']
                dj = f'<@&{store}>'
            except:
                dj = None
            
            emb.add_field(name = "DJ Role",value = f'This role specifies who can use the DJ commands with music.\n**Server Setting:** {dj}',inline = False)
        elif category == "giveaway":
            try:
                store = guild_settings['giveaway']
                giveaway = f'<@&{store}>'
            except:
                giveaway = None
            try:
                store = guild_settings['glogging']
                glog = f'<#{store}>'
            except:
                glog = None
            try:
                store = guild_settings['groles']
                groles = ""
                for role in store:
                    groles += f"\n`{role}` : <@&{store[role]}>"
            except:
                groles = None

            emb.add_field(name = "Giveaway Manager Role",value = f'This role specifies a giveaway manager, who can use the giveaway utility commands, as well as `o!drop`.\n**Server Setting:** {giveaway}',inline = False)
            emb.add_field(name = "Giveaway Manager Logging",value = f'This channel specifies where embeds will be send everyuserinput a donation is added (indicating a gaw).\n**Server Settings:** {glog}',inline = False)
            emb.add_field(name = "Giveaway Role Assigning",value = f'These roles specify the donation roles to add when a user reaches a certain donation value.\n**Server Settings:** {groles}')
        elif category == "private channels":
            try:
                store = guild_settings['pchannels']
                pchannels = ""
                for category in store:
                    pchannels += "\n<#" + str(category) + ">"
            except:
                pchannels = None

            emb.add_field(name = "Private Channel Categories",value = f'These categories define where private channel commands can be used.\n**Server Setting:** {pchannels}',inline = False)
        elif category == "freeloader":
            try:
                store = guild_settings['flogging']
                flog = f'<#{store}>'
            except:
                flog = None

            emb.add_field(name = "Freeloader Logging",value = f'This channel specifies where embeds will be send when a suspected freeloader leaves the server.\n**Server Settings:** {flog}')
        elif category == "modtrack":
            try:
                store = guild_settings['modtrack']
                mod = ""
                for role in store:
                    mod += "\n<@&" + str(role) + ">"
            except:
                mod = None

            try:
                store = guild_settings['mlogging']
                mlog = f'<#{store}>'
            except:
                mlog = None

            emb.add_field(name = "Mod Role",value = f'This role specifies a mod, who can use the modtracking commands to log their actions.\n**Server Setting:** {mod}',inline = False)
            emb.add_field(name = "Mod Tracking Channel",value = f'This channel specifies where embeds will be sent when a mod logs someuserinput using `o!logaction`.\n**Server Settings:** {mlog}')
        elif category == "sniper":
            try:
                sniperoles = ref.child(str(ctx.message.guild.id)).child('sniper').get()
                roles = ""
                for role in sniperoles:
                    roles += f"\n<@&{role}>"
            except:
                roles = None

                        
            snipelookback = ref.child(str(ctx.message.guild.id)).child('snipelb').get() or None
            snipecooldown = ref.child(str(ctx.message.guild.id)).child('snipecd').get() or None


            emb.add_field(name = "Sniping Roles",value = f'These roles indicates who can use the snipe commands. Be aware they are very op and may expose sensitive information.\n**Server Settings:** {roles}',inline = False)
            emb.add_field(name = "Sniping Lookback",value = f'This number indicates how many messages will be saved in the sniping database before old ones are removed.\n**Server Settings:** {snipelookback}',inline = False)
            emb.add_field(name = "Sniping Cooldown",value = f'This number indicates how long a message will linger in the snipe database until it is removed.\n**Server Settings:** {snipecooldown}',inline = False)
        elif category == "invites":
            try:
                store = guild_settings['ilogging']
                ilog = f'<#{store}>'
            except:
                ilog = None

            emb.add_field(name = "Invite Tracking Channel",value = f'This channel specifies where embeds will be sent when person leaves or joins the server.\n**Server Settings:** {ilog}')
        elif category == "dank":
            try:
                store = guild_settings['dheistdrole']
                dheistdrole = f'<@&{store}>'
            except:
                dheistdrole = None

            try:
                store = guild_settings['lottery']
                lotterymod = f'<@&{store}>'
            except:
                lotterymod = None

            emb.add_field(name = "Dank Heist Default Role",value = f'This role indicates the role to which channel viewage is locked on a dank heist command. Usually set to a server access role, leave it unset to lock viewage to everyone role.\n**Server Settings:** {dheistdrole}',inline = False)
            emb.add_field(name = "Dank Lottery Mod Role",value = f'This role indicates who can start, end, cancel, and manage entries to a dank lottery with lottery category.\n**Server Settings:** {lotterymod}',inline = False)
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed=emb)

    @commands.group(description = "Manage All Settings",help = "settings <option>",brief = "This command manages all configurable settings in the bot. Any user input that can have multiple options can be set using `add`, whild `set` will set any user input that is set to one option. You can remove any setting using `remove`. Try using `o!help settings <subcommand>` to see what you can configure.")
    async def settings(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('You did not select a setting to change!')

    @settings.group(description = "Set a specified setting",help = "settings set <setting>")
    async def set(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('You did not select a role or channel to change!\nTry using `o!help settings set` to see what you can set.')

    @settings.group(description = "Add a role or category",help = "settings add <setting>")
    async def add(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('You did not select a role or category to add!\nTry using `o!help settings add` to see what you can add.')
    
    @settings.group(description = "Remove a role or category",help = "settings remove <setting>")
    async def remove(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('You did not select a role or category to remove!\nTry using `o!help settings remove` to see what you can add.')

    @settings.group(description = "View your settings about a category",help = "settings view <category>")
    async def view(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('You did not select a category to view!\nTry using `o!help settings view` to see what you can view.')

    @set.command(description = "Change the bot prefix for this server",help = "settings set prefix <prefix>")
    @commands.has_permissions(manage_guild = True) 
    async def prefix(self,ctx,prefix):
        await self.set_prefix(ctx,prefix)

    @set.command(description = "Change the dj role for the server.",help = "settings set dj <role>")
    @commands.has_permissions(manage_guild = True) 
    async def dj(self,ctx,role : discord.Role):
        await self.set_dj(ctx,int(role.id))

    @remove.command(name = "dj",description = "Remove the dj role for the server.",help = "settings remove dj")
    @commands.has_permissions(manage_guild = True)
    async def djremove(self,ctx):
        await self.remove_dj(ctx)

    @set.command(description = "Change the default role for the server.",help = "settings set defaultrole <role>",brief = "This is used for the `dankheist` command to lock access to the heist channel from the general public. Recommend setting this role to a server access role.")
    @commands.has_permissions(manage_guild = True) 
    async def defaultrole(self,ctx,role : discord.Role):
        await self.set_default(ctx,int(role.id))

    @remove.command(name = "defaultrole",description = "Remove the default role for the server.",help = "settings remove defaultrole")
    @commands.has_permissions(manage_guild = True)
    async def defaultremove(self,ctx):
        await self.remove_default(ctx)

    @set.command(description = "Change the lottery mod role for the server.",help = "settings set lotterymod <role>")
    @commands.has_permissions(manage_guild = True) 
    async def lotterymod(self,ctx,role : discord.Role):
        await self.set_lottery(ctx,int(role.id))

    @remove.command(name = "lotterymod",description = "Remove the default role for the server.",help = "settings remove lotterymod")
    @commands.has_permissions(manage_guild = True)
    async def lotteryremove(self,ctx):
        await self.remove_lottery(ctx)

    @set.command(description = "Change the event manager role for the server.",help = "settings set eventmanager <role>")
    @commands.has_permissions(manage_guild = True) 
    async def eventmanager(self,ctx,role : discord.Role):
        await self.set_event(ctx,int(role.id))

    @remove.command(name = "eventmanager",description = "Remove the event manager role for the server.",help = "settings remove eventmanager")
    @commands.has_permissions(manage_guild = True)
    async def eventremove(self,ctx):
        await self.remove_event(ctx)

    @set.command(description = "Change the event ping role for the server.",help = "settings set eventping <role>")
    @commands.has_permissions(manage_guild = True) 
    async def eventping(self,ctx,role : discord.Role):
        await self.set_eping(ctx,int(role.id))

    @remove.command(name = "eventping",description = "Remove the event ping role for the server.",help = "settings remove eventping")
    @commands.has_permissions(manage_guild = True)
    async def pingremove(self,ctx):
        await self.remove_eping(ctx)

    @set.command(description = "Change the event annoucement channel for the server.",help = "settings set eventchannel <channel>")
    @commands.has_permissions(manage_guild = True) 
    async def eventchannel(self,ctx,channel : discord.TextChannel):
        await self.set_echannel(ctx,int(channel.id))

    @remove.command(name = "eventchannel",description = "Remove the event annoucement channel for the server.",help = "settings remove eventchannel")
    @commands.has_permissions(manage_guild = True)
    async def eventchannelremove(self,ctx):
        await self.remove_echannel(ctx)

    @set.command(description = "Change the giveaway logging channel for the server.",help = "settings set giveawaylog <channel>")
    @commands.has_permissions(manage_guild = True) 
    async def giveawaylog(self,ctx,channel : discord.TextChannel):
        await self.set_glog(ctx,int(channel.id))

    @remove.command(name = "giveawaylog",description = "Remove the giveaway log channel for the server.",help = "settings remove giveawaylog")
    @commands.has_permissions(manage_guild = True)
    async def glogremove(self,ctx):
        await self.remove_glog(ctx)

    @set.command(description = "Change the mod tracking logging channel for the server.",help = "settings set modtracklog <channel>")
    @commands.has_permissions(manage_guild = True) 
    async def modtracklog(self,ctx,channel : discord.TextChannel):
        await self.set_mlog(ctx,int(channel.id))

    @remove.command(name = "modtracklog",description = "Remove the mod tracking logging channel for the server.",help = "settings remove modtracklog")
    @commands.has_permissions(manage_guild = True)
    async def mlogremove(self,ctx):
        await self.remove_mlog(ctx)

    @set.command(description = "Change the invite tracking channel for the server.",help = "settings set invitelog <channel>")
    @commands.has_permissions(manage_guild = True) 
    async def invitelog(self,ctx,channel : discord.TextChannel):
        await self.set_ilog(ctx,int(channel.id))

    @remove.command(name = "invitelog",description = "Remove the invite tracking channel for the server.",help = "settings remove invitelog")
    @commands.has_permissions(manage_guild = True)
    async def ilogremove(self,ctx):
        await self.remove_ilog(ctx)

    @set.command(description = "Change the event logging channel for the server.",help = "settings set eventlog <channel>")
    @commands.has_permissions(manage_guild = True) 
    async def eventlog(self,ctx,channel : discord.TextChannel):
        await self.set_elog(ctx,int(channel.id))

    @remove.command(name = "eventlog",description = "Remove the event logging channel for the server.",help = "settings remove eventlog")
    @commands.has_permissions(manage_guild = True)
    async def elogremove(self,ctx):
        await self.remove_elog(ctx)

    @set.command(description = "Change the freeloader logging channel for the server.",help = "settings set freeloaderlog <channel>")
    @commands.has_permissions(manage_guild = True) 
    async def freeloaderlog(self,ctx,channel : discord.TextChannel):
        await self.set_flog(ctx,int(channel.id))

    @remove.command(name = "freeloaderlog",description = "Remove the freeloader logging channel for the server.",help = "settings remove freeloaderlog")
    @commands.has_permissions(manage_guild = True)
    async def flogremove(self,ctx):
        await self.remove_flog(ctx)

    @set.command(description = "Change the giveaway manager role for the server.",help = "settings set giveawaymanager <role>")
    @commands.has_permissions(manage_guild = True) 
    async def giveawaymanager(self,ctx,role : discord.Role):
        await self.set_giveaway(ctx,int(role.id))

    @remove.command(name = "giveawaymanager",description = "Remove the giveaway manager role for the server.",help = "settings remove giveawaymanager")
    @commands.has_permissions(manage_guild = True)
    async def giveawayremove(self,ctx):
        await self.remove_giveaway(ctx)

    @add.command(name = "mod",description = "Add a mod role for the server.",help = "settings add mod <role>")
    @commands.has_permissions(manage_guild = True) 
    async def modadd(self,ctx,role : discord.Role):
        await self.add_mod_role(ctx,int(role.id))

    @remove.command(name = "mod",description = "Remove a mod role for the server.",help = "settings remove mod <role>")
    @commands.has_permissions(manage_guild = True) 
    async def modremove(self,ctx,role : discord.Role):
        await self.remove_mod_role(ctx,int(role.id))

    @add.command(name = "sniper",description = "Add a sniping role for the server.",help = "settings add sniper <role>")
    @commands.has_permissions(manage_guild = True) 
    async def sniperadd(self,ctx,role : discord.Role):
        await self.add_snipe_role(ctx,int(role.id))

    @remove.command(name = "sniper",description = "Remove a sniping role for the server.",help = "settings remove sniper <role>")
    @commands.has_permissions(manage_guild = True) 
    async def sniperremove(self,ctx,role : discord.Role):
        await self.remove_snipe_role(ctx,int(role.id))

    @set.command(name = "snipelookback",description = "Sets the amount of messages the bot will snipe back to.",help = "settings set snipelookback <message amount>"
        ,brief = "If you only want the bot to see the most recent delete message in the channel, you would set the lookback to 1. If you want the bot to see two messages back, set it to 2 and so on.")
    @commands.has_permissions(manage_guild = True)
    async def snipelookbackset(self,ctx,lookback : int):
        await self.set_snipe_lookback(ctx,lookback)

    @remove.command(name = "snipelookback",description = "Removes the snipelookback amount, allowing the bot to see infintely backwards in snipe commands (unless you have a time cd set)."
        ,help = "settings remove snipelookback")
    @commands.has_permissions(manage_guild = True)
    async def snipelookbackremove(self,ctx):
        await self.remove_snipe_lookback(ctx)

    @set.command(name = "snipecooldown",description = "Set the cooldown for snipe. See documentation for more info.",help = "settings set snipecooldown <time>",
        brief = "This time is the amount of time before the bot deletes the sniped message from storage. Default is 30 seconds, and max time is 6 hours.\n" + 
        "\n**Example:**\n`o!settings set snipecooldown 10`\n`o!settings set snipecooldown 1h`")
    @commands.has_permissions(manage_guild = True) 
    async def snipecooldownset(self,ctx,time):
        try:
            timeunit = time[-1]
            seconds = 0
            if timeunit.isalpha():
                if timeunit.lower() == "s":
                    seconds = int(time[:-1])
                elif timeunit.lower() == "m":
                    seconds = int(time[:-1]) * 60
                elif timeunit.lower() == "h":
                    seconds = int(time[:-1]) * 60 * 60
                else:
                    return await ctx.reply("I could not process your input! Please try again.")
            else:
                seconds = time
            seconds = int(seconds)
            if seconds > 21600:
                return await ctx.reply("Wait a minute, you can't set the snipe cooldown over 6 hours.")
            elif seconds <= 0:
                return await ctx.reply("Wait a minute, you have to have a positive snipe cooldown.")
        except:
            return await ctx.reply("I could not process your input! Please try again.")

        await self.set_snipe_cd(ctx,seconds)
    
    @remove.command(name = "snipecooldown",description = "Remove the snipe cooldown setting, which resets back to 30 seconds.",help = "settings remove snipecooldown")
    @commands.has_permissions(manage_guild = True) 
    async def snipecooldownremove(self,ctx):
        await self.remove_snipe_cd(ctx)

    @add.command(name = "modtrack" ,description = "Add a mod tracking role for the server.",help = "settings add modtrack <role>")
    @commands.has_permissions(manage_guild = True) 
    async def modtrackadd(self,ctx,role : discord.Role):
        await self.add_modtrack_role(ctx,int(role.id))

    @remove.command(name = "modtrack", description = "Remove a mod tracking role for the server.",help = "settings remove modtrack <role>")
    @commands.has_permissions(manage_guild = True) 
    async def modtrackremove(self,ctx,role : discord.Role):
        await self.remove_modtrack_role(ctx,int(role.id))

    @add.command(name = "pchannel", description = "Add a private channel category for the server.",help = "settings add pchannel <category>")
    @commands.has_permissions(manage_guild = True) 
    async def privatechannelcategoryadd(self,ctx,category: discord.CategoryChannel):
        await self.add_pchannel(ctx,int(category.id))

    @remove.command(name = "pchannel", description = "Remove a private channel category for the server.",help = "settings remove pchannel <category>")
    @commands.has_permissions(manage_guild = True) 
    async def privatechannelcategoryremove(self,ctx,category: discord.CategoryChannel):
        await self.remove_pchannel(ctx,int(category.id))

    @view.command(name = "event",description = "View event settings for the server.",help = "settings view event")
    @commands.has_permissions(manage_guild = True)
    async def viewevent(self,ctx):
        await self.view_settings(ctx,"event")

    @view.command(name = "invites",description = "View invites settings for the server.",help = "settings view invites")
    @commands.has_permissions(manage_guild = True)
    async def viewinvites(self,ctx):
        await self.view_settings(ctx,"invites")

    @view.command(name = "moderation",description = "View moderation settings for the server.",help = "settings view moderation")
    @commands.has_permissions(manage_guild = True)
    async def viewmoderation(self,ctx):
        await self.view_settings(ctx,"moderation")

    @view.command(name = "music",description = "View music settings for the server.",help = "settings view music")
    @commands.has_permissions(manage_guild = True)
    async def viewmusic(self,ctx):
        await self.view_settings(ctx,"music")

    @view.command(name = "giveaway",description = "View giveaway settings for the server.",help = "settings view giveaway")
    @commands.has_permissions(manage_guild = True)
    async def viewgiveaway(self,ctx):
        await self.view_settings(ctx,"giveaway")

    @view.command(name = "privatechannels",description = "View private channel settings for the server.",help = "settings view privatechannels")
    @commands.has_permissions(manage_guild = True)
    async def viewprivatechannels(self,ctx):
        await self.view_settings(ctx,"private channels")

    @view.command(name = "freeloader",description = "View freeloader settings for the server.",help = "settings view freeloader")
    @commands.has_permissions(manage_guild = True)
    async def viewfreeloader(self,ctx):
        await self.view_settings(ctx,"freeloader")

    @view.command(name = "modtrack",description = "View modtrack settings for the server.",help = "settings view modtrack")
    @commands.has_permissions(manage_guild = True)
    async def viewmodtrack(self,ctx):
        await self.view_settings(ctx,"modtrack")

    @view.command(name = "sniper",description = "View sniper settings for the server.",help = "settings view sniper")
    @commands.has_permissions(manage_guild = True)
    async def viewsniper(self,ctx):
        await self.view_settings(ctx,"sniper")

    @view.command(name = "dank",description = "View dank memer settings for the server.",help = "settings view dank")
    @commands.has_permissions(manage_guild = True)
    async def viewdank(self,ctx):
        await self.view_settings(ctx,"dank")

    @add.command(name = "donorole", description = "Add a donation role for the server.",help = "settings add donorole <amount> <role>")
    @commands.has_permissions(manage_guild = True) 
    async def donatorroleadd(self,ctx,amount,role : discord.Role):
        try:
            amount = int(float(amount))
        except:
            return await ctx.reply("That does not look like a valid donation amount.")

        member = ctx.guild.get_member(self.client.user.id)
        top_role = member.top_role
        if ctx.author.top_role <= role:
            return await ctx.reply("Hold up, are you trying to exploit here? You can't assign a donation role that is higher or equal to your top role. Nice try.")
        elif top_role <= role:
            return await ctx.reply("Hold up, I can't even assign that role, since my position in the role hierarchy is lower than or equal to the role you want to assign.")

        await self.add_dono_role(ctx,amount,role.id)

    @remove.command(name = "donorole", description = "Remove a donation role for the server.",help = "settings remove donorole <amount>")
    @commands.has_permissions(manage_guild = True) 
    async def donatorroleremove(self,ctx,amount):
        try:
            amount = int(float(amount))
            
        except:
            return await ctx.reply("That does not look like a valid donation amount.")

        await self.remove_dono_role(ctx,amount)    

    @commands.command(description = "Enable certain commands for your server!",help = "enable <command> <user,role,channel,or all>",brief = "This command can help you enable commands for your server. Suppose that you disabled a command for everyone, but want your admin team to use it. You might use the command:\n" + 
        "`enable iq @Admin`\nOr if you want to enable the `iq` command for everyone everywhere, you can use\n`enable iq all`\nDo note that any sort of enable will override all disables for a command.")
    @commands.has_permissions(manage_guild = True) 
    async def enable(self,ctx,command,userinput):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        command = self.client.get_command(command)
        if not command:
            return await ctx.reply("That does not look like a valid command name!")
        if userinput == "all":
            if ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("aall").get():
                return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
            ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("aall").set(True)
            embed = discord.Embed(title = "Sucessfully Enabled!",description = f"Enabled the command **{command}** for everyone.")
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            return await ctx.reply(embed = embed)
        if not userinput.isnumeric():
            try:
                userinput = userinput.replace("<",'') 
                userinput = userinput.replace(">",'') 
                userinput = userinput.replace("@",'') 
                userinput = userinput.replace("!",'')
                userinput = userinput.replace("&",'')
                userinput = userinput.replace("#",'')
                userinput = int(userinput)
            except:
                return await ctx.reply("I could not process your input! Please try again.")
        else:
            userinput = int(userinput)
 
        guild = ctx.guild
        if guild.get_member(userinput):
            userinputobj = guild.get_member(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("ausers").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("ausers").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("ausers").set(store)
        elif guild.get_role(userinput):
            userinputobj = guild.get_role(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("aroles").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("aroles").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("aroles").set(store)
        elif guild.get_channel(userinput):
            userinputobj = guild.get_channel(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("achannels").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("achannels").set([userinput])
            else:
                store.append(userinput)
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("achannels").set(store)
        else:
            return await ctx.reply("I could not process your input! Please try again.")

        embed = discord.Embed(title = "Sucessfully Enabled!",description = f"Enabled the command **{command}** for {userinputobj.mention}.")
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)

    @commands.command(description = "Disable certain commands for your server!",help = "disable <command> <user,role,channel,or all>",brief = "This command can help you disable commands for your server. Say you do not want people spamming the `iq` command in your general chat. You can disable it using the following:\n" + 
        "`disable iq #general`\nOr if you want to disable the `iq` command for everyone everywhere, you can use\n`disable iq all`\nDo note that any sort of enable will override all disables for a command.")
    @commands.has_permissions(manage_guild = True) 
    async def disable(self,ctx,command,userinput):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        command = self.client.get_command(command)
        if not command:
            return await ctx.reply("That does not look like a valid command name!")
        if userinput == "all":
            if ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("dall").get():
                return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
            ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("dall").set(True)
            embed = discord.Embed(title = "Sucessfully Disabled!",description = f"Disabled the command **{command}** for everyone.")
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            return await ctx.reply(embed = embed)
        if not userinput.isnumeric():
            try:
                userinput = userinput.replace("<",'') 
                userinput = userinput.replace(">",'') 
                userinput = userinput.replace("@",'') 
                userinput = userinput.replace("!",'')
                userinput = userinput.replace("&",'')
                userinput = userinput.replace("#",'')
                userinput = int(userinput)
            except:
                return await ctx.reply("I could not process your input! Please try again.")
        else:
            userinput = int(userinput)
 
        guild = ctx.guild
        if guild.get_member(userinput):
            userinputobj = guild.get_member(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("dusers").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("dusers").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("dusers").set(store)
        elif guild.get_role(userinput):
            userinputobj = guild.get_role(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("droles").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("droles").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("droles").set(store)
        elif guild.get_channel(userinput):
            userinputobj = guild.get_channel(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("dchannels").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("dchannels").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child("dchannels").set(store)
        else:
            return await ctx.reply("I could not process your input! Please try again.")

        embed = discord.Embed(title = "Sucessfully Disabled!",description = f"Disabled the command **{command}** for {userinputobj.mention}.")
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)

    
    @commands.group(description = "Manage already exsisting command rules.",help = "rules [option]",brief = "This command allows you to view and edit exsisting rules. You can define rules by using `o!enable` or `o!disable`")
    @commands.has_permissions(manage_guild = True) 
    async def rules(self,ctx):
        if ctx.invoked_subcommand is None:
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            try:
                rules = ref.child(str(ctx.guild.id)).child("rules").get().keys()
            except AttributeError as error:
                return await ctx.reply("Does not seem like there are rules set up for this server.")
            rules = '\n'.join(rules)
            embed = discord.Embed(title = f"Rules and Permissions for {ctx.guild.name}",description = rules)

            await ctx.reply(embed = embed)

    @rules.command(name = "view",description = "View the rules of a certain command.",help = "rules view <command>",brief = "View all the rules for a certain command.")
    @commands.has_permissions(manage_guild = True) 
    async def viewrules(self,ctx,command):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        command = self.client.get_command(command)
        if not command:
            return await ctx.reply("That does not look like a valid command name!")
        settings = ref.child(str(ctx.guild.id)).child("rules").child(command.name).get()
        if not settings:
            return await ctx.reply("Seems like there aren't any rules for this command. Sometimes the command will have a custom check, you can check by exploring `o!help settings view`")
        aroles = settings.get("aroles",None)
        droles = settings.get("droles",None)
        achannels = settings.get("achannels",None)
        dchannels = settings.get("dchannels",None)
        ausers = settings.get("ausers",None)
        dusers = settings.get("dusers",None)
        aall = settings.get("aall",None)
        dall = settings.get("dall",None)

        embed = discord.Embed(title = f"Rules and Permissions for {command.name}")

        if aall:
            embed.add_field(name = f"**Enabled for All:**",value =  aall,inline = False)
        if dall:
            embed.add_field(name = f"**Disabled for All:**",value =  dall,inline = False)
        if aroles:
            embed.add_field(name = f"**Enabled Roles:** ",value = ' '.join(['<@&' + str(b) + '>' for b in aroles]),inline = False)
        if droles:
            embed.add_field(name = f"**Disabled Roles:**",value = ' '.join(['<@&' + str(b) + '>' for b in droles]),inline = False)
        if achannels:
            embed.add_field(name = f"**Enabled Channels:** ",value =' '.join(['<#' + str(b) + '>' for b in achannels]),inline = False)
        if dchannels:
            embed.add_field(name = f"**Disabled Channels:**",value = ' '.join(['<#' + str(b) + '>' for b in dchannels]),inline = False)
        if ausers:
            embed.add_field(name = f"**Enabled Users:** ",value =' '.join(['<@' + str(b) + '>' for b in ausers]),inline = False)
        if dusers:
            embed.add_field(name = f"**Disabled Users:** ",value =' '.join(['<@' + str(b) + '>' for b in dusers]),inline = False)

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)
    
    @rules.command(name = "remove",description = "Remove a certain rule",help = "rules remove <command> <enable or disable> <rule application> <application>",brief = "The syntax for this command is slightly confusing, but do not worry! Here are some examples:\n" + 
        "`o!rules remove help enable #general`\n> This will remove the rule that enables the command `help` in the general channel.\n\n" + 
        "`o!rules remove iq disable @Chu`\n> This will remove the rule that disables the command `iq` for the user Chu.\n\n" + 
        "`o!rules remove channelinfo enable all`\n> This will remove the rule that allows the command `channelinfo` to be run by all users.")
    @commands.has_permissions(manage_guild = True) 
    async def rulesremove(self,ctx,command,enabledisable,userinput1):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        if enabledisable == "enable":
            prefix = "a"
        elif enabledisable == "disable":
            prefix = "d"
        else:
            return await ctx.reply("Hey, you have to specify either `enable` or `disable`. Try again.")

        command = self.client.get_command(command)
        if not command:
            return await ctx.reply("That does not look like a valid command name!")
        if userinput1 == "all":
            if ref.child(str(ctx.guild.id)).child("rules").child(command.name).child(prefix +"all").get():
                ref.child(str(ctx.guild.id)).child("rules").child(command.name).child(prefix +"all").set({})
            else:
                return await ctx.reply(f"Hold up, this command does not have a rule for {enabledisable} all!")
            embed = discord.Embed(title = "Sucessfully Revmoed!",description = f"Revmoed the {enabledisable} rule for the command **{command}** for everyone.")
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            return await ctx.reply(embed = embed)
        if not userinput1.isnumeric():
            try:
                userinput1 = userinput1.replace("<",'') 
                userinput1 = userinput1.replace(">",'') 
                userinput1 = userinput1.replace("@",'') 
                userinput1 = userinput1.replace("!",'')
                userinput1 = userinput1.replace("&",'')
                userinput1 = userinput1.replace("#",'')
                userinput1 = int(userinput1)
            except:
                return await ctx.reply("I could not process your input! Please try again.")
        else:
            userinput1 = int(userinput1)
 
        guild = ctx.guild
        if guild.get_member(userinput1):
            userinputobj = guild.get_member(userinput1)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.name).child(prefix + "users").get()
            if not store:
                return await ctx.reply(f"This command does not even have any {enabledisable} users, what are you thinking?")
            else:
                if userinput1 in store:
                    store.remove(userinput1)
                    ref.child(str(ctx.guild.id)).child("rules").child(command.name).child(prefix + "users").set(store)
                else:
                    return await ctx.reply(f"That user is not in the {enabledisable} list for this command.")
        elif guild.get_role(userinput1):
            userinputobj = guild.get_role(userinput1)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.name).child(prefix + "roles").get()
            if not store:
                return await ctx.reply(f"This command does not even have any {enabledisable} roles, what are you thinking?")
            else:
                if userinput1 in store:
                    store.remove(userinput1)
                    ref.child(str(ctx.guild.id)).child("rules").child(command.name).child(prefix + "roles").set(store)
                else:
                    return await ctx.reply(f"That roles is not in the {enabledisable} list for this command.")
        elif guild.get_channel(userinput1):
            userinputobj = guild.get_channel(userinput1)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.name).child(prefix + "channels").get()
            if not store:
                return await ctx.reply(f"This command does not even have any {enabledisable} channels, what are you thinking?")
            else:
                if userinput1 in store:
                    store.remove(userinput1)
                    ref.child(str(ctx.guild.id)).child("rules").child(command.name).child(prefix + "channels").set(store)
                else:
                    return await ctx.reply(f"That channel is not in the {enabledisable} list for this command.")
        else:
            return await ctx.reply("I could not process your input! Please try again.")

        embed = discord.Embed(title = "Sucessfully Removed!",description = f"Removed the {enabledisable} rule for the command **{command}** for {userinputobj.mention}.")
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)

def setup(client):
    client.add_cog(Configure(client))
