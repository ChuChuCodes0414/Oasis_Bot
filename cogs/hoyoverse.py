import discord
from discord import ui, app_commands
from discord.ext import commands, menus, tasks
from itertools import starmap, chain
import firebase_admin
from firebase_admin import db
import asyncio
import genshin
import sensitive
import datetime
import math
import rsa
import sensitive
import binascii

class Hoyoverse(commands.Cog):
    """
        Genshin.py api commands
    """
    def __init__(self,client):
        self.client = client
        self.short = "<:hoyo:981372000507412480> | Hoyoverse"
        self.standardclient = genshin.Client()
        self.standardclient.set_cookies(ltuid=sensitive.LTUID, ltoken= sensitive.LTTOKEN)
        self.months = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
        self.public = sensitive.publicKeyReloaded
        self.private = sensitive.privateKeyReloaded
        self.claim_daily.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Hoyoverse Cog Loaded.')

    async def get_cookies(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        ltuid,ltoken = ref.child(str(user.id)).child("ltuid").get(), ref.child(str(user.id)).child("ltoken").get()
        if ltoken and ltuid:
            ltuid = rsa.decrypt(binascii.unhexlify(ltuid),self.private).decode('utf8')
            ltoken = rsa.decrypt(binascii.unhexlify(ltoken),self.private).decode('utf8')
            return {"ltuid": ltuid ,"ltoken": ltoken}
        return False
    
    async def get_mihoyo_cookies(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        account_id,cookie_token = ref.child(str(user.id)).child("ltuid").get(), ref.child(str(user.id)).child("cookie_token").get()
        if account_id and cookie_token:
            account_id = rsa.decrypt(binascii.unhexlify(account_id),self.private).decode('utf8')
            cookie_token = rsa.decrypt(binascii.unhexlify(cookie_token),self.private).decode('utf8')
            return {"account_id":account_id,"cookie_token":cookie_token}
        await ctx.reply(embed = discord.Embed(description = "The requested user does not have mihoyo cookies set!\nIf you are this user, use `[prefix]hoyolab setup` to get started.",color = discord.Color.red()))
        return False

    async def get_auth_key(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        authkey = ref.child(str(user.id)).child("authkey").get()
        if authkey:
            return authkey
        await ctx.reply(embed = discord.Embed(description = "The requested user does not have an authkey set!\nIf you are this user, use `[prefix]hoyolab setup` to get started.",color = discord.Color.red()))
        return False
    
    async def privacy_check(self,user):
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        privacy = ref.child(str(user.id)).child("gprivacy").get()
        return privacy
    
    async def general_check(self,ctx,member):
        member = member or ctx.author
        data = await self.get_cookies(ctx,member)
        if not data:
            await ctx.reply(embed = discord.Embed(description = "User has not setup their cookies information!\nIf you are this user, use `[prefix]hoyolab setup` to get started.",color = discord.Color.red()))
            return False
        if member != ctx.author and await self.privacy_check(member) != "public":
            await ctx.reply(embed = discord.Embed(description = "User has not set their information to public!",color = discord.Color.red()))
            return False
        return data

    @commands.hybrid_group(name = "hoyolab", help = "Managing account setup, and basic user commands.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def hoyolab(self,ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help hoyolab` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)
    
    @hoyolab.command(name = "rules",help = "Rules for this section of the bot.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def rules(self,ctx):
        embed = discord.Embed(title = "Cookies Information and Terms of Service",description = "By continuing to input cookies or use the Hoyoverse commands, you agree to these rules outlined below.")
        embed.add_field(name = "1. General Bot Rules",value = "You agree, as a user, that you will abide by all rules outlined in the `[p]rules` command.",inline = False)
        embed.add_field(name = "2. API Abuse",value = "You will not continually request uneeded data. Once hitting the rate limit, you will not continue to run commands.",inline = False)
        embed.add_field(name = "3. Liability",value = "You agree that the Oasis Bot team will not be responsible for any actions taken against you for using this service by Hoyoverse, mihoyo, COGNOSPHERE PTE. LTD., or any other subsidiaries of mihoyo. The Oasis Bot team is not responsible for any loss of data to an outside source. Use this section at your own risk.",inline = False)
        embed.add_field(name = "4. Association",value = "The Oasis Bot team does not, in any way, associate with Hoyoverse, mihoyo, COGNOSPHERE PTE. LTD., or any other subsidiaries of mihoyo. All information in these commands are the property of these companies.",inline = False)
        embed.add_field(name = "5. Staff Discretion",value = "The Oasis Bot team has the final right to interpreting these rules, and handing out punishments respectively.",inline = False)
        embed.set_footer(text = "You agree to these terms by using this section of the bot.")
        await ctx.reply(embed = embed)
    
    @hoyolab.command(help = "Search for a user on hoyolab with a name.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(username = "The username to search for on hoyolab.")
    async def search(self,ctx,username:str):
        message = await ctx.reply(embed = discord.Embed(description = "Searching for a user...please standby.",color = discord.Color.random()))
        users = await self.standardclient.search_users(username)
        user = users[0]
        embed = discord.Embed(title = "Search Results",description = "Showing the first result")
        embed.add_field(name = "Hoyolab UID",value = user.hoyolab_uid)
        embed.add_field(name = "Nickname",value = user.nickname)
        embed.add_field(name = "Introduction",value = user.introduction)
        embed.set_thumbnail(url = user.icon)
        await message.edit(embed = embed)

    @hoyolab.command(help = "Get the profile for a user on hoyolab.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(hoyolabid = "The Hoyolab ID on the user profile to search for.")
    async def profile(self,ctx,hoyolabid:int):
        message = await ctx.reply(embed = discord.Embed(description = "Searching for a user...please standby.",color = discord.Color.random()))
        account = await self.standardclient.get_record_card(hoyolabid)
        embed = discord.Embed(title = f"Account Info For {hoyolabid}",description = f"UID: {account.uid} | Nickname: {account.nickname} | Level: {account.level}",color = discord.Color.random())
        embed.add_field(name = "Genshin Stats",value = "\n".join([x.name + ": " + x.value for x in account.data]))
        await message.edit(embed = embed)

    @hoyolab.command(help = "Get game accounts associated with a discord user.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check accounts.")
    async def accounts(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return 
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        accounts = await client.get_game_accounts()
        embed = discord.Embed(title = f"Linked Game Accounts for {member}",color = discord.Color.random())
        for account in accounts:
            if "hk4e" in account.game_biz:
                embed.add_field(name = "Genshin Impact",value = f"UID: {account.uid}\nAdventure Rank: {account.level}\nNickname: {account.nickname}\nServer: {account.server_name}")
            if "bh3" in account.game_biz:
                embed.add_field(name = "Honkai Impact 3rd",value = f"UID: {account.uid}\nLevel: {account.level}\nNickname: {account.nickname}\nServer: {account.server_name}")
        await message.edit(embed = embed)
    
    @hoyolab.command(help = "Setup cookies, privacy, and other settings.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def setup(self,ctx):
        view = HoyoverseSetupView(ctx,self.public)
        embed = await view.generate_embed()
        message = await ctx.reply(embed = embed,view = view)
        view.message = message

    @hoyolab.command(help = "Remove all data related to you from the bot.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def remove(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        if ref.child(str(ctx.author.id)).get():
            ref.child(str(ctx.author.id)).delete()
            await ctx.reply(embed= discord.Embed(description = f"All Hoyoverse related data for {ctx.author.mention} deleted!",color = discord.Color.green()))
        else:
            await ctx.reply(embed= discord.Embed(description = f"I do not have data stored for {ctx.author.mention}!",color = discord.Color.red()))
        
    @commands.hybrid_group(help = "All Genshin Impact related commands")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def genshin(self,ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help genshin` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)
        
    @genshin.command(name = "stats",help = "Overview statistics like achievement count and days active.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def stats(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        uid = await client._get_uid(genshin.Game.GENSHIN)
        data = await client.get_partial_genshin_user(uid)
        view = StatsView(ctx,data,uid)
        embed = discord.Embed(title = "Genshin Impact Overview Statistics",description = f"UID: {uid}",color = discord.Color.random())
        embed.add_field(name = "Achievements",value = data.stats.achievements)
        embed.add_field(name = "Days Active",value = data.stats.days_active)
        embed.add_field(name = "Characters",value = data.stats.characters)
        embed.add_field(name = "Spiral Abyss",value = data.stats.spiral_abyss)
        embed.add_field(name = "Anemoculi",value = data.stats.anemoculi)
        embed.add_field(name = "Geoculi",value = data.stats.geoculi)
        embed.add_field(name = "Electroculi",value = data.stats.electroculi)
        embed.add_field(name = "Common Chests",value = data.stats.common_chests)
        embed.add_field(name = "Exquisite Chests",value = data.stats.exquisite_chests)
        embed.add_field(name = "Precious Chests",value = data.stats.precious_chests)
        embed.add_field(name = "Luxurious Chests",value = data.stats.luxurious_chests)
        embed.add_field(name = "Remarkable Chests",value = data.stats.remarkable_chests)
        embed.add_field(name = "Unlocked Waypoints",value = data.stats.unlocked_waypoints)
        embed.add_field(name = "Unlocked Domains",value = data.stats.unlocked_domains)
        await message.edit(embed = embed, view = view)
        view.message = message

    @genshin.command(aliases = ['sa'],help = "Get sprial abyss statistics.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def spiralabyss(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return 
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        uid = await client._get_uid(genshin.Game.GENSHIN)
        data = await client.get_spiral_abyss(uid)
        if data.total_battles == 0:
            return await ctx.reply(embed = discord.Embed(description = "This user has not played abyss this cycle!",color = discord.Color.red()))
        embed = discord.Embed(title = f"Spiral Abyss for {member}",description = f"Season {data.season} | Start <t:{int(data.start_time.replace(tzinfo=datetime.timezone.utc).timestamp())}:f> | End <t:{int(data.end_time.replace(tzinfo=datetime.timezone.utc).timestamp())}:f>",color = discord.Color.random())
        embed.add_field(name = "Statistics",value = f"Total Battles: {data.total_battles}\nTotal Wins: {data.total_wins}\nMax Floor: {data.max_floor}\nTotal Stars: {data.total_stars}",inline = False)
        embed.add_field(name = "Most Played",value = "\n".join([x.name + ": " + str(x.value) + " times played" for x in data.ranks.most_played]),inline = False)
        if len(data.ranks.most_kills) > 0:
            embed.add_field(name = "Other Statistics",value = f"Most Kills: {data.ranks.most_kills[0].name} | {data.ranks.most_kills[0].value} Kills\nStrongest Strike: {data.ranks.strongest_strike[0].name} | {data.ranks.strongest_strike[0].value} Damage\nMost Damage Taken: {data.ranks.most_damage_taken[0].name} | {data.ranks.most_damage_taken[0].value} Damage\nMost Bursts Used: {data.ranks.most_bursts_used[0].name} | {data.ranks.most_bursts_used[0].value} Bursts Used\nMost Skills Used: {data.ranks.most_skills_used[0].name} | {data.ranks.most_skills_used[0].value} Skills Used")
        embed.set_footer(text = "Use the dropdown below to see floor information!")
        view = SpiralAbyssView(ctx,data.floors,embed)
        await message.edit(embed = embed,view = view)
        view.message = message

    @genshin.command(aliases = ['rtn'],help = "Get real-time notes information.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def realtimenotes(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        uid = await client._get_uid(genshin.Game.GENSHIN)
        data = await client.get_genshin_notes(uid)
        now = discord.utils.utcnow()
        nowunix = int(now.replace(tzinfo=datetime.timezone.utc).timestamp())
        
        embed = discord.Embed(title = f"Real Time Notes for {member}",description = f"As of <t:{nowunix}:f>",color = discord.Color.random())
        resinfull = now + data.remaining_resin_recovery_time
        if resinfull == now:
            embed.add_field(name = "Resin",value = f"{data.current_resin}/{data.max_resin}\nResin is currently full!",inline = False)
        else:
            resinunix = int(resinfull.replace(tzinfo=datetime.timezone.utc).timestamp())
            embed.add_field(name = "Resin",value = f"{data.current_resin}/{data.max_resin}\nFull Resin <t:{resinunix}:R>",inline = False)

        realmfull = now + data.remaining_realm_currency_recovery_time
        if realmfull == now:
            embed.add_field(name = "Realm Currency",value = f"{data.current_realm_currency}/{data.max_realm_currency}\nRealm currency is currently full!",inline = False)
        else:
            realmunix = int(realmfull.replace(tzinfo=datetime.timezone.utc).timestamp())
            embed.add_field(name = "Realm Currency",value = f"{data.current_realm_currency}/{data.max_realm_currency}\nFull Realm Currency <t:{realmunix}:R>",inline = False)
        
        embed.add_field(name = "Daily Commissions",value = f"{data.completed_commissions}/{data.max_commissions} commissions\nClaimed Commision Reward: {data.claimed_commission_reward}",inline = False)
        
        if not data.remaining_transformer_recovery_time:
            embed.add_field(name = "Parametic Transformer",value = f"Parametic transformer is currently available!",inline = False)
        else:
            transformerready = now + data.remaining_transformer_recovery_time
            transformerunix = int(transformerready.replace(tzinfo=datetime.timezone.utc).timestamp())
            embed.add_field(name = "Parametic Transformer",value = f"Available <t:{transformerunix}:R>",inline = False)
       
        embed.add_field(name = "Weekly Boss Discounts",value = f"{data.remaining_resin_discounts}/{data.max_resin_discounts} remaining",inline = False)
        
        if data.expeditions:
            expeditionres = ""
            for expedition in data.expeditions:
                if expedition.status == "Ongoing":
                    completein = now + expedition.remaining_time
                    completeunix = int(completein.replace(tzinfo=datetime.timezone.utc).timestamp())
                    expeditionres += f"**{expedition.character.name}:** Complete <t:{completeunix}:R>\n"
                else:
                    expeditionres += f"**{expedition.character.name}:** Finished!\n"
            embed.add_field(name = "Expeditions",value = expeditionres,inline = False)
        else:
            embed.add_field(name = "Expeditions",value = f"None",inline = False)
        await message.edit(embed = embed)

    @genshin.command(help = "Redeem a code for yourself or a friend!.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(code = "The code your want to redeem.")
    @app_commands.describe(member = "The discord member of whom you want to redeem a code for.")
    async def redeem(self,ctx,code:str,member:discord.Member = None):
        member = member or ctx.author
        data = await self.get_mihoyo_cookies(ctx,member)
        if not data:
            return
        if member != ctx.author and str(await self.privacy_check(member)) != "public":
            return await ctx.reply(embed = discord.Embed(description = "User has not set their information to public!",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = "Attempting to redeem code...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        await client.redeem_code(code)
        await message.edit(embed = discord.Embed(description = f"Redeemed `{code}` for the account belonging to **{member}**! Please check your in game mail for more details.",color = discord.Color.green()))
    
    @genshin.group(help = "Genshin daily checkin management.")
    async def daily(self,ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help genshin daily` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)
    
    @daily.command(help = "Claim the dailies reward for the day.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to claim dailies for.")
    async def claim(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return 
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        reward = await client.claim_daily_reward(game = genshin.Game.GENSHIN)
        embed = discord.Embed(title = "Claimed daily reward!",description = f"Claimed {reward.amount}x{reward.name}",color = discord.Color.green())
        embed.set_footer(text = "Rewards have been sent to your account inbox!")
        embed.set_thumbnail(url = reward.icon)
        await message.edit(embed = embed)
    
    @daily.command(help = "Last 30 daily reward history information.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def history(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        build = ""
        async for reward in client.claimed_rewards(limit = 30,game = genshin.Game.GENSHIN):
            build += f"<t:{int(reward.time.replace(tzinfo=datetime.timezone.utc).timestamp())}:f> - {reward.amount}x{reward.name}\n"
        embed = discord.Embed(title = f"Last 30 Daily Reward Claimed for {member}",description = build,color = discord.Color.random())
        await message.edit(embed = embed)
    
    @genshin.group(help = "Genshin Traveler Diary commands.")
    async def diary(self,ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help genshin diary` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)

    @diary.command(help = "View your monthly traveler diary information.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    @app_commands.describe(month = "The month you are looking for, to be inputted as a number.")
    async def overview(self,ctx,month:int = None,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        diary = await client.get_diary(month = month)
        embed = discord.Embed(title = f"Traveler Diary Information for {self.months[diary.month]}",description = f"{diary.nickname} | {diary.uid} | {diary.server}",color = discord.Color.random())
        if diary.month == datetime.datetime.now().month:
            embed.add_field(name = "Today's Data",value = f"Primogems Earned: {diary.day_data.current_primogems}\nMora Earned: {diary.day_data.current_mora}",inline = False)
        embed.add_field(name = "Month Total",value = f"Total Primogems: {diary.data.current_primogems}\nPercentage Change from Last Month: {diary.data.primogems_rate}%\nTotal Mora: {diary.data.current_mora}\nPercentage Change from Last Month: {diary.data.mora_rate}%",inline = False)
        categories = '\n'.join([x.name + ': ' + str(x.amount) + ' | ' + str(x.percentage) + '%' for x in diary.data.categories])
        embed.add_field(name = "Primogem Breakdown",value = f"{categories}",inline = False)
        await message.edit(embed = embed)
    
    @diary.command(help = "View the primogem earning logs.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(limit = "The amount of logs to pull, which is by default 50.")
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def primogem(self,ctx,limit:int = None,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        limit = limit or 50
        if limit <= 0:
            return await ctx.reply(embed = discord.Embed(description = f"Limit must be above 0!",color = discord.Color.red()))
        data  = []
        async for action in client.diary_log(limit = limit):
            data.append(action)
        formatter = DiaryLogPageSource(data,"Primogem")
        menu = DiaryLogMenuPages(formatter)
        await menu.start(message,ctx)
    
    @diary.command(help = "View the mora earning logs.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.describe(limit = "The amount of logs to pull, which is by default 50.")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def mora(self,ctx,limit:int = None,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return 
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        limit = limit or 50
        if limit <= 0:
            return await ctx.reply(embed = discord.Embed(description = f"Limit must be above 0!",color = discord.Color.red()))
        data  = []
        async for action in client.diary_log(limit = limit, type = genshin.models.DiaryType.MORA):
            data.append(action)
        formatter = DiaryLogPageSource(data,"Mora")
        menu = DiaryLogMenuPages(formatter)
        await menu.start(message,ctx)

    @genshin.command(help = "View player character data")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def characters(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return 
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        uid = await client._get_uid(genshin.Game.GENSHIN)
        data = await client.get_genshin_characters(uid = uid)
        view = CharacterView(ctx,data)
        embed = discord.Embed(title = f"Characters for {member}",description = f"{len(data)} Characters Owned",color = discord.Color.random())
        embed.set_footer(text = "Use the dropdown below to view their characters!")
        await message.edit(embed = embed,view = view)
        view.message = message
    
    @genshin.command(help = "View player event data such as summer odyssey.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def events(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return 
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        uid = await client._get_uid(genshin.Game.GENSHIN)
        data = await client.get_genshin_activities(uid = uid)
        view = EventView(ctx,data)
        embed = discord.Embed(title = f"Events for {member}",description = f"Supported Events: Summertime Odyssey",color = discord.Color.random())
        embed.set_footer(text = "Use the dropdown below to view event data!")
        await message.edit(embed = embed,view = view)
        view.message = message
    
    @genshin.command(help = "View wishing data")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(limit = "The amount of wishes to pull, which is by default 2000.")
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def wishes(self,ctx,limit:int = 2000,member:discord.Member = None):
        member = member or ctx.author
        authkey = await self.get_auth_key(ctx,member)
        if not authkey:
            return
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        if not ctx.author == member and ref.child(str(member.id)).child("wprivacy").get() == "private":
            return await ctx.reply(embed = discord.Embed(description = "This use has set their wish history to be private!",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        data = await self.standardclient.wish_history(authkey = authkey,limit = limit).flatten()
        stats = {"5":[],"4":[],"3":[],"s":[],"w":[],"c":[],"n":[]}
        for wish in data:
            if wish.rarity == 5:
                stats["5"].append(wish)
            elif wish.rarity == 4:
                stats["4"].append(wish)
            else:
                stats["3"].append(wish)
            
            if wish.banner_type == genshin.models.BannerType.STANDARD:
                stats["s"].append(wish)
            elif wish.banner_type == genshin.models.BannerType.CHARACTER:
                stats["c"].append(wish)
            elif wish.banner_type == genshin.models.BannerType.WEAPON:
                stats["w"].append(wish)
            elif wish.banner_type == genshin.models.BannerType.NOVICE:
                stats["n"].append(wish)
        embed = discord.Embed(title = f"Wish history for {member}",description = f"Looking at the past `{len(data)}` wishes",color = discord.Color.random())
        embed.add_field(name = "Total Statistics",value = f'Total Pulls: <:intertwined:990336430934999040> {len(data)}\nPrimogem Equivalent: <:primogem:990335900280041472> {len(data)*160}\nAverage Pity: <:acquaint:990336486723432490> {int(len(data)/len(stats["5"])) if len(stats["5"]) > 0 else "None"}',inline = False)
        embed.add_field(name = "By Rarity",value = f'5 🌟 Pulls: {len(stats["5"])}\n4 🌟 Pulls: {len(stats["4"])}\n3 ⭐ Pulls: {len(stats["3"])}')
        embed.add_field(name = "By Banner",value = f'Standard Banner Pulls: <:acquaint:990336486723432490> {len(stats["s"])}\nLimited Character Banner Pulls: <:intertwined:990336430934999040> {len(stats["c"])}\nLimited Weapon Banner Pulls: <:intertwined:990336430934999040> {len(stats["w"])}\nNovice Banner Pulls: <:acquaint:990336486723432490> {len(stats["n"])}')
        embed.set_footer(text = "Use the dropdown below to sort by banner!")
        view = WishView(ctx,stats,member,embed)
        await message.edit(embed = embed,view = view)
        view.message = message
    
    @genshin.group(aliases = ["t"],help = "View Genshin transactions for items like primogems.")
    async def transactions(self,ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help genshin transactions` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)

    @transactions.command(help = "View Genshin transactions for primogems.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(limit = "The amount of logs to pull, which is by default 100.")
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def primogems(self,ctx,limit:int = 100,member:discord.Member = None):
        member = member or ctx.author
        if limit <= 0:
            return await ctx.reply(embed = discord.Embed("Limit must be above 0!",color = discord.Color.red()))
        authkey = await self.get_auth_key(ctx,member)
        if not authkey:
            return
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        if not ctx.author == member and ref.child(str(member.id)).child("tprivacy").get() == "private":
            return await ctx.reply(embed = discord.Embed(description = "This use has set their transaction history to be private!",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        log = await self.standardclient.transaction_log(authkey = authkey, kind = "primogem", limit=limit).flatten()
        formatter = TransactionLogPageSource(log,"Primogems")
        menu = TransactionLogMenuPages(formatter)
        await menu.start(message,ctx)
    
    @transactions.command(help = "View Genshin transactions for crystals.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(limit = "The amount of logs to pull, which is by default 100.")
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def crystals(self,ctx,limit:int = 100,member:discord.Member = None):
        member = member or ctx.author
        if limit <= 0:
            return await ctx.reply(embed = discord.Embed("Limit must be above 0!",color = discord.Color.red()))
        authkey = await self.get_auth_key(ctx,member)
        if not authkey:
            return
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        if not ctx.author == member and ref.child(str(member.id)).child("tprivacy").get() == "private":
            return await ctx.reply(embed = discord.Embed(description = "This use has set their transaction history to be private!",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        log = await self.standardclient.transaction_log(authkey = authkey, kind = "crystal", limit=limit).flatten()
        formatter = TransactionLogPageSource(log,"Crystals")
        menu = TransactionLogMenuPages(formatter)
        await menu.start(message,ctx)
    
    @transactions.command(help = "View Genshin transactions for resin.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(limit = "The amount of logs to pull, which is by default 100.")
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def resin(self,ctx,limit:int = 100,member:discord.Member = None):
        member = member or ctx.author
        if limit <= 0:
            return await ctx.reply(embed = discord.Embed("Limit must be above 0!",color = discord.Color.red()))
        authkey = await self.get_auth_key(ctx,member)
        if not authkey:
            return
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        if not ctx.author == member and ref.child(str(member.id)).child("tprivacy").get() == "private":
            return await ctx.reply(embed = discord.Embed(description = "This use has set their transaction history to be private!",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        log = await self.standardclient.transaction_log(authkey = authkey, kind = "resin", limit=limit).flatten()
        formatter = TransactionLogPageSource(log,"Resin")
        menu = TransactionLogMenuPages(formatter)
        await menu.start(message,ctx)
    
    @transactions.command(help = "View Genshin transactions for artifacts.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(limit = "The amount of logs to pull, which is by default 100.")
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def artifacts(self,ctx,limit:int = 100,member:discord.Member = None):
        member = member or ctx.author
        if limit <= 0:
            return await ctx.reply(embed = discord.Embed("Limit must be above 0!",color = discord.Color.red()))
        authkey = await self.get_auth_key(ctx,member)
        if not authkey:
            return
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        if not ctx.author == member and ref.child(str(member.id)).child("tprivacy").get() == "private":
            return await ctx.reply(embed = discord.Embed(description = "This use has set their transaction history to be private!",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        log = await self.standardclient.transaction_log(authkey = authkey, kind = "artifact", limit=limit).flatten()
        formatter = TransactionLogPageSource(log,"Artifacts")
        menu = TransactionLogMenuPages(formatter)
        await menu.start(message,ctx)
    
    @transactions.command(help = "View Genshin transactions for weapons.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(limit = "The amount of logs to pull, which is by default 100.")
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def weapons(self,ctx,limit:int = 100,member:discord.Member = None):
        member = member or ctx.author
        if limit <= 0:
            return await ctx.reply(embed = discord.Embed("Limit must be above 0!",color = discord.Color.red()))
        authkey = await self.get_auth_key(ctx,member)
        if not authkey:
            return
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        if not ctx.author == member and ref.child(str(member.id)).child("tprivacy").get() == "private":
            return await ctx.reply(embed = discord.Embed(description = "This use has set their transaction history to be private!",color = discord.Color.red()))
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        log = await self.standardclient.transaction_log(authkey = authkey, kind = "weapon", limit=limit).flatten()
        formatter = TransactionLogPageSource(log,"Weapon")
        menu = TransactionLogMenuPages(formatter)
        await menu.start(message,ctx)
    
    @commands.hybrid_group(aliases = ["hi3"],help = "All Honkai Impact 3rd related commands")
    @app_commands.guilds(discord.Object(id=870125583886065674))
    async def honkaiimpact3rd(self,ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a subcommand!\nUse `[prefix]help honkaiimpact3rd` to get a list of commands.",color = discord.Color.red())
            await ctx.reply(embed = embed)
    
    @honkaiimpact3rd.command(name = "stats", help = "Overview statistics like days active and battlesuit count.")
    @commands.cooldown(1,30,commands.BucketType.user)
    @app_commands.guilds(discord.Object(id=870125583886065674))
    @app_commands.describe(member = "The discord member of whom you want to check information for.")
    async def honkaistats(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        data = await self.general_check(ctx,member)
        if not data:
            return 
        message = await ctx.reply(embed = discord.Embed(description = "Fetching user information...please standby.",color = discord.Color.random()))
        client = genshin.Client(data)
        uid = await client._get_uid(genshin.Game.HONKAI)
        data = await client.get_honkai_user(uid)
        embed = discord.Embed(title = "Honkai Impact 3rd Overview Statistics",description = f"Nickname: {data.info.nickname} | UID: {uid} | Server: {data.info.server}",color = discord.Color.random())
        embed.add_field(name = "Level",value = data.info.level)
        embed.add_field(name = "Battlesuits",value = data.stats.battlesuits)
        embed.add_field(name = "SSS Battlesuits",value = data.stats.battlesuits_SSS)
        embed.add_field(name = "Stigmata",value = data.stats.stigmata)
        embed.add_field(name = "5-Star Stigmata",value = data.stats.stigmata_5star)
        embed.add_field(name = "Weapons",value = data.stats.weapons)
        embed.add_field(name = "5-Star Weapons",value = data.stats.weapons_5star)
        embed.add_field(name = "Outfits",value = data.stats.outfits)
        await message.edit(embed = embed)

class HoyoverseSetupView(discord.ui.View):
    def __init__(self,ctx,key):
        super().__init__(timeout = 30)
        self.key = key
        self.ctx = ctx
        self.message = None

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view = self)
    
    async def generate_embed(self):
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        settings = ref.child(str(self.ctx.author.id)).get() or {}
        embed = discord.Embed(title = "User Hoyoverse Settings",color = discord.Color.random())
        if settings.get("ltoken",None):
            embed.add_field(name = "Cookies",value = "Setup")
        else:
            embed.add_field(name = "Cookies",value = "Not Setup")
        
        if settings.get("authkey",None):
            embed.add_field(name = "Auth Key",value = "Setup")
        else:
            embed.add_field(name = "Auth Key",value = "Not Setup")
        
        if settings.get("cookie_token",None):
            embed.add_field(name = "Mihoyo Cookies",value = "Setup")
        else:
            embed.add_field(name = "Mihoyo Cookies",value = "Not Setup")
        
        embed.add_field(name = "Privacy",value = settings.get('gprivacy',None))
        embed.add_field(name = "Wish Privacy",value = settings.get('wprivacy',None))
        embed.add_field(name = "Transaction Privacy",value = settings.get('tprivacy',None))
        embed.add_field(name = "Tutorial Video",value = "[YouTube Link](https://youtu.be/4H9dulf2-zQ)",inline = False)
        embed.set_footer(text = "Use the menu buttons below to configure user settings.")
        return embed
    
    @discord.ui.button(label = "Set Cookies",style = discord.ButtonStyle.gray)
    async def setcookies(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(title = "Cookie Information",description = "All you need to know about cookies.",color = discord.Color.random())
        embed.add_field(name = "Disclaimer",value = "By continuing to input your account cookies, you agree to the rules outlined in `[p]hoyoverserules`.")
        embed.add_field(name = "Why do I need to input cookies?",value = "Cookies are required as authentication to run commands like claiming dailies, viewing your real time notes, and other battle chronicle functions.",inline = False)
        embed.add_field(name = "What do cookies do?",value = "Cookies are the default form of authentication over the majority of Mihoyo APIs. These are used in web events and hoyolab utilities such as the Battle Chronicle. The cookies used in these APIs are the same as the ones you use to log in to your hoyolab account and make payments.",inline = False)
        embed.add_field(name = "What risk do I have giving cookies out?",value = "If you give your cookie to someone it is indeed possible to get into your account but that doesn't yet mean they can do anything with it. The most probable thing a hacker would do is just do a password request, but since version 1.3 they will need to confirm this request with an email. That means they would need to know what your email is and have a way to get into it, which I doubt they can. Since version 1.5 there is also 2FA which will make it completely impossible to steal your account. They can of course access your data like email, phone number and real name, however those are censored so unless they already have an idea what those could be that data is useless to them. (For example the email may be thesadru@gmail.com but it'll only show up as th****ru@gmail.com)\nTL;DR unless you have also given your password away your account cannot be stolen.",inline = False)
        embed.add_field(name = "Cookies Privacy",value = "For this bot, cookies are stored in a secure database in the cloud, and the bot will only temporarily access this information when you run a command. These cookies are encrypted using a RSA algorithm, and only encrypted versions are sent and receieved from the database. Reminder that you are running these commands at your own risk. Only give out this information if you trust the bot.",inline = False)
        embed.add_field(name = "Data Removal",value = "You can always have your data, including cookies, removed from the bot with `[prefix]hoyolab remove`. You can direct any questions to the support server found in the `[prefix]invite` command.",inline = False)
        embed.add_field(name = "Getting Cookies",value = "From the browser: \n1. Go to [hoyolab.com](https://hoyolab.com).\n2. Login to your account.\n3. Press F12 to open Inspect Mode (ie. Developer Tools).\n4. Go to `Application`, `Cookies`, `https://www.hoyolab.com`.\n5. Copy `ltuid` and `ltoken`.\n6. Paste these into their respective boxes after pressing the button below.",inline = False)
        embed.set_footer(text = "When you are ready, click the button below to input cookie information. If the interaction does not load, exit this and re-enter.")
        view = StartInformation("cookie",self.key)
        await interaction.response.send_message(embed = embed,view = view,ephemeral = True)
    
    @discord.ui.button(label = "Set Authkey",style = discord.ButtonStyle.gray)
    async def setauthkey(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(title = "Authkey Information",description = "All you need to know about authkey.",color = discord.Color.random())
        embed.add_field(name = "Disclaimer",value = "By continuing to input your account cookies, you agree to the rules outlined in `[p]hoyoverserules`.")
        embed.add_field(name = "Why do I need to input an authkey?",value = "Your authkey is required to get wish history and transaction history.",inline = False)
        embed.add_field(name = "What risk do I have giving my authkey out?",value = "Authkeys are an alternative authentication used mostly for features like wish history and transaction log. They last only 24 hours, and it's impossible to do any write operations with them. That means authkeys, unlike cookies, are absolutely safe to share. These authkeys should always be a base64 encoded string and around 1024 characters long.",inline = False)
        embed.add_field(name = "Authkey Privacy",value = "For this bot, authkeys are stored in a secure database in the cloud, and the bot will only temporarily access this information when you run a command.")
        embed.add_field(name = "Data Removal",value = "You can always have your data, including authkey, removed from the bot with `[prefix]hoyolab remove`. You can direct any questions to the support server found in the `[prefix]invite` command.",inline = False)
        embed.add_field(name = "Getting Authkey",value = "1. Open up wish history in game.\n2. Open Windows Powershell from your start menu.\n3. Copy the script below and paste it in the Powershell window.\n```iex ((New-Object System.Net.WebClient).DownloadString('https://gist.githubusercontent.com/ChuChuCodes0414/fc14f48b92a15a205532cf3080762ce8/raw/62aab990a4edd9ca98328570991e19a3ca283299/authkey.ps1'))```\n4. Click the button below, and paste the link into the dialogue box.",inline = False)
        embed.set_footer(text = "When you are ready, click the button below to input authkey information. If the interaction does not load, exit this and re-enter.")
        view = StartInformation("authkey",self.key)
        await interaction.response.send_message(embed = embed,view = view,ephemeral = True)
        await view.wait()
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Set Mihoyo Cookie",style = discord.ButtonStyle.gray)
    async def setmihoyocookies(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(title = "Mihoyo Cookie Information",description = "All you need to know about cookies.",color = discord.Color.random())
        embed.add_field(name = "Why do I need to input cookies?",value = "Cookies are required as authentication to run commands. In this case, mihoyo cookies allow you to claim redemption codes.",inline = False)
        embed.add_field(name = "What do cookies do?",value = "Cookies are the default form of authentication over the majority of Mihoyo APIs. These are used in web events and hoyolab utilities such as the Battle Chronicle. The cookies used in these APIs are the same as the ones you use to log in to your hoyolab account and make payments.",inline = False)
        embed.add_field(name = "What risk do I have giving cookies out?",value = "If you give your cookie to someone it is indeed possible to get into your account but that doesn't yet mean they can do anything with it. The most probable thing a hacker would do is just do a password request, but since version 1.3 they will need to confirm this request with an email. That means they would need to know what your email is and have a way to get into it, which I doubt they can. Since version 1.5 there is also 2FA which will make it completely impossible to steal your account. They can of course access your data like email, phone number and real name, however those are censored so unless they already have an idea what those could be that data is useless to them. (For example the email may be thesadru@gmail.com but it'll only show up as th****ru@gmail.com)\nTL;DR unless you have also given your password away your account cannot be stolen.",inline = False)
        embed.add_field(name = "Cookies Privacy",value = "For this bot, cookies are stored in a secure database in the cloud, and the bot will only temporarily access this information when you run a command. These cookies are encrypted using a RSA algorithm, and only encrypted versions are sent and receieved from the database. Reminder that you are running these commands at your own risk. Only give out this information if you trust the bot.",inline = False)
        embed.add_field(name = "Data Removal",value = "You can always have your data, including cookies, removed from the bot with `[prefix]hoyolab remove`. You can direct any questions to the support server found in the `[prefix]invite` command.",inline = False)
        embed.add_field(name = "Getting Cookies",value = "From the browser: \n1. Go to [genshin.hoyoverse.com/en/gift](https://genshin.hoyoverse.com/en/gift).\n2. Login to your account.\n3. Press F12 to open Inspect Mode (ie. Developer Tools).\n4. Go to `Application`, `Cookies`, `https://genshin.hoyoverse.com`.\n5. Copy `ltuid` and `cookie_token`.\n6. Paste these into their respective boxes after pressing the button below.",inline = False)
        embed.set_footer(text = "When you are ready, click the button below to input cookie information. If the interaction does not load, exit this and re-enter.")
        view = StartInformation("mihoyocookies",self.key)
        await interaction.response.send_message(embed = embed,view = view,ephemeral = True)
        await view.wait()
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)

    @discord.ui.button(label = "Set Privacy",style = discord.ButtonStyle.gray)
    async def setgeneralprivacy(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(description = "Input either `public` or `private` to change your profile privacy! This determines if people can view your statistics.")
        embed.set_footer(text = "Type \"cancel\" to cancel your input.")
        await interaction.response.edit_message(embed = embed,view = None)

        def check(message: discord.Message):
            return message.author.id == self.ctx.author.id and message.channel.id == self.ctx.channel.id
        while True:
            try:
                msg = await interaction.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                self.value = False
                self.stop()
            if msg.content.lower() == "cancel":
                await msg.delete()
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            if msg.content.lower() == "private" or msg.content.lower() == "public":
                await msg.delete()
                break
            else:
                embed = discord.Embed(description = "Input either `public` or `private` to change your profile privacy! This determines if people can view your statistics.\n\n⚠ You choice can only be `public` or `private`!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        ref.child(str(interaction.user.id)).child("gprivacy").set(msg.content.lower())
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)

    @discord.ui.button(label = "Set Wish Privacy",style = discord.ButtonStyle.gray)
    async def setwishprivacy(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(description = "Input either `public` or `private` to change your wish privacy! This determines if people can view your wish history.")
        embed.set_footer(text = "Type \"cancel\" to cancel your input.")
        await interaction.response.edit_message(embed = embed,view = None)

        def check(message: discord.Message):
            return message.author.id == self.ctx.author.id and message.channel.id == self.ctx.channel.id
        while True:
            try:
                msg = await interaction.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                self.value = False
                self.stop()
            if msg.content.lower() == "cancel":
                await msg.delete()
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            if msg.content.lower() == "private" or msg.content.lower() == "public":
                await msg.delete()
                break
            else:
                embed = discord.Embed(description = "Input either `public` or `private` to change your wish privacy! This determines if people can view your wish history.\n\n⚠ You choice can only be `public` or `private`!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        ref.child(str(interaction.user.id)).child("wprivacy").set(msg.content.lower())
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)

    @discord.ui.button(label = "Set Transaction Privacy",style = discord.ButtonStyle.gray)
    async def settransactionprivacy(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(description = "Input either `public` or `private` to change your transaction privacy! This determines if people can view your transaction like primogems, genesis crystals, resin, etc.")
        embed.set_footer(text = "Type \"cancel\" to cancel your input.")
        await interaction.response.edit_message(embed = embed,view = None)

        def check(message: discord.Message):
            return message.author.id == self.ctx.author.id and message.channel.id == self.ctx.channel.id
        while True:
            try:
                msg = await interaction.client.wait_for("message",timeout = 60.0,check=check)
            except asyncio.TimeoutError:
                self.value = False
                self.stop()
            if msg.content.lower() == "cancel":
                await msg.delete()
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            if msg.content.lower() == "private" or msg.content.lower() == "public":
                await msg.delete()
                break
            else:
                embed = discord.Embed(description = "Input either `public` or `private` to change your transaction privacy! This determines if people can view your transaction like primogems, genesis crystals, resin, etc.\n\n⚠ You choice can only be `public` or `private`!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        ref.child(str(interaction.user.id)).child("tprivacy").set(msg.content.lower())
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Settings Information",style = discord.ButtonStyle.gray,row = 1)
    async def infomenu(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(title = "Hoyoverse User Settings Information",color = discord.Color.random())
        embed.add_field(name = "Cookies",value = "Sets up authentication cookies needed for many functions in the Hoyoverse category. This is required for functions like daily checkin, real-time notes, or abyss stats. More information can be found by clicking the corresponding setting button below.",inline = False)
        embed.add_field(name = "Authkey",value = "Sets up the authentication key needed to access wish history and transaction history. Must be refreshed every 24 hours in order to still function. More information can be found by clicking the corresponding setting button below.",inline = False)
        embed.add_field(name = "Privacy",value = "Sets whether or not other users can see your statistics like real-time notes, abyss, teapot, and more. Does not include wishes or transactions.",inline = False)
        embed.add_field(name = "Wish Privacy",value = "Sets whether or not other users can see your wish history.",inline = False)
        embed.add_field(name = "Transaction Privacy",value = "Sets whether or not other users can see your transaction history. Includes primogems, genesis crystals, resin, artifact, and weapon history.")
        embed.set_footer(text = "To set these up, click the buttons on the original message!")
        await interaction.response.send_message(embed = embed,ephemeral = True)

    @discord.ui.button(label = "End interaction",style = discord.ButtonStyle.gray,row = 1)
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()

class StartInformation(discord.ui.View):
    def __init__(self,type,key):
        super().__init__(timeout = 30)
        self.type = type
        self.key = key
    
    @discord.ui.button(label = "Enter Infomation",style = discord.ButtonStyle.gray)
    async def setgeneralprivacy(self,interaction:discord.Interaction,button:discord.ui.Button):
        if self.type == "cookie":
            await interaction.response.send_modal(CollectCookies(self.key))
        elif self.type == "authkey":
            await interaction.response.send_modal(CollectAuthKey())
        else:
            await interaction.response.send_modal(CollectMihoyoCookies(self.key))
        self.stop()

class CollectCookies(discord.ui.Modal,title = "Cookie Request"):
    def __init__(self,key):
        super().__init__()
        self.key = key

    ltuid = discord.ui.TextInput(label = "ltuid",placeholder="An integer number from cookies...",max_length = 15)
    ltoken = discord.ui.TextInput(label = "ltoken",placeholder = "A string containing letters and numbers...",max_length = 100)

    async def on_submit(self, interaction: discord.Interaction):
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        uidutf8 = self.ltuid.value.encode('utf8')
        encodeduid = rsa.encrypt(uidutf8,self.key)
        tokenutf8 = self.ltoken.value.encode('utf8')
        encodedtoken = rsa.encrypt(tokenutf8,self.key)
        ref.child(str(interaction.user.id)).child("ltuid").set(binascii.hexlify(encodeduid).decode('utf8'))
        ref.child(str(interaction.user.id)).child("ltoken").set(binascii.hexlify(encodedtoken).decode('utf8'))
        if not ref.child(str(interaction.user.id)).child("gprivacy").get():
            ref.child(str(interaction.user.id)).child("gprivacy").set("private")
        embed = discord.Embed(title = "Authentication Data Set!",description = "I have setup your cookies in the bot. You can now use any genshin command pertaining to yourself!")
        await interaction.response.send_message(embed = embed,ephemeral = True)

class CollectMihoyoCookies(discord.ui.Modal,title = "Mihoyo Cookie Request"):
    def __init__(self,key):
        super().__init__()
        self.key = key

    ltuid = discord.ui.TextInput(label = "ltuid",placeholder="An integer number from cookies...",max_length = 15)
    cookie_token = discord.ui.TextInput(label = "cookie_token",placeholder = "A string containing letters and numbers...",max_length = 100)

    async def on_submit(self, interaction: discord.Interaction):
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        uidutf8 = self.ltuid.value.encode('utf8')
        encodeduid = rsa.encrypt(uidutf8,self.key)
        tokenutf8 = self.cookie_token.value.encode('utf8')
        encodedtoken = rsa.encrypt(tokenutf8,self.key)
        ref.child(str(interaction.user.id)).child("ltuid").set(binascii.hexlify(encodeduid).decode('utf8'))
        ref.child(str(interaction.user.id)).child("cookie_token").set(binascii.hexlify(encodedtoken).decode('utf8'))
        if not ref.child(str(interaction.user.id)).child("gprivacy").get():
            ref.child(str(interaction.user.id)).child("gprivacy").set("private")
        embed = discord.Embed(title = "Authentication Data Set!",description = "I have setup your cookies in the bot. This allows you to use the redeem code feature!")
        await interaction.response.send_message(embed = embed,ephemeral = True)

class CollectAuthKey(discord.ui.Modal,title = "Authkey Request"):
    def __init__(self):
        super().__init__()

    authkey = discord.ui.TextInput(label = "Authkey",placeholder="A long link...",max_length = 3000)
    
    async def on_submit(self, interaction: discord.Interaction):
        ref = db.reference("/",app = firebase_admin._apps['hoyoverse'])
        ref.child(str(interaction.user.id)).child("authkey").set(genshin.utility.extract_authkey(self.authkey.value))
        if not ref.child(str(interaction.user.id)).child("wprivacy").get():
            ref.child(str(interaction.user.id)).child("wprivacy").set("private")
        if not ref.child(str(interaction.user.id)).child("tprivacy").get():
            ref.child(str(interaction.user.id)).child("tprivacy").set("private")
        embed = discord.Embed(title = "Authentication Data Set!",description = "I have setup your authkey in the bot. You can now use any genshin command pertaining to wish history and transaction history!")
        await interaction.response.send_message(embed = embed,ephemeral = True)

class StatsSelect(discord.ui.Select):
    def __init__(self,data,uid):
        options = [
            discord.SelectOption(label = "Overview",description = "Stats such as achievements, chests opened, etc.",value = 0),
            discord.SelectOption(label = "Exploration",description = "Stats such as exploration percent, reputation, etc.",value = 1),
            discord.SelectOption(label = "Teapot",description = "Stats such as level, visitors, etc.",value = 2),
        ]
        self.data = data
        self.uid = uid
        super().__init__(placeholder='Statistics Category', min_values=0, max_values=1, options=options,row = 0)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "0":
            embed = discord.Embed(title = "Overview Statistics",description = f"UID: {self.uid}",color = discord.Color.random())
            embed.add_field(name = "Achievements",value = self.data.stats.achievements)
            embed.add_field(name = "Days Active",value = self.data.stats.days_active)
            embed.add_field(name = "Characters",value = self.data.stats.characters)
            embed.add_field(name = "Spiral Abyss",value = self.data.stats.spiral_abyss)
            embed.add_field(name = "Anemoculi",value = self.data.stats.anemoculi)
            embed.add_field(name = "Geoculi",value = self.data.stats.geoculi)
            embed.add_field(name = "Electroculi",value = self.data.stats.electroculi)
            embed.add_field(name = "Common Chests",value = self.data.stats.common_chests)
            embed.add_field(name = "Exquisite Chests",value = self.data.stats.exquisite_chests)
            embed.add_field(name = "Precious Chests",value = self.data.stats.precious_chests)
            embed.add_field(name = "Luxurious Chests",value = self.data.stats.luxurious_chests)
            embed.add_field(name = "Remarkable Chests",value = self.data.stats.remarkable_chests)
            embed.add_field(name = "Unlocked Waypoints",value = self.data.stats.unlocked_waypoints)
            embed.add_field(name = "Unlocked Domains",value = self.data.stats.unlocked_domains)
        elif self.values[0] == "1":
            embed = discord.Embed(title = "Exploration Statistics",description = f"UID: {self.uid}",color = discord.Color.random())
            for exploration in self.data.explorations:
                build = f"Exploration: {exploration.raw_explored/10}%\n"
                if len(exploration.offerings) > 0:
                    build += "\n".join([x.name + ": " + str(x.level) for x in exploration.offerings])
                embed.add_field(name = exploration.name,value = build,inline = False)
        elif self.values[0] == "2":
            embed = discord.Embed(title = "Teapot Statistics",description = f"UID: {self.uid}",color = discord.Color.random())
            embed.add_field(name = "Trust Rank",value = self.data.teapot.level)
            embed.add_field(name = "Confort Level",value = f"{self.data.teapot.comfort_name}: {self.data.teapot.comfort}")
            embed.add_field(name = "Furnishings Obtained",value = self.data.teapot.items)
        await interaction.response.edit_message(embed = embed)

class StatsView(discord.ui.View):
    def __init__(self,ctx,data,uid):
        super().__init__(timeout=60)
        self.add_item(StatsSelect(data,uid))
        self.message = None
        self.ctx = ctx
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view = self)

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False

class AbyssSelect(discord.ui.Select):
    def __init__(self,floors,default):
        options = [discord.SelectOption(label = "Overview",description = "Floor wide data",value = -1)]
        self.floors = floors
        self.default = default
        for index,floor in enumerate(floors):
            options.append(discord.SelectOption(label = f"Spiral Abyss {floor.floor}",description = f"{floor.stars}/{floor.max_stars} Stars",value = index))
        super().__init__(placeholder='Abyss Floor', min_values=0, max_values=1, options=options,row = 0)
    
    async def callback(self, interaction: discord.Interaction):
        if int(self.values[0]) == -1:
            await interaction.response.edit_message(embed = self.default)
            return
        floor = self.floors[int(self.values[0])]
        embed = discord.Embed(title = f"Spiral Abyss Floor {floor.floor}",description = f"⭐ {floor.stars}/{floor.max_stars}",color = discord.Color.random())
        for chamber in floor.chambers:
            details = ""
            for battle in chamber.battles:
                strformat = battle.timestamp.strftime("%m/%d/%y")
                details += f"**Half {battle.half}**\nCompleted on: {strformat}\n**Characters**\n{', '.join([x.name for x in battle.characters])}\n"
            embed.add_field(name = f"Chamber {chamber.chamber}: ⭐ {chamber.stars}/{chamber.max_stars}",value = details,inline = False)
        await interaction.response.edit_message(embed = embed)

class SpiralAbyssView(discord.ui.View):
    def __init__(self,ctx,floors,default):
        super().__init__(timeout=60)
        self.add_item(AbyssSelect(floors,default))
        self.message = None
        self.ctx = ctx
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view = self)

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False

class DiaryLogMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.message = None
        self.ctx = None
        self.delete_message_after = False

    async def start(self, message,ctx):
        await self._source._prepare_once()
        self.message = message
        self.ctx = ctx
        self.message = await self.send_initial_message(self.message)

    async def _get_kwargs_from_page(self, page):
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value
    
    async def send_initial_message(self, message):
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await message.edit(**kwargs)
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False

    @ui.button(emoji='<:doubleleft:930948763885899797>', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_page(0)

    @ui.button(emoji='<:arrowleft:930948708458172427>', style=discord.ButtonStyle.blurple)
    async def before_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page - 1)

    @ui.button(emoji='<:arrowright:930948684718432256>', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page + 1)

    @ui.button(emoji='<:doubleright:930948740557193256>', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_page(self._source.get_max_pages() - 1)
    
    @ui.button(label='End Interaction', style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction, button):
        await interaction.response.defer()
        self.stop()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

class DiaryLogPageSource(menus.ListPageSource):
    def __init__(self, data,type):
        self.type = type
        super().__init__(data, per_page=10)
    def format_leaderboard_entry(self, no, action):
        return f"**{no}.** {action.action} - {action.amount} {self.type} (<t:{int(action.time.replace().timestamp())}:D>)"
    async def format_page(self, menu, users):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_leaderboard_entry, enumerate(users, start=starting_number))
        page_content = "\n".join(iterator)
        embed = discord.Embed(
            title=f"{self.type} Recent Gains [{page + 1}/{max_page}]", 
            description=page_content,
            color= discord.Color.random()
        )
        embed.set_footer(text=f"Use the buttons below to navigate pages!") 
        return embed

class CharacterSelect(discord.ui.Select):
    def __init__(self,characters):
        self.colors = {"Electro":discord.Color.from_rgb(162,83,198),"Hydro":discord.Color.from_rgb(74,188,233),"Pyro":discord.Color.from_rgb(232,117,54),"Cryo":discord.Color.from_rgb(154,207,220),"Geo":discord.Color.from_rgb(242,176,48),"Anemo":discord.Color.from_rgb(112,188,163),"Dendro":discord.Color.from_rgb(160,194,57)}
        options = []
        self.characters = characters
        for index,character in enumerate(characters):
            options.append(discord.SelectOption(label = character.name,description = f"{character.rarity} ⭐ | Level {character.level}",value = index))
        super().__init__(placeholder='Character Selection', min_values=0, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        character = self.characters[int(self.values[0])]
        embed = discord.Embed(title = character.name,description = f"⭐{character.rarity} | {character.element} | Level {character.level} | | <:nofriends:990260672250122350> {character.friendship} | Constellation {character.constellation}",color = self.colors[character.element])
        embed.add_field(name = f"Weapon ({character.weapon.type}): {character.weapon.name} | ⭐ {character.weapon.rarity}",value = f"Level: {character.weapon.level}\nRefinement: {character.weapon.refinement}\n{character.weapon.description}",inline = False)
        if len(character.artifacts) > 0:
            embed.add_field(name = f"Artifacts",value = "\n".join([x.pos_name + ": " + x.name + " (" + x.set.name + ")" for x in character.artifacts]),inline = False)
            sets = []
            for artifact in character.artifacts:
                if artifact.set in sets:
                    continue
                sets.append(artifact.set)
                if artifact.set.effects[0].enabled:
                    embed.add_field(name = f"Artifact Set: {artifact.set.name}",value = "\n".join(["**" + str(x.pieces) + " Piece Effect**" + "\n" + x.effect for x in artifact.set.effects if x.enabled]))
        else:
            embed.add_field(name = "Artifacts",value = "No artifacts applied.")
        embed.set_thumbnail(url = character.icon)
        await interaction.response.edit_message(embed = embed)

class CharacterView(discord.ui.View):
    def __init__(self,ctx,data):
        super().__init__(timeout=60)
        for i in range(0,len(data),25):
            self.add_item(CharacterSelect(data[i:min(i+25,len(data))]))
        self.message = None
        self.ctx = ctx
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view = self)

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False

class WishSelect(discord.ui.Select):
    def __init__(self,wishes,member,default):
        options = [
            discord.SelectOption(emoji = "🌟", label = "Wish Overview", value = "o"),
            discord.SelectOption(emoji = "<:intertwined:990336430934999040>", label = "Limited Character Banner", value = "c"),
            discord.SelectOption(emoji = "<:intertwined:990336430934999040>", label = "Limited Weapon Banner",value = "w"),
            discord.SelectOption(emoji = "<:acquaint:990336486723432490>", label = "Standard Banner",value = "s"),
            discord.SelectOption(emoji = "<:acquaint:990336486723432490>", label = "Novice Banner",value = "n")
        ]
        self.wishes = wishes
        self.default = default
        self.member = member
        self.names = {"c":"Limited Character Banner","w":"Limited Weapon Banner","s":"Standard Banner","n":"Novice Banner"}
        super().__init__(placeholder='Banner Selection', min_values=0, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "o":
            return await interaction.response.edit_message(embed = self.default)
        stats = {"5":[],"4":[],"3":[]}
        banner = self.wishes[self.values[0]]
        fivepity = 0
        fourpity = 0
        for wish in banner[::-1]:
            if wish.rarity == 5:
                stats["5"].append(wish)
                fivepity = 0
                fourpity += 1
            elif wish.rarity == 4:
                stats["4"].append(wish)
                fivepity += 1
                fourpity = 0
            else:
                stats["3"].append(wish)
                fivepity += 1
                fourpity += 1
        embed = discord.Embed(title = f"{self.names[self.values[0]]} Wishes for {self.member}",description = f"Looking at the past `{len(banner)}` wishes",color = discord.Color.random())
        embed.set_footer(text = "Use the dropdown below to sort by banner!")
        if len(banner) < 1:
            embed.add_field(name = "No wishes found!",value = "I did not find any wishes on this banner for this user!")
            await interaction.response.edit_message(embed = embed)
        embed.add_field(name = "Total Statistics",value = f"Total Pulls: {len(banner)} <:intertwined:990336430934999040>\nPrimogem Equivalent: {len(banner)*160} <:primogem:990335900280041472>\nAverage Pity: {int((len(banner)-fivepity)/len(stats['5'])) if len(stats['5']) > 0 else 'None'} <:acquaint:990336486723432490>",inline = False)
        embed.add_field(name = "By Rarity",value = f'5 🌟 Pulls: {len(stats["5"])}\n4 🌟 Pulls: {len(stats["4"])}\n3 ⭐ Pulls: {len(stats["3"])}')
        embed.add_field(name = "Recent Statistics",value = f'Last 5 🌟: {stats["5"][-1].name if len(stats["5"]) > 0 else "None"}\nLast 4 🌟: {stats["4"][-1].name if len(stats["4"]) > 0 else "None"}\nLast 3 ⭐: {stats["3"][-1].name if len(stats["3"]) > 0 else "None"}')
        if self.values[0] == "c" or self.values[0] == "s":
            embed.add_field(name = "Current Pity",value = f"5 🌟 Pity: {fivepity} ({90-fivepity} to guaranteed)\n4 🌟 Pity: {fourpity} ({10-fourpity} to guaranteed)",inline = False)
        elif self.values[0] == "w":
            embed.add_field(name = "Current Pity",value = f"5 🌟 Pity: {fivepity} ({80-fivepity} to guaranteed)\n4 🌟 Pity: {fourpity} ({10-fourpity} to guaranteed)",inline = False)
        await interaction.response.edit_message(embed = embed)

class WishView(discord.ui.View):
    def __init__(self,ctx,data,member,default):
        super().__init__(timeout=60)
        self.add_item(WishSelect(data,member,default))
        self.message = None
        self.ctx = ctx
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view = self)

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False

class TransactionLogMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = False

    async def start(self, message,ctx):
        await self._source._prepare_once()
        self.message = message
        self.ctx = ctx
        self.message = await self.send_initial_message(self.message)

    async def _get_kwargs_from_page(self, page):
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value
    
    async def send_initial_message(self,message):
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await message.edit(**kwargs)
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False

    @ui.button(emoji='<:doubleleft:930948763885899797>', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_page(0)

    @ui.button(emoji='<:arrowleft:930948708458172427>', style=discord.ButtonStyle.blurple)
    async def before_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page - 1)

    @ui.button(emoji='<:arrowright:930948684718432256>', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page + 1)

    @ui.button(emoji='<:doubleright:930948740557193256>', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction, button):
        await interaction.response.defer()
        await self.show_page(self._source.get_max_pages() - 1)
    
    @ui.button(label='End Interaction', style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction, button):
        await interaction.response.defer()
        self.stop()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

class TransactionLogPageSource(menus.ListPageSource):
    def __init__(self, data,type):
        self.type = type
        super().__init__(data, per_page=10)
    def format_transaction_entry(self, no, action):
        return f"**{no}.** {action.reason_name}: {action.amount} {self.type} (<t:{int(action.time.replace().timestamp())}:D>)"
    async def format_page(self, menu, items):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_transaction_entry, enumerate(items, start=starting_number))
        page_content = "\n".join(iterator)
        embed = discord.Embed(
            title=f"{self.type} Recent Gains [{page + 1}/{max_page}]", 
            description=page_content,
            color= discord.Color.random()
        )
        embed.set_footer(text=f"Use the buttons below to navigate pages!") 
        return embed

class EventSelect(discord.ui.Select):
    def __init__(self,events):
        options = [
            discord.SelectOption(label = "Summertime Odyssey",description = "v2.8 Golden Apple Archipelago",value = "s")
        ]
        self.events = events
        super().__init__(placeholder='Event Selection', min_values=0, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "s":
            embed = discord.Embed(title = "Summertime Odyssey", description = "v2.8 Golden Apple Archipelago",color = discord.Color.random())
            embed.add_field(name = "Teleport Waypoints Unlocked",value = f"{self.events.summertime_odyssey.waypoints}/10")
            embed.add_field(name = "Waverider Waypoints Unlocked",value = f"{self.events.summertime_odyssey.waverider_waypoints}/13")
            embed.add_field(name = "Chests Opened",value = f"{self.events.summertime_odyssey.treasure_chests}")
            res = ""
            for count,data in enumerate(self.events.summertime_odyssey.surfpiercer):
                if data.finished:
                    res += f"#{count} Best Record: {data.time//60} min {data.time%60} seconds\n"
                else:
                    res += f"Surfpiercer challenge #{count} not completed!\n"
            embed.add_field(name = "Surfpiercer",value = res,inline = False)
            res = ""
            for memory in self.events.summertime_odyssey.memories:
                if memory.finished:
                    res += f"{memory.name} finished on <t:{int(memory.finish_time.replace(tzinfo=datetime.timezone.utc).timestamp())}:f>\n"
                else:
                    res += f"{memory.name} not yet completed!\n"
            embed.add_field(name = "Memories",value = res, inline = False)
            for realm in self.events.summertime_odyssey.realm_exploration:
                if realm.finished:
                    embed.add_field(name = f"Phantom Realm: {realm.name}",value = f"Initial Clear On: <t:{int(realm.finish_time.replace(tzinfo=datetime.timezone.utc).timestamp())}:f>\nCompleted Successfully: {realm.success} times\nSpecial Skills Used: {realm.skills_used} times")
            await interaction.response.edit_message(embed = embed)


class EventView(discord.ui.View):
    def __init__(self,ctx,data):
        super().__init__(timeout=60)
        self.add_item(EventSelect(data))
        self.message = None
        self.ctx = ctx
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view = self)

    async def interaction_check(self, interaction):
        if interaction.user == self.ctx.author:
            return True
        interaction.response.send_message(embed = discord.Embed(description = "This menu is not for you!",color = discord.Color.red()))
        return False

async def setup(client):
    await client.add_cog(Hoyoverse(client))

