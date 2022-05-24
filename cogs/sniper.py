import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import db
from datetime import datetime
import asyncio
import os

class Sniper(commands.Cog):
    '''
        Powerful snipe commands, can make for some fun! You must setup a sniper role for these commands to work.
        \n**Setup for this Category**
        Sniper Role: `o!settings add sniper <role>` 
    '''
    def __init__(self, client):
        self.short = "<:sniper:950162525083815937> | Message Sniper"
        self.client = client
        self.sniped_messages = {}
        self.edited_messages = {}
        self.removed_reactions = {}
        self.purged_messages = {}
        self.image_snipes = {}
        self.settings = {}
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        all = ref.get()
        for guild,data in all.items():
            self.settings[int(guild)] = [data.get("snipelb",None),data.get("snipecd",None)]

    @commands.Cog.listener()
    async def on_ready(self):
        print('Snipe Cog Loaded.')
    
    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        data = ref.child(str(guild.id)).get() or None
        self.settings[int(guild.id)] = [data.get("snipelb",None),data.get("snipecd",None)]
    
    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        try:
            self.settings.pop(int(guild.id))
        except:
            pass

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        now = datetime.now()
        if message.channel.id in self.sniped_messages:
            self.sniped_messages[message.channel.id].insert(0,[message,now])
        else:
            self.sniped_messages[message.channel.id] = [[message,now]]
        max = self.settings[message.guild.id][0] or 50
        if max > 50:
            max = 50
        if len(self.sniped_messages[message.channel.id]) > max:
            self.sniped_messages[message.channel.id].pop(-1)
        time = self.settings[message.guild.id][1] or 30
        await asyncio.sleep(time)
        try:
            self.sniped_messages[message.channel.id].remove([message,now])
        except:
            pass
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self,messages):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        now = datetime.now()
        if messages[0].channel.id in self.purged_messages:
            self.purged_messages[messages[0].channel.id].insert(0,[messages,now])
        else:
            self.purged_messages[messages[0].channel.id] = [[messages,now]]
        max = self.settings[messages[0].guild.id][0] or 50
        if max > 50:
            max = 50
        if len(self.purged_messages[messages[0].channel.id]) > max:
            self.purged_messages[messages[0]].channel.id.pop(-1)
        time = self.settings[messages[0].guild.id][1] or 30
        await asyncio.sleep(time)
        try:
            self.purged_messages[messages[0].channel.id].remove([messages,now])
        except:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self,message_before,message_after):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        if message_before.content and message_after.content:
            now = datetime.now()
            if message_before.channel.id in self.edited_messages:
                self.edited_messages[message_before.channel.id].insert(0,[message_before,message_after,now])
            else:
                self.edited_messages[message_before.channel.id] = [[message_before,message_after,now]]
            max = self.settings[message_before.guild.id][0] or 50
            if max > 50:
                max = 50
            if len(self.edited_messages[message_before.channel.id]) > max:
                self.edited_messages[message_before.channel.id].pop(-1)
            time = self.settings[message_before.guild.id][1] or 30
            await asyncio.sleep(time)
            try:
                self.edited_messages[message_before.channel.id].remove([message_before,message_after,now])
            except:
                pass

    @commands.Cog.listener()
    async def on_reaction_remove(self,reaction, user):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        message = reaction.message
        now = datetime.now()
        if message.channel.id in self.removed_reactions:
            self.removed_reactions[message.channel.id].insert(0,[message,user,reaction,now])
        else:
            self.removed_reactions[message.channel.id] = [[message,user,reaction,now]]
        max = self.settings[message.guild.id][0] or 50
        if max > 50:
            max = 50
        if len(self.removed_reactions[message.channel.id]) > max:
            self.removed_reactions[message.channel.id].pop(-1)
        time = self.settings[message.guild.id][1] or 30
        await asyncio.sleep(time)
        try:
            self.removed_reactions[message.channel.id].remove([message,user,reaction,now])
        except:
            pass

    def snipe_role_check():
        async def predicate2(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            sniperoles = ref.child(str(ctx.message.guild.id)).child('sniper').get()

            if sniperoles == None:
                return False
            for role in sniperoles:
                role_ob = ctx.message.guild.get_role(role)
                if role_ob in ctx.message.author.roles:
                    return True
            else:
                return False
        return commands.check(predicate2)

    @commands.command(name = 'snipe',aliases = ['sn'],help = "Snipe a recently deleted message!")
    @snipe_role_check()
    async def snipe(self,ctx,index = 1,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        index -= 1

        if not channel.id in self.sniped_messages:
            return await ctx.reply(embed = discord.Embed(description = f"There are no deleted messages in {channel.mention}",color = discord.Color.red()))
        if not index < len(self.sniped_messages[channel.id]) or index < 0:
            return await ctx.reply(embed = discord.Embed(description = f"Your snipe request is not valid!\nThere are only `{len(self.sniped_messages[channel.id])}` deleted messages in {channel.mention}.",color = discord.Color.red()))
        
        message = self.sniped_messages[channel.id][index][0]
        time = self.sniped_messages[channel.id][index][1]

        if message.embeds:
            sniped_embed = message.embeds[0]
            await ctx.reply(embed = sniped_embed)
            emb = discord.Embed(title = f"Deleted message {index+1} in #{channel.name}", description = "Embed sniped, shown above.",color = discord.Color.random())
            emb.set_author(name=f"Sent by {message.author}",icon_url=message.author.avatar)
            emb.set_footer(text = f"Sniped by {ctx.message.author}")
            emb.timestamp = time
            return await ctx.send(embed = emb)
        else:
            description = message.content

        emb = discord.Embed(title = f"Deleted message {index+1} in #{channel.name}", description = description,color = discord.Color.random())
        emb.set_author(name=f"Sent by {message.author}",icon_url=message.author.avatar)
        emb.set_footer(text = f"Sniped by {ctx.message.author}")
        emb.timestamp = time

        try:
            emb.set_image(url = message.attachments[0])
        except:
            pass

        await ctx.reply(embed = emb)

    @commands.command(aliases = ['ms'],help = "Just how many messages that were deleted are hiding in this channel? Find out with this command.")
    @snipe_role_check()
    async def maxsnipe(self,ctx):
        try:
            messages = len(self.sniped_messages[ctx.channel.id])
        except:
            messages = 0
        await ctx.reply(embed = discord.Embed(description = f"There are a total of `{messages}` messages hiding in this channel!",color = discord.Color.random()))

    @commands.command(name = 'esnipe',aliases = ['esn'],help = "Snipe a recently edited message!")
    @snipe_role_check()
    async def esnipe(self,ctx,index = 1,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        index -= 1

        if not channel.id in self.edited_messages:
            return await ctx.reply(embed = discord.Embed(description = f"There are no edited messages in {channel.mention}",color = discord.Color.red()))
        if not index < len(self.edited_messages[channel.id]) or index < 0:
            return await ctx.reply(embed = discord.Embed(description = f"Your snipe request is not valid!\nThere are only `{len(self.sniped_messages[channel.id])}` edited messages in {channel.mention}.",color = discord.Color.red()))

        message = self.edited_messages[channel.id][index]

        emb = discord.Embed(title = f"Edited message {index + 1} in #{channel.name}", description = f'**Before:** {message[0].content}\n**After:** {message[1].content}',color = discord.Color.random())
        emb.set_author(name= f"Edited by {message[0].author}" ,icon_url=message[0].author.avatar)
        emb.set_footer(text = f"Sniped by {ctx.message.author}")
        emb.timestamp = message[2]

        await ctx.reply(embed = emb)

    @commands.command(aliases = ['mes'],help = "Just how many messages that were edited are hiding in this channel? Find out with this command.")
    @snipe_role_check()
    async def maxesnipe(self,ctx):
        try:
            messages = len(self.edited_messages[ctx.channel.id])
        except:
            messages = 0
        await ctx.reply(embed = discord.Embed(description = f"There are a total of `{messages}` edited messages hiding in this channel!",color = discord.Color.random()))

    @commands.command(name = 'rsnipe',aliases = ['rsn'],help = "Snipe a recently removed reaction!")
    @snipe_role_check()
    async def rsnipe(self,ctx,index = 1,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        index -= 1

        if not channel.id in self.removed_reactions:
            return await ctx.reply(embed = discord.Embed(description = f"There are no removed reactions in {channel.mention}",color = discord.Color.red()))
        if not index < len(self.removed_reactions[channel.id]) or index < 0:
            return await ctx.reply(embed = discord.Embed(description = f"Your snipe request is not valid!\nThere are only `{len(self.sniped_messages[channel.id])}` removed reactions in {channel.mention}.",color = discord.Color.red()))

        data = self.removed_reactions[channel.id][index]

        emb = discord.Embed(title = f"Removed reaction {index+1} in #{channel.name}", description = f'**Message:** [Link to Message]({data[0].jump_url})\n**Reaction Removed:** {data[2].emoji}',color = discord.Color.random())
        emb.set_author(name=f"Reationed removed by {data[1]}",icon_url=data[1].avatar)
        emb.set_footer(text = f"Sniped by {ctx.message.author}")
        emb.timestamp = data[3]
        await ctx.reply(embed = emb)

    @commands.command(aliases = ['mrs'],help = "Just how many messages that were edited are hiding in this channel? Find out with this command.")
    @snipe_role_check()
    async def maxrsnipe(self,ctx):
        try:
            reactions = len(self.removed_reactions[ctx.channel.id])
        except:
            reactions = 0
        await ctx.reply(embed = discord.Embed(description = f"There are a total of `{reactions}` removed reactions hiding in this channel!",color = discord.Color.random()))

    @commands.command(aliases = ['psn'],help = "Snipe the list of recently purged messages!")
    @snipe_role_check()
    async def psnipe(self,ctx,index = 1,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        index -= 1

        if not channel.id in self.purged_messages:
            return await ctx.reply(embed = discord.Embed(description = f"There are no purged messages in {channel.mention}",color = discord.Color.red()))
        if not index < len(self.purged_messages[channel.id]) or index < 0:
            return await ctx.reply(embed = discord.Embed(description = f"Your snipe request is not valid!\nThere are only `{len(self.sniped_messages[channel.id])}` purged messages in {channel.mention}.",color = discord.Color.red()))
       
        data = self.purged_messages[channel.id][index]

        if len(data[0]) >= 16:
            emb = discord.Embed(title = f"Purged messages in #{channel.name}", description = f'There were 16+ purged messages here. What are they? I don\'t know I didn\'t store them lol.',color = discord.Color.random())
            emb.set_footer(text = f"Sniped by {ctx.message.author}")
            emb.timestamp = data[1]
            return await ctx.reply(embed = emb)

        build = ""

        for message in data[0]:
            if message.content:
                build += f"[{message.author}]: {message.content}\n"
            else:
                build += f"[{message.author}]: *No Message Content to Display*\n"
            
        emb = discord.Embed(title = f"Purged messages in #{channel.name}", description = f'{build}',color = discord.Color.random())
        emb.set_footer(text = f"Sniped by {ctx.message.author}")
        emb.timestamp = data[1]
        return await ctx.reply(embed = emb)

    @commands.command(aliases = ['mps'],help = "Just how many messages that were purged are hiding in this channel? Find out with this command. You can use `o!psnipe [index]` to reveal them.")
    @snipe_role_check()
    async def maxpsnipe(self,ctx):
        try:
            messages = len(self.purged_messages[ctx.channel.id])
        except:
            messages = 0
        await ctx.reply(embed = discord.Embed(description = f"There are a total of `{messages}` purgess hiding in this channel!",color = discord.Color.random()))
    
    @commands.command(aliases = ['csn'],help = "Clears all sniped messages from the bot cache for the specified or current channel.")
    @commands.has_permissions(administrator = True)
    async def clearsnipes(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        try:
            self.sniped_messages.pop(channel.id)
        except:
            pass
        try:
            self.edited_messages.pop(channel.id)
        except:
            pass
        try:
            self.removed_reactions.pop(channel.id)
        except:
            pass
        await ctx.send(embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Removed sniped cache for {channel.mention}",color = discord.Color.green()))

async def setup(client):
    await client.add_cog(Sniper(client))
    