import discord
from discord.ext import commands

import firebase_admin
from firebase_admin import db
import asyncio
import datetime

class GiveawayUtil(commands.Cog):
    '''
        Log giveaway donations for members in the server! Many of these commands will require a giveaway manager role.
        \n**Setup for this Category**
        Giveaway Manager: `o!settings set giveawaymanager <role>` 
    '''
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Giveaways Cog Loaded.')

    def giveaway_role_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            giveaway = ref.child(str(ctx.message.guild.id)).child('giveaway').get()
            role_ob = ctx.message.guild.get_role(giveaway)
            if role_ob in ctx.message.author.roles:
                return True
            else:
                return False
        return commands.check(predicate)

    async def log_giveaway(self,ctx,manager):
        ref = db.reference("/",app = firebase_admin._apps['glogging'])
        amount = ref.child(str(ctx.message.guild.id)).child(str(manager)).get()

        if amount:
            amount += 1
        else:
            amount = 1

        ref.child(str(ctx.message.guild.id)).child(str(manager)).set(amount)

    async def get_leaderboard(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['glogging'])
        log = ref.child(str(ctx.message.guild.id)).get()

        if log:
            return sorted(log, key=log.get, reverse=True) , log
        else:
            return {},{}

    async def get_gamount(self,ctx,member):
        ref = db.reference("/",app = firebase_admin._apps['glogging'])
        log = ref.child(str(ctx.message.guild.id)).child(str(member)).get()

        if log:
            return log
        else:
            return 0

    async def post_log(self,ctx,channel,member,amount):
        emb = discord.Embed(title=f"Giveaway Recorded for {ctx.message.author.name}",description = f"{ctx.message.author.mention}",
                                color=discord.Color.green())

        emb.add_field(name = "Giveaway information:",value = f"[Link to Donation]({ctx.message.jump_url})\nDonated By: <@{member}> ({member})\nDonation Amount: {amount}")

        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'Oasis Bot Giveaway Logging',icon_url = ctx.message.channel.guild.icon_url)

        await channel.send(embed = emb)
   

    async def add_giveaway_amount(self,ctx,user,amount,category = None):
        ref = db.reference("/",app = firebase_admin._apps['giveaways'])
        ref2 = db.reference("/",app = firebase_admin._apps['settings'])
        person = ref.child(str(ctx.message.guild.id)).child(str(user)).get()

        if not person:
            person = {'total':None}
        if category:
            categories = ref.child(str(ctx.message.guild.id)).child('categories').get()
            if not categories:
                return await ctx.reply("You do not have any special categories set up!")
            if not category in categories:
                return await ctx.reply("I can't seem to find that custom event, please try again.")
            else:
                try:
                    person[category] += int(amount)
                except:
                    person[category] = int(amount)

        
        if person['total']:
            person['total'] += int(amount)
        else:
            person['total'] = int(amount)

        await self.update_roles(ctx,user,person['total'])
        ref.child(str(ctx.message.guild.id)).child(str(user)).set(person)

        await ctx.message.add_reaction('<a:PB_greentick:865758752379240448>')

        await self.log_giveaway(ctx,ctx.message.author.id)

        logchannel = ref2.child(str(ctx.message.guild.id)).child('glogging').get()
        if logchannel:
            channel = ctx.guild.get_channel(logchannel)
            if channel:
                await self.post_log(ctx,channel,user,amount)

    async def view_categories(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['giveaways'])
        categories = ref.child(str(ctx.message.guild.id)).child('categories').get()

        if categories:
            store = ", ".join(categories)
        else:
            store = "There are no categories set up for this server!"

        emb = discord.Embed(title=f"Giveaway Categories for {ctx.guild.name}",description = f"{store}",
                                color=discord.Color.green())
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = emb)

    async def remove_giveaway_amount(self,ctx,user,amount,category = None):
        ref = db.reference("/",app = firebase_admin._apps['giveaways'])
        person = ref.child(str(ctx.message.guild.id)).child(str(user)).get()

        if category:
            categories = ref.child(str(ctx.message.guild.id)).child('categories').get()
            if not categories:
                return await ctx.reply("You do not have any special categories set up!")
            if not category in categories:
                return await ctx.reply("I can't seem to find that custom event, please try again.")
            else:
                if category in person:
                    if person[category]:
                        person[category] -= int(amount)
                else:
                    return await ctx.reply("Doesn't seem this person even has anything donated for this event.")

        if person['total']:
            person['total'] -= int(amount)
        else:
            return await ctx.reply("Doesn't seem like this person has even donated at all. What are you trying to do?")

        await self.update_roles(ctx,user,person['total'])
        ref.child(str(ctx.message.guild.id)).child(str(user)).set(person)
        await ctx.message.add_reaction('<a:PB_greentick:865758752379240448>')

    async def add_category(self,ctx,category):
        ref = db.reference("/",app = firebase_admin._apps['giveaways'])
        categories = ref.child(str(ctx.message.guild.id)).child('categories').get()

        if categories:
            if category in categories:
                return await ctx.reply("Seems like this category already exsists!")
            else:
                categories.append(category)
                ref.child(str(ctx.message.guild.id)).child('categories').set(categories)
                return await ctx.reply(f"<a:PB_greentick:865758752379240448> Successfully added {category} as a new giveaway category.")
        else:
            categories = [category]
            ref.child(str(ctx.message.guild.id)).child('categories').set(categories)
            return await ctx.reply(f"<a:PB_greentick:865758752379240448> Successfully added {category} as a new giveaway category.")

    async def update_roles(self,ctx,member,amount):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        groles = ref.child(str(ctx.message.guild.id)).child('groles').get()
        rolestoadd = []
        rolestoremove = []
        guild = ctx.guild
        member = guild.get_member(int(member))
        
        if groles:
            for role in groles:
                if int(amount) >= int(role):
                    role_ob = ctx.message.guild.get_role(groles[role])
                    rolestoadd.append(role_ob)
                else:
                    role_ob = ctx.message.guild.get_role(groles[role])
                    rolestoremove.append(role_ob)


            for role in rolestoremove:
                await member.remove_roles((role))
            
            for role in rolestoadd:
                await member.add_roles((role))

    async def remove_category(self,ctx,category):
        ref = db.reference("/",app = firebase_admin._apps['giveaways'])
        categories = ref.child(str(ctx.message.guild.id)).child('categories').get()

        if categories:
            if category in categories:
                def check(message: discord.Message):
                    if message.author.bot:
                        return False
                    if message.content.lower() != "n":
                        return True
                    elif message.content.lower() != "y":
                        return True
                    else:
                        return False
                message = await ctx.reply(f"**Warning!!**\nYou are now deleting the giveaway category `{category}`. This will delete all giveaway information for this category, but the total donations will still be kept. All information is NOT recoverable.\nAre you sure you want to do this? (y/n):")
                
                try:
                    msg = await self.client.wait_for("message",timeout = 30.0,check=check)
                except asyncio.TimeoutError:
                    await message.channel.send("You took too long to answer, try to respond next time.")
                    return

                if msg.content.lower() == 'n':
                    await ctx.reply("Cancelling....")
                else:
                    await ctx.reply(f"Deleting `{category}`, this may take a while.")

                    todelete = ref.child(str(ctx.message.guild.id)).get()

                    for person in todelete:
                        if person == 'categories':
                            continue
                        try:
                            temp = todelete[person]
                            temp.pop(category)
                            todelete[person] = temp
                        except:
                            pass
                    
                    todelete['categories'].remove(category)
                    ref.child(str(ctx.message.guild.id)).set(todelete)
                    await ctx.reply("Category Deleted!")
            else:
                return await ctx.reply("Doesn't seem like that category exsists.")
        else:
            return await ctx.reply("Doesn't seem like there are any categories set up. What are your trying to remove anyways?")

    async def view_profile(self,ctx,user):
        ref = db.reference("/",app = firebase_admin._apps['giveaways'])
        profile = ref.child(str(ctx.message.guild.id)).child(str(user)).get()

        if not profile:
            return await ctx.reply("That person has not donated yet!")
        else:
            emb = discord.Embed(title="Donation Profile",
                            description=f"Donation profile for <@{user}>",
                            color=discord.Color.blue())

            for category in profile:
                emb.add_field(name = category,value = f'> {profile[category]:,}',inline = False)
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
            await ctx.reply(embed = emb)

    async def get_leaderboard(self,ctx,category = None):
        ref = db.reference("/",app = firebase_admin._apps['giveaways'])
        guild_info = ref.child(str(ctx.message.guild.id)).get()

        if not guild_info:
            return await ctx.reply("Seems like this server does not have any donations.")

        if category:
            categories = ref.child(str(ctx.message.guild.id)).child('categories').get()
            if not categories:
                return await ctx.reply("You do not have any special categories set up!")
            if not category in categories:
                return await ctx.reply("I can't seem to find that custom event, please try again.")
        
        if not category:
            category = 'total'

        category = category.lower()

        def check(a,category):
            if a == "categories":
                return 0
            if category in guild_info[a]:
                return guild_info[a][category]
            else:
                return 0

        sortedinfo = sorted(guild_info,key = lambda a: check(a,category),reverse = True)

        build = ""
        for person in sortedinfo:
            try:
                formatted = '{:,}'.format(guild_info[person][category])
                build += f'<@{person}>: `{formatted}`\n'
            except:
                pass

        emb = discord.Embed(title=f"{category.capitalize()} Donation Leaderboard",
                            description=f"{build}",
                            color=discord.Color.blue())

        emb.timestamp = datetime.datetime.utcnow()
        emb.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)

        await ctx.reply(embed = emb)

    @commands.group(description = "Manage all donations, or view your own donation.",help = "dono [option]")
    async def dono(self,ctx):
        if ctx.invoked_subcommand is None:
            await self.view_profile(ctx,ctx.message.author.id)

    @commands.group(description = "Manage donation categories, or view the current categories for the server.",help = "category [option]")
    async def category(self,ctx):
        if ctx.invoked_subcommand is None:
            await self.view_categories(ctx)

    @category.command(name = "add",description = "Add a donation category.",help = "category add <category>")
    @commands.has_permissions(manage_guild= True)
    async def addcat(self,ctx,category):
        await self.add_category(ctx,category)

    @category.command(name = "remove",description = "Remove a donation category.",help = "category remove <category>")
    @commands.has_permissions(manage_guild= True)
    async def removecat(self,ctx,category):
        await self.remove_category(ctx,category)

    @dono.command(description = "Add the donation amount to someone.",help = "dono add <member> <amount> [category]")
    @giveaway_role_check()
    async def add(self,ctx,member,amount,category = None):
        if str(member).isnumeric():
            guild = ctx.guild
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)

        try:
            amount = int(float(amount))
        except:
            return await ctx.reply("That does not look like a valid donation amount.")

        await self.add_giveaway_amount(ctx,member.id,amount,category)

    @dono.command(aliases = ['leaderboard'],description = "Check the donations leaderboard for the server, or for a category.",help = "dono lb [category]")
    async def lb(self,ctx,category = None):
        await self.get_leaderboard(ctx,category)

    @dono.command(description = "Remove the donation amount to someone.",help = "dono remmove <member> <amount> [category]")
    @giveaway_role_check()
    async def remove(self,ctx,member,amount,category = None):
        if str(member).isnumeric():
            guild = ctx.guild
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)

        try:
            amount = int(float(amount))
        except:
            return await ctx.reply("That does not look like a valid donation amount.")

        await self.remove_giveaway_amount(ctx,member.id,amount,category)

    @dono.command(description = "View the donation amount for someone.",help = "dono view <member>")
    async def view(self,ctx,member):
        if str(member).isnumeric():
            guild = ctx.guild
            member = guild.get_member(int(member))
        else:
            member = await commands.converter.MemberConverter().convert(ctx,member)

        await self.view_profile(ctx,member.id)

    @commands.command(description = "Check giveaway manager leaderboard.",help = "gleaderboard")
    @giveaway_role_check()
    async def gleaderboard(self,ctx):
        users,log = await self.get_leaderboard(ctx)

        embed=discord.Embed(title="Giveaways Leaderboard", color=discord.Color.blue())
        
        count = 1
        for user in users:
            amount = log[user]
            embed.add_field(name=f"{count}",value=f'<@{user}> {amount} giveaways',inline=False)
            count += 1

            if count >= 10:
                break
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)

    @commands.command(description = "Check giveaway manager log amount.",help = "gamount")
    @giveaway_role_check()
    async def gamount(self,ctx,member = None):
        if member:
            if str(member).isnumeric():
                guild = ctx.guild
                member = guild.get_member(int(member))
            else:
                member = await commands.converter.MemberConverter().convert(ctx,member)
        else:
            member = ctx.message.author

        amount = await self.get_gamount(ctx,str(member.id))

        embed=discord.Embed(title="Giveways Hosted",description = f'{member.mention}: `{amount}` giveaways', color=discord.Color.blue())
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon_url)
        await ctx.reply(embed = embed)


def setup(client):
    client.add_cog(GiveawayUtil(client))

