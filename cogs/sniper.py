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
        self.client = client
        self.sniped_messages = {}
        self.edited_messages = {}
        self.removed_reactions = {}
        self.purged_messages = {}
        self.image_snipes = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print('Snipe Cog Loaded.')

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        now = datetime.now()
        if message.channel.id in self.sniped_messages:
            self.sniped_messages[message.channel.id].insert(0,[message,now])
        else:
            self.sniped_messages[message.channel.id] = [[message,now]]
        max = ref.child(str(message.guild.id)).child("snipelb").get() or 50
        if max > 50:
            max = 50
        if len(self.sniped_messages[message.channel.id]) > max:
            self.sniped_messages[message.channel.id].pop(-1)
        '''
        if message.attachments:
            path = f"imagesnipes\\{message.channel.id}"
            if not os.path.isdir(path):
                os.mkdir(f"imagesnipes\\{message.channel.id}")
            files = len(os.listdir(path))
            attachments = message.attachments[0]
            await attachments.save(f"imagesnipes\\{message.channel.id}\\{files+1}_{attachments.filename}")
            self.image_snipes[f"{files+1}_{attachments.filename}"] = [message.author,now]
            attachment = True
        if attachment:
            os.remove(f"imagesnipes\\{message.channel.id}\\{files+1}_{attachments.filename}")
            if len(os.listdir(path)) == 0:
                os.rmdir(path)
        attachment = False
        '''
        time = ref.child(str(message.guild.id)).child("snipecd").get() or 30
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
        max = ref.child(str(messages[0].guild.id)).child("snipelb").get() or 50
        if max > 50:
            max = 50
        if len(self.purged_messages[messages[0].channel.id]) > max:
            self.purged_messages[messages[0]].channel.id.pop(-1)
        time = ref.child(str(messages[0].guild.id)).child("snipecd").get() or 30
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
            max = ref.child(str(message_before.guild.id)).child("snipelb").get() or 50
            if max > 50:
                max = 50
            if len(self.edited_messages[message_before.channel.id]) > max:
                self.edited_messages[message_before.channel.id].pop(-1)
            time = ref.child(str(message_before.guild.id)).child("snipecd").get() or 30
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

        max = ref.child(str(message.guild.id)).child("snipelb").get() or 50

        if max > 50:
            max = 50
        if len(self.removed_reactions[message.channel.id]) > max:
            self.removed_reactions[message.channel.id].pop(-1)
        time = ref.child(str(message.guild.id)).child("snipecd").get() or 30
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

    @commands.command(name = 'snipe',aliases = ['sn'],description = "Snipe a recently deleted message!",help = "snipe [index] [channel]")
    @snipe_role_check()
    async def snipe(self,ctx,index = 1,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        index -= 1

        try: #This piece of code is run if the bot finds anything in the dictionary
            message = self.sniped_messages[channel.id][index][0]
            time = self.sniped_messages[channel.id][index][1]
        except: #This piece of code is run if the bot doesn't find anything in the dictionary
            return await ctx.reply(f"There are no recently deleted messages in {channel.mention}, or there are not that many recently deleted messages here.")

        if message.embeds:
            sniped_embed = message.embeds[0]
            await ctx.reply(embed = sniped_embed)
            emb = discord.Embed(name = f"Last deleted message in #{channel.name}", description = "Embed sniped, shown above.")
            emb.set_author(name="Sent by " + message.author.name + "#" + message.author.discriminator,icon_url=message.author.avatar_url)
            emb.set_footer(text = f"Sniped by {ctx.message.author}")
            return await ctx.send(embed = emb)
        else:
            description = message.content

        emb = discord.Embed(name = f"Last deleted message in #{channel.name}", description = description)
        emb.set_author(name="Sent by " + message.author.name + "#" + message.author.discriminator,icon_url=message.author.avatar_url)
        emb.set_footer(text = f"Sniped by {ctx.message.author}")
        emb.timestamp = time

        try:
            emb.set_image(url = message.attachments[0])
        except:
            pass

        await ctx.reply(embed = emb)

    @commands.command(aliases = ['ms'],description = "Just how many messages that were deleted are hiding in this channel? Find out with this command. You can use `o!snipe [index]` to reveal them.")
    @snipe_role_check()
    async def maxsnipe(self,ctx):
        try:
            messages = len(self.sniped_messages[ctx.channel.id])
        except:
            messages = 0
        await ctx.reply(f"There are a total of `{messages}` messages hiding in this channel!")


    @commands.command(name = 'esnipe',aliases = ['esn'],description = "Snipe a recently edited message!",help = "esnipe [index] [channel]")
    @snipe_role_check()
    async def esnipe(self,ctx,index = 1,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        index -= 1

        try: #This piece of code is run if the bot finds anything in the dictionary
            message = self.edited_messages[channel.id][index]
        except: #This piece of code is run if the bot doesn't find anything in the dictionary
            return await ctx.reply(f"There are no recently edited messages in {channel.mention}, or there are not that many recently edited messages here.")

        emb = discord.Embed(name = f"Last edited message in #{channel.name}", description = f'**Before:** {message[0].content}\n**After:** {message[1].content}')
        emb.set_author(name="Edited by " + message[0].author.name + "#" + message[0].author.discriminator,icon_url=message[0].author.avatar_url)
        emb.set_footer(text = f"Sniped by {ctx.message.author}")
        emb.timestamp = message[2]

        await ctx.reply(embed = emb)

    @commands.command(aliases = ['mes'],description = "Just how many messages that were edited are hiding in this channel? Find out with this command. You can use `o!esnipe [index]` to reveal them.")
    @snipe_role_check()
    async def maxesnipe(self,ctx):
        try:
            messages = len(self.edited_messages[ctx.channel.id])
        except:
            messages = 0
        await ctx.reply(f"There are a total of `{messages}` edited messages hiding in this channel!")

    @commands.command(name = 'rsnipe',aliases = ['rsn'],description = "Snipe a recently removed reaction!",help = "rsnipe [index] [channel]")
    @snipe_role_check()
    async def rsnipe(self,ctx,index = 1,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        index -= 1

        try: #This piece of code is run if the bot finds anything in the dictionary
            data = self.removed_reactions[channel.id][index]
        except: #This piece of code is run if the bot doesn't find anything in the dictionary
            return await ctx.reply(f"There are no recently removed reactions in {channel.mention}, or there are not that many recently removed reactions here.")

        emb = discord.Embed(name = f"Removed reaction in #{channel.name}", description = f'**Message:** [Link to Message]({data[0].jump_url})\n**Reaction Removed:** {data[2].emoji}')
        emb.set_author(name="Reationed removed by " + data[1].name + "#" + data[1].discriminator,icon_url=data[1].avatar_url)
        emb.set_footer(text = f"Sniped by {ctx.message.author}")
        emb.timestamp = data[3]

        await ctx.reply(embed = emb)

    @commands.command(aliases = ['mrs'],description = "Just how many messages that were edited are hiding in this channel? Find out with this command. You can use `p!esnipe [index]` to reveal them.")
    @snipe_role_check()
    async def maxrsnipe(self,ctx):
        try:
            messages = len(self.removed_reactions[ctx.channel.id])
        except:
            messages = 0
        await ctx.reply(f"There are a total of `{messages}` removed reactions in this channel!")

    @commands.command(aliases = ['psn'],description = "Snipe the list of recently purged messages!",help = "psnipe [index] [channel]",brief = "Someone purging their messages to hide their dumb messages? Well now you can snipe it.")
    @snipe_role_check()
    async def psnipe(self,ctx,index = 1,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        index -= 1

        try: #This piece of code is run if the bot finds anything in the dictionary
            data = self.purged_messages[channel.id][index]
        except: #This piece of code is run if the bot doesn't find anything in the dictionary
            return await ctx.reply(f"There are no recently purged messages in {channel.mention}, or there are not that many recently purged messages here.")

        if len(data[0]) >= 16:
            emb = discord.Embed(title = f"Purged messages in #{channel.name}", description = f'There were 16+ purged messages here. What are they? I don\'t know I didn\'t store them lol.')
            emb.set_footer(text = f"Sniped by {ctx.message.author}")
            emb.timestamp = data[1]
            return await ctx.reply(embed = emb)

        build = ""

        for message in data[0]:
            if message.content:
                build += f"[{message.author}]: {message.content}\n"
            else:
                build += f"[{message.author}]: *No Message Content to Display*\n"
            
        emb = discord.Embed(title = f"Purged messages in #{channel.name}", description = f'{build}')
        emb.set_footer(text = f"Sniped by {ctx.message.author}")
        emb.timestamp = data[1]
        return await ctx.reply(embed = emb)

    @commands.command(aliases = ['mps'],description = "Just how many messages that were purged are hiding in this channel? Find out with this command. You can use `o!psnipe [index]` to reveal them.")
    @snipe_role_check()
    async def maxpsnipe(self,ctx):
        try:
            messages = len(self.purged_messages[ctx.channel.id])
        except:
            messages = 0
        await ctx.reply(f"There are a total of `{messages}` purges in this channel!")
    
    @commands.command(disabled = True,aliases = ['isn'],description = "Snipe images that were deleted.",help = "isnipe [index] [channel]")
    @snipe_role_check()
    async def isnipe(self,ctx,index:int = 1, channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        index -= 1

        path = f"imagesnipes\\{channel.id}"

        if not os.path.isdir(path):
            return await ctx.reply(f"I did not find any deleted images here in {channel.mention}")
        else:
            files = os.listdir(path)
            files.reverse()
            if len(files) <= index:
                return await ctx.reply(f"There are not that many deleted files here!")
            file = files[index]
            info = self.image_snipes[file] 
            file = discord.File(path + "\\" + file)
            embed = discord.Embed(title = "Image Sniped Above",description = f"Sent by: {info[0]}")
            embed.set_footer(text = f"Sniped by {ctx.message.author}")
            embed.timestamp = info[1]
            await ctx.send(embed = embed,file = file)

    @commands.command(disabled = True,aliases = ['mis'],description = "How many hiding images are in this channel? Find out.",help = "maxisnipe")
    @snipe_role_check()
    async def maxisnipe(self,ctx):
        path = f"imagesnipes\\{ctx.channel.id}"

        if not os.path.isdir(path):
            return await ctx.reply(f"I did not find any deleted images here in {ctx.channel.mention}")
        else:
            return await ctx.reply(f"There are `{len(os.listdir(path))}` hiding images in {ctx.channel.mention}!")


    @commands.command(aliases = ['csn'],description = "Clears all sniped messages from the bot cache for the specified or current channel.",help = "clearsnipes [channel]")
    @commands.has_permissions(administrator = True)
    async def clearsnipes(self,ctx,channel:discord.Member = None):
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
        await ctx.send(f"<a:PB_greentick:865758752379240448> Removed sniped cache for {channel.mention}")



def setup(client):
    client.add_cog(Sniper(client))
    