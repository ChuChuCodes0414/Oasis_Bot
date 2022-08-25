from typing import runtime_checkable
import discord
from discord.ext import commands
import datetime
import firebase_admin
from firebase_admin import db
import random
import asyncio
import locale

class Lottery(commands.Cog):
    '''
        Lottery commands, for lotteries involving dank memer items. Will automatically track when an entry to sent to the host in a channel and add lottery entries.
        \n**Setup for this Category**
        Lottery Mod: `o!settings set lotterymod <role>` 
    '''
    def __init__(self,client):
        self.short = "🎫 | Dank Memer Lottery"
        self.client = client
        self.active_channels = []
        
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        for guild in ref.get().values():
            for channel in guild:
                try:
                    if guild[channel].get("active",None):
                        self.active_channels.append(int(channel))
                except:
                    pass
        locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

    def lottery_role_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            lottery = ref.child(str(ctx.message.guild.id)).child('lottery').get()
            role_ob = ctx.message.guild.get_role(lottery)
            if role_ob in ctx.message.author.roles:
                return True
            else:
                return False
        return commands.check(predicate)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Lottery Cog Loaded, and lotteries cached.')

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.id != 270904126974590976 or message.channel.id not in self.active_channels:
            return

        dictionary = message.embeds
        if dictionary:
            dictionary = dictionary[0].to_dict()
        else:
            return
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        guild = message.guild.id
        active = ref.child(str(guild)).child(str(message.channel.id)).child("active").get()
        if not active:
            return
        thelottery = ref.child(str(guild)).child(str(message.channel.id)).get()
        host = thelottery['host']
        hostob = message.guild.get_member(int(host))
        wayentered = None
        try:
            methods = dictionary["fields"][0]["name"] 
        except:
            return
        if methods == "Gifted":
            methods = "gift"
        elif methods == "Shared":
            methods = "coin"
        else:
            return
        if "Coins" in thelottery['entrymethods'] and methods == "coin" and hostob.name in dictionary["fields"][2]["name"]:
            priceamount = thelottery['entrymethods']['coins']['amount']
            entriesper = thelottery['entrymethods']['coins']['entries']
            sendamount = int(locale.atoi(dictionary['fields'][0]['value'].split()[1][:-1]))
            wayentered = "coins"
        elif methods == "gift" and hostob.name in dictionary["fields"][2]["name"]:
            for price,data in thelottery['entrymethods'].items():
                wayentered = price
                if price in dictionary["fields"][0]["value"]:
                    priceamount = data['amount']
                    entriesper = data['entries']
                    sendamount = int(locale.atoi(dictionary["fields"][0]["value"].split()[0][1:-2]))
                    break
        else:
            return
        userinput = message.reference.cached_message.author.id
        try:
            entrycount = sendamount//int(priceamount)
            entrycount *= entriesper
        except:
            return

        if entrycount <= 0:
            embed = discord.Embed(title = f"You did not include enough items for a full entry!",description = f"Each entry into the raffle requires **{priceamount}** `{wayentered}`"
            , color = discord.Color.random())

            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text = f'{message.guild.name} Lottery System',icon_url = message.channel.guild.icon)
            return await message.channel.send(embed = embed)

        currententries = thelottery.get("currententries",0)
        maxentries = thelottery.get('maxentries',None)

        if maxentries:
            if currententries + int(entrycount) > int(maxentries):
                embed = discord.Embed(title = f"Entry exceeds max entries!",description = f"Your entry of `{entrycount}` exceeds the max entries of `{maxentries}`. Contact the host for further details."
                , color = discord.Color.red())
                return await message.channel.send(embed = embed)

        entries = thelottery.get("entries",None)
        if entries:
            totalentries = entries.get(str(userinput),0)
        else:
            totalentries = 0

        ref.child(str(message.guild.id)).child(str(message.channel.id)).child("entries").child(str(userinput)).set(totalentries + entrycount)
        ref.child(str(message.guild.id)).child(str(message.channel.id)).child("currententries").set(currententries + entrycount)

        embed = discord.Embed(title = f"Entry Confirmed!",description = f"Thanks for entering the `{thelottery['prize']}` lottery <@{userinput}>!\nYou claimed `{entrycount}` entries, bringing your total entries to `{totalentries + entrycount}`"
        , color = discord.Color.random())

        embed.add_field(name = "Entry Details",value = f"Entry Method: `{wayentered}`\nAmount Sent: `{sendamount}`\nEntries Granted: `{entrycount}`")

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{message.guild.name} Lottery System',icon_url = message.channel.guild.icon)
        await message.channel.send(embed = embed)

    @commands.command(aliases = ["lstart"],help = "Start a lottery through an interactive embed.")
    @lottery_role_check()
    async def lotterystart(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        if ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).get():
            return await ctx.reply(embed = discord.Embed(description = "Wait, you have a lottery in this channel. Delete it first with `o!lotterycancel` if you want to start another one.",color = discord.Color.red()))
        embed = discord.Embed(title = f"{ctx.author}'s Lottery Setup",description = "Fields marked with a `*` are required, while the others are optional.",color = discord.Color.random())
        embed.set_footer(text = "Click a button to get started!")
        view = SetupLottery(ctx,self.client)
        message = await ctx.send(embed = embed,view = view)
        view.board = message
        await view.wait()
        data = view.value
        if data:
            host,channel,maxentries,prize = data['host'],data['channel'],data['maxentries'],data['prize']
            build = ""
            build += f"Host: {host.mention} (`{host.id}`)"
            build += f"\nChannel: {channel.mention}"
            build += f"\nMax Entries: `{maxentries}`"
            build += f"\nPrize: `{prize}`"

            embed = discord.Embed(title = f"{host} is hosting a lottery!",description = build,color = discord.Color.random())
            count = 1
            entrymethods = data['entrymethods']
            for type,details in entrymethods.items():
                embed.add_field(name = f"Entry Method {count}: {type}",value = f"**Amount Needed:** {details['amount']}\n**Entries Given:** {details['entries']}")
                count += 1
            embed.set_footer(text = "View the above entry methods to enter.")
            await ctx.send(f"Alright, lottery setup! Beginning now in {channel.mention}.")
            await channel.send(embed = embed)
            ref.child(str(ctx.guild.id)).child(str(channel.id)).set({"channel":channel.id,"active":True,"host":host.id,"entrymethods":entrymethods,"maxentries":maxentries,"prize":prize})
            self.active_channels.append(channel.id)

    @commands.command(help = "Manually give entries to a user.")
    @lottery_role_check()
    async def grantentries(self,ctx,entrycount:int,member:discord.Member):
        if entrycount < 1:
            return await ctx.reply(embed = discord.Embed(description = "Kind of need to grant at least one entry.",color = discord.Color.red()))
        ref = db.reference("/",app = firebase_admin._apps['lottery'])

        active = ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("active").get()
        if not active:
            return await ctx.reply(embed = discord.Embed(description = "Are you sure there's a lottery active in this channel? Doesn't seem like it",color = discord.Color.red()))

        lotteries = ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).get()
        entries = lotteries.get("entries",{})
        currententries = lotteries.get("currententries",0)
        maxentries = lotteries.get('maxentries',None)

        if maxentries:
            if currententries + int(entrycount) > int(maxentries):
                return await ctx.reply(embed = discord.Embed(description = f"Adding `{entrycount}` entries would go over the max entries set at `{maxentries}`.",color = discord.Color.red()))

        personentries = entries.get(str(member.id),0)

        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("entries").child(str(member.id)).set(personentries + entrycount)
        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("currententries").set(currententries + entrycount)

        embed = discord.Embed(title = f"Entries Added!",description = f"Added `{entrycount}` entries for {member}. They now have `{personentries + entrycount}` total entries in this lottery!", color = discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon)
        await ctx.send(embed = embed)

    @commands.command(help = "Manually remove entries from a user.")
    @lottery_role_check()
    async def removeentries(self,ctx,entrycount:int,member:discord.Member):
        if entrycount < 1:
            return await ctx.reply("Kind of need to remove at least one entry.")
        ref = db.reference("/",app = firebase_admin._apps['lottery'])

        active = ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("active").get()
        if not active:
            return await ctx.reply("Are you sure there's a lottery active in this channel? Doesn't seem like it")

        lotteries = ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).get()

        entries = lotteries.get("entries",{})
        maxentries = lotteries.get("maxentries")
        currententries = lotteries.get("currententries",0)

        personentries = entries.get(str(member.id),0)

        if personentries == 0:
            return await ctx.reply("Can't remove entries from someone with 0.")
        elif personentries - entrycount <= 0:
            return await ctx.reply("Uh, this person can't have negative entries.")

        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("entries").child(str(member.id)).set(personentries - entrycount)
        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("currententries").set(currententries - entrycount)

        embed = discord.Embed(title = f"Entries Removed!",description = f"Removed `{entrycount}` entries for {member}. They now have `{personentries - entrycount}` total entries in this lottery!", color = discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon)
        await ctx.send(embed = embed)

    @commands.command(help = "End the ongoing lottery in the channel, and give out the winner. Also can be used to reroll.")
    @lottery_role_check()
    async def lotteryend(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['lottery'])

        lotteries = ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).get()

        if not lotteries:
            return await ctx.reply("Are you sure there's a lottery in this channel? Doesn't seem like it")

        entries = lotteries.get("entries",{})

        if len(entries) == 0:
            return await ctx.send("This lottery has 0 entries...consider cancelling it instead.")

        embed = discord.Embed(title = f"🏆 The Lottery is now Over!",description = f"Tickets are being generated! Please standby.", color = discord.Color.green())
        message = await ctx.send(embed = embed)
        tickets = []
        async with ctx.typing():
            for person in entries:
                tickets.extend([person for i in range(int(entries[person]))])
        winner = random.randint(0,len(tickets)-1)
        embed = discord.Embed(title = f"🏆 The Lottery is now Over!",description = f"Tickets have been generated! With `{len(entries)}` unique entries and `{len(tickets)}` generated, the winner with ticket `{winner}` is...", color = discord.Color.random())
        await message.edit(embed = embed)
        await asyncio.sleep(5)
        prize = lotteries["prize"]
        host = lotteries["host"]
        embed = discord.Embed(title = f"🏆 The Lottery is now Over!",description = f"Tickets have been generated! With `{len(entries)}` unique entries and `{len(tickets)}` tickets generated, the winner with ticket `{winner}` is... <@{tickets[winner]}>\nThis lottery was hosted by <@{host}>", color = discord.Color.gold())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon)
        await message.edit(embed = embed)

        host = ctx.guild.get_member(int(host))
        embed = discord.Embed(title = f"🏆 Your Lottery is now Over!",description = f"Your lottery for `{prize}` is now over.\nWith `{len(tickets)}` total entries, the winner is <@{tickets[winner]}>!\n[Link to Ending Message]({message.jump_url})", color = discord.Color.gold())
        dm = host.dm_channel
        if dm == None:
            dm = await host.create_dm()
        await dm.send(embed = embed)

        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("active").set(False)
        #ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).delete()

    @commands.command(help = "Cancel the lottery, and do NOT give out a winner. All lottery data for the lottery will be deleted.")
    @lottery_role_check()
    async def lotterycancel(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['lottery'])

        lotteries = ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).get()

        if not lotteries:
            return await ctx.reply("Are you sure there's a lottery active in this channel? Doesn't seem like it")

        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).delete()
        await ctx.reply("Lottery data deleted and cancelled.")

    @commands.command(help = "View the info for the lottery in the specified or currenct channel.")
    async def lotteryinfo(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        lotteries = ref.child(str(ctx.guild.id)).child(str(channel.id)).get()

        if not lotteries:
            return await ctx.reply("Are you sure there's a lottery active in that channel? Doesn't seem like it")
        entrycount = len(lotteries.get("entries",[]))
        totalentries = lotteries.get("currententries",0)
        maxentries = lotteries.get("maxentries","None")
        embed = discord.Embed(title = f"Lottery for {lotteries['prize']}",description = f"**Lottery Channel:** {channel.mention}\n**Total People Entered:** `{entrycount}`\n**Total Entries:** `{totalentries}`" + 
            f"\n**Lottery Host:** <@{lotteries['host']}> (`{lotteries['host']}`)\n**Maximum Raffle Entries:** `{maxentries}`\n**Raffle Prize:** {lotteries['prize']}", color = discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        count = 1
        for type,details in lotteries.get("entrymethods",{}).items():
            embed.add_field(name = f"Entry Method {count}: {type}",value = f"**Amount Needed:** {details['amount']}\n**Entries Given:** {details['entries']}")
            count += 1
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon)
        message = await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.is_owner()
    async def cachelotteries(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        for guild in ref.get().values():
            for channel in guild:
                try:
                    self.active_channels.append(int(channel))
                except:
                    pass
        await ctx.send("cached")

    @commands.command(help = "View the info your own or another member lottery entries.")
    async def lotteryprofile(self,ctx,member:discord.Member=None):
        member = member or ctx.author

        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        lotteries = ref.child(str(ctx.guild.id)).get()

        if not lotteries:
            return await ctx.reply("Are you sure there's a lottery active in this server? Doesn't seem like it")

        lotteryinfo = ""

        for lottery in lotteries:
            if lottery == "dankhunt":
                continue
            thelottery = lotteries[lottery]
            entries = thelottery.get('entries',{}).get(str(member.id),0)
            lotteryinfo += f"**{thelottery['prize']} Lottery**\n`{entries}` entries\n\n"

        embed = discord.Embed(title = f"Lottery Profile for {member}",description = f"{lotteryinfo}", color = discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon)

        await ctx.send(embed = embed)

    @commands.command(help = "View all active lottery in the server.")
    async def lotteryserver(self,ctx,):
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        lotteries = ref.child(str(ctx.guild.id)).get()

        if not lotteries:
            return await ctx.reply("Are you sure there's a lottery active in this server? Doesn't seem like it")

        lotteryinfo = ""

        for lottery in lotteries:
            if lottery == "dankhunt":
                continue
            thelottery = lotteries[lottery]
            channel = thelottery.get("channel")
            lotteryinfo += f"**{thelottery['prize']} Lottery**\nLocation: <#{channel}>\n\n"

        embed = discord.Embed(title = f"Active Lottery for {ctx.guild}",description = f"{lotteryinfo}", color = discord.Color.random())
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon)

        await ctx.send(embed = embed)

    @commands.command(help = "Who has most entry in lottery? Who knows.")
    async def lotteryleaderboard(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        lottery = ref.child(str(ctx.guild.id)).child(str(channel.id)).child("entries").get()

        if not lottery:
            return await ctx.reply("Are you sure there's a lottery active in this server? Doesn't seem like it")

        sortedlottery = sorted(lottery , key=lottery.get, reverse=True)
        build = ""
        count = 1
        for person in sortedlottery[:10]:
            build += f'{count}. <@{person}>: `{lottery[person]}` entries\n'
            count += 1

        emb = discord.Embed(title=f"Lottery Leaderboard",description = build,color = discord.Color.random())
        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = emb)
    
class SetupEntryMethods(discord.ui.View):
    def __init__(self,ctx,client,entrymethods,board):
        super().__init__()
        self.ctx = ctx
        self.value = entrymethods
        self.client = client
        self.board = board
    
    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def formatentriesembed(self):
        count = 0
        embed = discord.Embed(title = f"Current Defined Entry Methods")
        if self.value:
            for method,data in self.value.items():
                embed.add_field(name = method,value = f"**Amount Needed:** {data['amount']}\n**Entries Given:** {data['entries']}")
                count += 1
        else:
            embed.description = "No current entry methods defined!"
        embed.set_footer(text = "Use the buttons below to continue.")
        return embed, count
    
    @discord.ui.button(label='Add Entry Method', style= discord.ButtonStyle.green)
    async def addmethod(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type in your entry method now! You can define one by using the syntax `item/amount/entries`. Your item must be formatted like the title of each item found with `pls shop <item>`, including spaces. If you want a coins entry method, use `coins` in place of the item name. You can have up to 5 entry methods.\n\nFor example, `Pepe Trophy/1/5` will give 5 entries for 1 Pepe Trophy. `Bank Note/10/1` will give 1 entry for 10 Bank Note.")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
        await interaction.response.edit_message(embed = embed,view = None)

        def check(message: discord.Message):
            return message.author.id == self.ctx.author.id and message.channel.id == self.ctx.channel.id
        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                self.value = False
                self.stop()
            if msg.content.lower() == "cancel":
                await msg.delete()
                embed = await self.formatentriesembed()
                await self.board.edit(embed = embed[0],view = self)
                return
            try:
                split = msg.content.split("/")
                entrytype,amount,entries = split[0].title(),int(split[1]),int(split[2])
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Type in your entry method now! You can define one by using the syntax `item/amount/entries`. Your item must be formatted like the title of each item found with `pls shop <item>`, including spaces. If you want a coins entry method, use `coins` in place of the item name. You can have up to 5 entry methods.\n\nFor example, `Pepe Trophy/1/5` will give 5 entries for 1 Pepe Trophy. `Bank Note/10/1` will give 1 entry for 10 Bank Note.\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel input.")
                await self.board.edit(embed = embed)
                await msg.delete()
                continue
        self.value[entrytype] = {"amount":amount,"entries":entries}
        embed,count = await self.formatentriesembed()
        if count >= 5:
            self.children[0].disabled = True
        await self.board.edit(embed = embed,view = self)
    
    @discord.ui.button(label='Remove Entry Method', style= discord.ButtonStyle.red)
    async def removemethod(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type in which entry method you want to remove now, using the entry method! For example, to remove `Pepe Trophy` from the entry methods, just type `Pepe Trophy`.")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
        await interaction.response.edit_message(embed = embed,view = None)

        def check(message: discord.Message):
            return message.author.id == self.ctx.author.id and message.channel.id == self.ctx.channel.id
        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                self.value = False
                self.stop()
            if msg.content.lower() == "cancel":
                await msg.delete()
                embed = await self.formatentriesembed()
                await self.board.edit(embed = embed[0],view = self)
                return
            try:
                self.value.pop(msg.content.title())
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Type in which entry method you want to remove now, using the entry method! For example, to remove `Pepe Trophy` from the entry methods, just type `Pepe Trophy`.\n\n⚠ I could not process your input! Are you sure that is a valid method?")
                embed.set_footer(text = "Type \"cancel\" to cancel input.")
                await self.board.edit(embed = embed)
                await msg.delete()
                continue
        embed,count = await self.formatentriesembed()
        if count >= 5:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False
        await self.board.edit(embed = embed,view = self)

    @discord.ui.button(label='Save', style= discord.ButtonStyle.green,row = 1)
    async def savemethods(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.stop()

class SetupLottery(discord.ui.View):
    def __init__(self,ctx,client):
        super().__init__(timeout=60)
        self.value = {"channel":None,"host":None,"entrymethods":{},"maxentries":None,"prize":None}
        self.ctx = ctx
        self.client = client
        self.board = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
    
    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def formatembed(self):
        embed = discord.Embed(title = f"{self.ctx.author}'s Lottery Setup",description = "Fields marked with a `*` are required, while the others are optional.",color = discord.Color.random())
        embed.set_footer(text = "Click a button to continue!")
        count = 0
        if self.value['host']:
            embed.add_field(name = "Host",value = f"{self.value['host'].mention}")
            count += 1
        else:
            embed.add_field(name = "Host",value = "None")
        if self.value['channel']:
            embed.add_field(name = "Channel",value = f"<#{self.value['channel'].mention}>")
            count += 1
        else:
            embed.add_field(name = "Channel",value = "None")
        if self.value['entrymethods']:
            embed.add_field(name = "Entry Methods",value = len(self.value['entrymethods']))
            count += 1
        else:
            embed.add_field(name = "Entry Methods",value = "None")
        if self.value['prize']:
            count += 1
        embed.add_field(name = "Prize",value = self.value['prize'])
        embed.add_field(name = "Max Entries",value = self.value['maxentries'])
        return embed, count == 4
    
    async def formatentriesembed(self):
        count = 0
        embed = discord.Embed(title = f"Current Defined Entry Methods")
        if self.value["entrymethods"]:
            for method,data in self.value["entrymethods"].items():
                embed.add_field(name = method,value = f"**Amount Needed:** {data['amount']}\n**Entries Given:** {data['entries']}")
                count += 1
        else:
            embed.description = "No current entry methods defined!"
        embed.set_footer(text = "Use the buttons below to continue.")
        return embed, count

    @discord.ui.button(label='Lottery Host*', style= discord.ButtonStyle.red)
    async def sethost(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type in who you want to receieve the items now!")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
        await interaction.response.edit_message(embed = embed,view = None)

        def check(message: discord.Message):
            return message.author.id == self.ctx.author.id and message.channel.id == self.ctx.channel.id
        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                self.value = False
                self.stop()
            if msg.content.lower() == "cancel":
                await msg.delete()
                embed = await self.formatembed()
                await self.board.edit(embed = embed[0],view = self)
                return
            try:
                member = await commands.converter.MemberConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Type in who you want to receieve the items now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel input.")
                await self.board.edit(embed = embed)
                await msg.delete()
                continue
        self.value['host'] = member
        self.children[0].style = discord.ButtonStyle.green
        embed,count = await self.formatembed()
        if count:
            self.children[5].disabled = False
        await self.board.edit(embed = embed,view = self)

    @discord.ui.button(label='Channel*', style=discord.ButtonStyle.red,row = 0)
    async def setchannel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type in the channel where items will be sent now!")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
        await interaction.response.edit_message(embed = embed,view = None)

        def check(message: discord.Message):
            return message.author.id == self.ctx.author.id and message.channel.id == self.ctx.channel.id
        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                self.value = False
                self.stop()
            if msg.content.lower() == "cancel":
                await msg.delete()
                embed = await self.formatembed()
                await self.board.edit(embed = embed[0],view = self)
                return
            try:
                channel = await commands.converter.TextChannelConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Type in the channel where items will be sent now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel input.")
                await self.board.edit(embed = embed)
                await msg.delete()
                continue
        self.value['channel'] = channel
        self.children[1].style = discord.ButtonStyle.green
        embed,count = await self.formatembed()
        if count:
            self.children[5].disabled = False
        await self.board.edit(embed = embed,view = self)
    
    @discord.ui.button(label='Entry Methods*', style=discord.ButtonStyle.red,row = 0)
    async def setentry(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed,count = await self.formatentriesembed()
        view = SetupEntryMethods(self.ctx,self.client,self.value['entrymethods'],self.board)
        if count >= 5:
            view.children[0].disabled = True
        await interaction.response.edit_message(embed = embed,view = view)
        await view.wait()
        if len(view.value) >= 1:
            self.value["entrymethods"] = view.value
            self.children[2].style = discord.ButtonStyle.green
        else:
            self.value["entrymethods"] = view.value
            self.children[2].style = discord.ButtonStyle.red
        embed,count = await self.formatembed()
        if count:
            self.children[5].disabled = False
        await self.board.edit(embed = embed,view = self)

    @discord.ui.button(label='Prize*', style=discord.ButtonStyle.red,row = 0)
    async def setprize(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type the prize for the lottery now!")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
        await interaction.response.edit_message(embed = embed,view = None)

        def check(message: discord.Message):
            return message.author.id == self.ctx.author.id and message.channel.id == self.ctx.channel.id
        
        try:
            msg = await self.client.wait_for("message",timeout = 60.0,check=check)
        except asyncio.TimeoutError:
            self.value = False
            self.stop()
        if msg.content.lower() == "cancel":
            await msg.delete()
            embed = await self.formatembed()
            await self.board.edit(embed = embed[0],view = self)
            return

        prize = msg.content
        await msg.delete()
        self.value['prize'] = prize
        self.children[3].style = discord.ButtonStyle.green
        embed,count = await self.formatembed()
        if count:
            self.children[5].disabled = False
        await self.board.edit(embed = embed,view = self)
    
    @discord.ui.button(label='Max Entries', style=discord.ButtonStyle.grey,row = 0)
    async def setmax(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type in the max entry count now!\nTo remove the max entry setting, type \"remove\".")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
        await interaction.response.edit_message(embed = embed,view = None)

        def check(message: discord.Message):
            return message.author.id == self.ctx.author.id and message.channel.id == self.ctx.channel.id

        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                self.value = False
                self.stop()
            if msg.content.lower() == "cancel":
                await msg.delete()
                embed = await self.formatembed()
                await self.board.edit(embed = embed[0],view = self)
                return
            elif msg.content.lower() == "remove":
                await msg.delete()
                self.value['maxentries'] = None
                self.children[4].style = discord.ButtonStyle.gray
                embed = await self.formatembed()
                await self.board.edit(embed = embed[0],view = self)
                return
            try:
                maxentry = int(msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Type in the max entry count now!\nTo remove the max entry setting, type \"remove\".\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel input.")
                await self.board.edit(embed = embed)
                await msg.delete()
                continue
        self.value['maxentries'] = maxentry
        self.children[4].style = discord.ButtonStyle.green
        embed,count = await self.formatembed()
        if count:
            self.children[5].disabled = False
        await self.board.edit(embed = embed,view = self)
    
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green,disabled = True,row = 1)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red,row = 1)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        self.value = False
        self.stop()

async def setup(client):
    await client.add_cog(Lottery(client))