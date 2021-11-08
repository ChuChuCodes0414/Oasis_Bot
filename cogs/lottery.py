from typing import runtime_checkable
import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button
import datetime
import math
import firebase_admin
from firebase_admin import db
import random
import asyncio

class Lottery(commands.Cog):
    '''
        Lottery commands, for lotteries involving dank memer items. Will automatically track when an entry to sent to the host in a channel and add lottery entries.
        \n**Setup for this Category**
        Lottery Mod: `o!settings set lotterymod <role>` 
    '''
    def __init__(self,client):
        self.client = client
        self.active_channels = []

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
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        for guild in ref.get().values():
            for channel in guild:
                try:
                    if guild[channel].get("active",None):
                        self.active_channels.append(int(channel))
                except:
                    pass
        print('Lottery Cog Loaded, and lotteries cached.')

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.id != 270904126974590976 or message.channel.id not in self.active_channels:
            return

        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        guild = message.guild.id

        active = ref.child(str(guild)).child(str(message.channel.id)).child("active").get()

        if not active:
            return
        found = False
        thelottery = ref.child(str(guild)).child(str(message.channel.id)).get()
        host = thelottery['host']
        hostob = message.guild.get_member(int(host))
        splitmessage = message.content.split()
        wayentered = None
        if "coins" in thelottery['entrymethods']:
            priceamount = thelottery['entrymethods']['coins']['amount']
            entriesper = thelottery['entrymethods']['coins']['entries']
            if len(splitmessage) >= 3:
                if splitmessage[1] == "You" and splitmessage[2] == "gave" and splitmessage[3] == hostob.name and splitmessage[4] == "**⏣":
                    amount = splitmessage[5]
                    sendamount = (amount.strip("*,"))
                    sendamount = sendamount.replace(',','')
                    sendamount = int(sendamount)
                    userinput = splitmessage[0]
                    userinput = userinput.replace("<",'') 
                    userinput = userinput.replace(">",'') 
                    userinput = userinput.replace("@",'') 
                    userinput = userinput.replace("!",'')
                    userinput = userinput.replace("&",'')
                    userinput = userinput.replace("#",'')
                    userinput = int(userinput)
                    wayentered = "Coins"
                    found = True
        
        if not found:
            for price,data in thelottery['entrymethods'].items():
                wayentered = price
                price = "**"+price+ "**,"
                if price in message.content and hostob.name in splitmessage:
                    priceamount = data['amount']
                    entriesper = data['entries']
                    found = True
                    break
            if found and splitmessage[1] == "You" and splitmessage[2] == "gave" and splitmessage[3] == hostob.name and splitmessage[0].startswith("<@") and splitmessage[0].endswith(">"):
                sendamount = splitmessage[4].replace(',','')
                sendamount = int(sendamount)
                userinput = splitmessage[0]
                userinput = userinput.replace("<",'') 
                userinput = userinput.replace(">",'') 
                userinput = userinput.replace("@",'') 
                userinput = userinput.replace("!",'')
                userinput = userinput.replace("&",'')
                userinput = userinput.replace("#",'')
                userinput = int(userinput)

        if not found:
            return
        try:
            entrycount = sendamount//int(priceamount)
            entrycount *= entriesper
        except:
            return

        if entrycount <= 0:
            embed = discord.Embed(title = f"You did not include enough items for a full entry!",description = f"Each entry into the raffle requires **{priceamount}** `{wayentered}`"
            , color = discord.Color.random())

            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text = f'{message.guild.name} Lottery System',icon_url = message.channel.guild.icon_url)
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

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{message.guild.name} Lottery System',icon_url = message.channel.guild.icon_url)
        await message.channel.send(embed = embed)

    @commands.command(description = "Start a lottery with dank memer being the entry currency. See documentation for info.",help = "lotterystart"
        ,brief = "This command is now interactive, just the run the command to get started.")
    @lottery_role_check()
    async def lotterystart(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['lottery'])
        if ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).get():
            return await ctx.reply("Wait, you have a lottery in this channel. Delete it first with `o!lotterycancel` if you want to start another one.")
        def check(message: discord.Message):
            return message.author.id == ctx.author.id and message.channel.id == ctx.channel.id
        await ctx.reply("Seems like you want to start a lottery. Lets get started! To cancel at any time, type `cancel`.\nFirst, enter who will be the host of the lottery. This user will receieve the items.")
        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                return await ctx.send("Well guess we aren't starting a lottery today.")
                
            userinput = msg.content
            if userinput.lower() == "cancel":
                return await ctx.send("Alright, setup cancelled.")
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
                    await ctx.send("That does not look like a valid user to me.")
                    continue
            else:
                userinput = int(userinput)
            if not ctx.guild.get_member(userinput):
                await ctx.send("That does not look like a valid user to me.")
                continue
            if ctx.guild.get_member(userinput).bot:
                await ctx.send("You cant have a bot accept entries.")
                continue
            
            host = ctx.guild.get_member(userinput)
            break
        await ctx.send(f"Alright, looks like {host.mention} will receieve the items.\nNext, which channel will entries be sent in? This is where I will be looking for messages from Dank Memer to register entries.")
        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                return await ctx.send("Well guess we aren't starting a lottery today.")
                
            userinput = msg.content
            if userinput.lower() == "cancel":
                return await ctx.send("Alright, setup cancelled.")
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
                    await ctx.send("That does not look like a valid channel to me.")
                    continue
            else:
                userinput = int(userinput)
            if not ctx.guild.get_channel(userinput):
                await ctx.send("That does not look like a valid channel to me.")
                continue
            if userinput in self.active_channels:
                await ctx.send("There is already a lottery happening in that channel.")
                continue
            channel = ctx.guild.get_channel(userinput)
            break
        await ctx.send(f"Ok, I will be looking for messages in {channel.mention}.\nNext, we need to define some entry methods. You can define one by using the syntax `item/amount/entries`. Your item must be formatted like the title of each item found with `pls shop <item>`, including spaces."+ 
            "If you want a coins entry method, use `coins` in place of the item name. You can have up to 5 entry methods." +
            "\nFor example, `Pepe Trophy/1/5` will give 5 entries for 1 Pepe Trophy. `Bank Note/10/1` will give 1 entry for 10 Bank Note.\nWhen you are done adding entry methods, enter `done`.")
        entrymethods = {}
        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                return await ctx.send("Well guess we aren't starting a lottery today.")
            
            if msg.content.lower() == "done":
                break
            if msg.content.lower() == "cancel":
                return await ctx.send("Alright, setup cancelled.")
            split = msg.content.split("/")

            if len(split) != 3:
                await ctx.send("That does not look like a valid entry method to me.")
                continue
            
            try:
                type = split[0]
                amount = int(split[1])
                entries = int(split[2])
            except:
                await ctx.send("Your amount and entries need to be integers.")
                continue
        
            entrymethods[type] = {"amount":amount,"entries":entries}
            
            await ctx.send(f"**Entry Method:**\nType: {type}\nAmount: {amount}\nEntries: {entries}\nAdd another entry method using the same format. If this is your last entry method, type `done`.")
        await ctx.send(f"Alright, I have registered a total of `{len(entrymethods)}` methods to enter.\nNext, specify the maximum amount of entries you will allow. If you do not want a maximum, type `none`.")
        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                return await ctx.send("Well guess we aren't starting a lottery today.")
                
            userinput = msg.content
            if userinput.lower() == "cancel":
                return await ctx.send("Alright, setup cancelled.")
            if userinput.lower() == "none":
                maxentries = None
                break
            if not userinput.isnumeric():
                await ctx.send("Well you have to specify a number or `none`. Enter a valid number this time.")
                continue
            else:
                userinput = int(userinput)

            if userinput <= 1:
                await ctx.send("Well you need more than one entry to hold a lottery. Enter a valid number this time.")
                continue
            
            maxentries = userinput
            break
        await ctx.send(f"Alright, I have registered the max entries as `{maxentries}`\nWhat will be the prize for the lottery?")
        while True:
            try:
                msg = await self.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                return await ctx.send("Well guess we aren't starting a lottery today.")
                
            userinput = msg.content
            if userinput.lower() == "cancel":
                return await ctx.send("Alright, setup cancelled.")
            if not userinput:
                await ctx.send("Well it needs to be a string, not some other input. Try again.")
                continue

            prize = userinput
            break

        build = ""
        build += f"Host: {host.mention} (`{host.id}`)"
        build += f"\nChannel: {channel.mention}"
        build += f"\nMax Entries: `{maxentries}`"
        build += f"\nPrize: `{prize}`"

        embed = discord.Embed(title = f"{host} is hosting a lottery!",description = build,color = discord.Color.random())
        count = 1
        for type,details in entrymethods.items():
            embed.add_field(name = f"Entry Method {count}: {type}",value = f"**Amount Needed:** {details['amount']}\n**Entries Given:** {details['entries']}")
            count += 1
        embed.set_footer(text = "View the above entry methods to enter.")
        await ctx.send(f"Alright, lottery setup! Beginning now in {channel.mention}.")
        await channel.send(embed = embed)
        ref.child(str(ctx.guild.id)).child(str(channel.id)).set({"channel":ctx.channel.id,"active":True,"host":host.id,"entrymethods":entrymethods,"maxentries":maxentries,"prize":prize})
        self.active_channels.append(channel.id)

    @commands.command(description = "Manually give entries to a user.",help = "grantentries <entry amount> <member>")
    @lottery_role_check()
    async def grantentries(self,ctx,entrycount:int,member:discord.Member):
        if entrycount < 1:
            return await ctx.reply("Kind of need to grant at least one entry.")
        ref = db.reference("/",app = firebase_admin._apps['lottery'])

        active = ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("active").get()
        if not active:
            return await ctx.reply("Are you sure there's a lottery active in this channel? Doesn't seem like it")

        lotteries = ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).get()
        entries = lotteries.get("entries",{})
        maxentries = lotteries.get("maxentries")
        currententries = lotteries.get("currententries",0)
        maxentries = lotteries.get('maxentries',None)

        if maxentries:
            if currententries + int(entrycount) > int(maxentries):
                return await ctx.reply("Wait a minute, that would exceed the maximum entry count.")

        personentries = entries.get(str(member.id),0)

        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("entries").child(str(member.id)).set(personentries + entrycount)
        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("currententries").set(currententries + entrycount)

        embed = discord.Embed(title = f"Entries Added!",description = f"Added `{entrycount}` entries for {member}. They now have `{personentries + entrycount}` total entries in this lottery!", color = discord.Color.random())
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.send(embed = embed)

    @commands.command(description = "Manually remove entries from a user.",help = "removeentries <entry amount> <member>")
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
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.send(embed = embed)


    @commands.command(description = "End the ongoing lottery in the channel, and give out the winner. Also can be used to reroll.",help = "lotteryend")
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
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon_url)
        await message.edit(embed = embed)

        host = ctx.guild.get_member(int(host))
        embed = discord.Embed(title = f"🏆 Your Lottery is now Over!",description = f"Your lottery for `{prize}` is now over.\nWith `{len(tickets)}` total entries, the winner is <@{tickets[winner]}>!\n[Link to Ending Message]({message.jump_url})", color = discord.Color.gold())
        dm = host.dm_channel
        if dm == None:
            dm = await host.create_dm()
        await dm.send(embed = embed)

        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).child("active").set(False)
        #ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).delete()

    @commands.command(description = "Cancel the lottery, and do NOT give out a winner. All lottery data for the lottery will be deleted.",help = "lotterycancel")
    @lottery_role_check()
    async def lotterycancel(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['lottery'])

        lotteries = ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).get()

        if not lotteries:
            return await ctx.reply("Are you sure there's a lottery active in this channel? Doesn't seem like it")

        ref.child(str(ctx.guild.id)).child(str(ctx.channel.id)).delete()
        await ctx.reply("Lottery data deleted and cancelled.")

    @commands.command(description = "View the info for the lottery in the specified or currenct channel.",help = "lotteryinfo [channel]")
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
        embed.timestamp = datetime.datetime.utcnow()
        count = 1
        for type,details in lotteries.get("entrymethods",{}).items():
            embed.add_field(name = f"Entry Method {count}: {type}",value = f"**Amount Needed:** {details['amount']}\n**Entries Given:** {details['entries']}")
            count += 1
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon_url)
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

    @commands.command(description = "View the info your own or another member lottery entries.",help = "lotteryprofile [member]")
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
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon_url)

        await ctx.send(embed = embed)

    @commands.command(description = "View all active lottery in the server.",help = "lotteryserver")
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
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon_url)

        await ctx.send(embed = embed)

    @commands.command(description = "Who has most entry in lottery? Who knows.",help = "lotteryleaderboard [channel]")
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
        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name} Lottery System',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = emb)

def setup(client):
    client.add_cog(Lottery(client))