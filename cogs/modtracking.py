import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button
import firebase_admin
from firebase_admin import db
import datetime
import math
import asyncio

if not 'modtracking' in firebase_admin._apps:
    cred_obj = firebase_admin.credentials.Certificate('modtracking-dc79b-firebase-adminsdk-dhnil-6e2c14fbb0.json')
    default_app = firebase_admin.initialize_app(cred_obj , {
        'databaseURL':'https://modtracking-dc79b-default-rtdb.firebaseio.com/'
        },name="modtracking")

class ModTracking(commands.Cog):
    """
        Tracking mod actions, are your mods slacking? This will allow mods to log their actions so you can view them. Includes a cool leaderboard to see how you stack up against the other mods.
        \n**Setup for this Category**
        Mod Tracking Role: `o!settings add modtrack <role>` 
    """
    def __init__(self,client):
        self.client = client
    
    def modtrack_role_check():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            modroles = ref.child(str(ctx.message.guild.id)).child('modtrack').get()

            if modroles == None:
                return False
            for role in modroles:
                role_ob = ctx.message.guild.get_role(role)
                if role_ob in ctx.message.author.roles:
                    return True
            else:
                return False
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Mod Traking Cog Loaded.')

    async def post_log(self,ctx,channel,action):
        emb = discord.Embed(title=f"Mod Action Recorded for {ctx.message.author.name}",description = f"{ctx.message.author.mention}",
                                color=discord.Color.green())

        emb.add_field(name = "Action Recorded:",value = f"[Link to Command]({ctx.message.jump_url})\nAction Details: {action}")

        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text = f'Oasis Bot Mod Logging',icon_url = ctx.message.channel.guild.icon)

        await channel.send(embed = emb)

    async def remove_data(self,ctx,member):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        ref.child(str(ctx.guild.id)).child(str(member)).delete()
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Removed mod tracking data for <@{member}>',color = discord.Color.green())
        await ctx.reply(embed = embed)
        return True

    async def pull_data(self,guild,member):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        modtracking = ref.child(str(guild)).child(str(member)).get()
        return modtracking

    async def set_data(self,ctx,guild,member,action):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        modtracking = ref.child(str(guild)).child(str(member)).get()

        if modtracking == None:
            modtracking = []

        now = datetime.datetime.now()
        formatnow = str(now.month) + "-" + str(now.day) + "-" + str(now.year) + " " + str(now.hour) + ":" + str(now.minute)

        modtracking.append([action,formatnow])

        ref.child(str(guild)).child(str(member)).set(modtracking)

        ref = db.reference("/",app = firebase_admin._apps['settings'])
        logchannel = ref.child(str(ctx.message.guild.id)).child('mlogging').get()
        if logchannel:
            channel = ctx.guild.get_channel(logchannel)
            if channel:
                await self.post_log(ctx,channel,action)

    async def pull_leaderboard(self,guild):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        guildtracking = ref.child(str(guild)).get()

        build = {}
        if not guildtracking:
            return [],build
        for person in guildtracking:
            build[person] = len(guildtracking[person])

        return sorted(build, key=build.get, reverse=True) , build

    async def edit_log(self,ctx,guild,member,index,action):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        modtracking = ref.child(str(guild)).child(str(member)).get()
        index = int(index)

        try:
            edit = modtracking[index-1]
            edit[0] = action
            modtracking[index-1] = edit
        except:
            return await ctx.send("Does not look like that is a valid index.")

        ref.child(str(guild)).child(str(member)).set(modtracking)
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully Edited **{index}** to **{action}**!',color = discord.Color.green())
        await ctx.reply(embed = embed)

    async def remove_log(self,ctx,guild,member,index):
        ref = db.reference("/",app = firebase_admin._apps['modtracking'])
        modtracking = ref.child(str(guild)).child(str(member)).get()
        index = int(index)

        try:
            modtracking.pop(index-1)
        except:
            return await ctx.send("Does not look like that is a valid index.")

        ref.child(str(guild)).child(str(member)).set(modtracking)
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully Removed action **{index}**!',color = discord.Color.green())
        return await ctx.reply(embed = embed)

    @commands.command(description = "Log an action that you have completed.",help = 'logaction <action>')
    @modtrack_role_check()
    async def logaction(self,ctx,*,action):
        await self.set_data(ctx,ctx.guild.id,ctx.message.author.id,action)
        embed = discord.Embed(description = f"<a:PB_greentick:865758752379240448> Successfully logged **{action}**!",color = discord.Color.green())
        await ctx.reply(embed = embed)

    @commands.group(description = "Some shortcuts for `[prefix]logaction`.",help = "log <option>")
    async def log(self,ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(description = "You need to specify a shortcut!\nUse `[prefix]help log` to see what you can log.",color = discord.Color.red())
            await ctx.reply(embed = embed)
    
    @log.command(description = "Log alt blacklist.",help = "log alt <id>")
    async def alt(self,ctx,*,ids):
        await self.set_data(ctx,ctx.guild.id,ctx.message.author.id,f"Blacklisted Alt: {ids}")
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully logged alt blacklist of  **{ids}**!',color = discord.Color.green())
        await ctx.reply(embed = embed)

    @log.command(description = "Log freeloader ban.",help = "log free <id>")
    async def free(self,ctx,*,ids):
        await self.set_data(ctx,ctx.guild.id,ctx.message.author.id,f"Banned for Freeloading: {ids}")
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully logged freeloder ban of  **{ids}**!',color = discord.Color.green())
        await ctx.reply(embed = embed)

    @log.command(description = "Log donation role/managerment.",help = "log dono <id>")
    async def dono(self,ctx,*,ids):
        await self.set_data(ctx,ctx.guild.id,ctx.message.author.id,f"Did donations for: {ids}")
        embed = discord.Embed(description = f'<a:PB_greentick:865758752379240448> Successfully logged donations for  **{ids}**!',color = discord.Color.green())
        await ctx.reply(embed = embed)

    @commands.command(description = "Edit an action that you had, with the index of the action.",help = 'editaction <index> <action>')
    @modtrack_role_check()
    async def editaction(self,ctx,index,*,action):
        await self.edit_log(ctx,str(ctx.guild.id), str(ctx.message.author.id),index, action)

    @commands.command(description =  "Remove one of your logs",help = "removeaction <index>")
    @modtrack_role_check()
    async def removeaction(self,ctx,index):
        await self.remove_log(ctx,str(ctx.guild.id),str(ctx.message.author.id),index)

    @commands.command(description =  "Remove all mod tracking data for a member",help = "removeactiondata <member>")
    @commands.has_permissions(administrator= True)
    async def removeactiondata(self,ctx,member:discord.Member):
        await self.remove_data(ctx,member.id)

    @commands.command(description = "Shows the amount of logs you or another person has.",help = 'actionamount [member]')
    @modtrack_role_check()
    async def actionamount(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        logs = await self.pull_data(ctx.guild.id,member.id)
        embed=discord.Embed(description=f"{member.mention}: `{len(logs)}` actions", color=discord.Color.random())
        await ctx.reply(embed=embed)

    @commands.command(description = "See the details of your or another person's logging.",help = 'actiondetail [member]')
    @modtrack_role_check()
    async def actiondetail(self,ctx,member:discord.Member = None):
        member = member or ctx.author
        index = 1
        logs = (await self.pull_data(ctx.guild.id,member.id))

        if logs == None:
            logs = []

        logs.reverse()

        embed=discord.Embed(title=f"Mod Tracking for {member}",description=f"`{len(logs)}` actions", color=discord.Color.random())

        index = int(index)
        logamount = len(logs)
        if index > 1:
            if (index - 1) * 9 < logamount:
                if int(index) * 9 > logamount:
                    end = logamount 
                else:
                    end = (index)*9
                
                start = (index-1) * 9
        else:
            start = 0
            if logamount > 9:
                end = 9
            else:
                end = logamount 
        for log in range(start,end):
            embed.add_field(name=f'Action {len(logs)-log}',value = f'{logs[log][1]}\n{logs[log][0]}',inline = True)

        embed.set_footer(text=f"Showing page {index} out of {math.ceil(logamount/9)}")

        if index >= math.ceil(logamount/9):
            message = await ctx.reply(
                embed = embed, components = [
                    [
                        Button(label = "Back",disabled = True,style = 1),
                        Button(label = "Forward",disabled = True,style = 1)
                    ]
                ]
                )
        else:
            message = await ctx.reply(embed = embed, components = [
                    [
                        Button(label = "Back",disabled = True,style = 1),
                        Button(label = "Forward",style = 1)
                    ]
                ]
                )

        def check(i):
            if i.message.id == message.id:
                if (i.component.label.startswith("Forward") or i.component.label.startswith("Back")):
                    return True
                else:
                    return False
            else:
                return False
            
        while True:
            try:
                interaction = await self.client.wait_for("button_click", timeout = 120.0,check = check)
            except asyncio.TimeoutError:
                try:
                    await message.edit("Message no longer Active",embed = embed,components = [
                        [
                            Button(label = "Back",disabled = True,style = 1),
                            Button(label = "Forward",disabled = True,style = 1)
                        ]
                    ])
                    break
                except:
                    break

            if not interaction.user.id == ctx.message.author.id:
                embed1=discord.Embed(description=f"Only {ctx.message.author.mention} can use these buttons!", color=discord.Color.red())
                await interaction.respond(embed = embed1)
                continue

            if interaction.component.label == "Forward":
                index += 1
            else:
                if index == 1:
                    embed=discord.Embed(description=f"Hey, there aren't negative page numbers", color=discord.Color.red())
                    await interaction.respond(embed = embed)
                    continue
                else:
                    index -= 1

            embed=discord.Embed(title=f"Mod Tracking for {member}",description=f"`{len(logs)}` actions", color=discord.Color.random())

            index = int(index)
            logamount = len(logs)
            if index > 1:
                if (index - 1) * 9 < logamount:
                    if int(index) * 9 > logamount:
                        end = logamount 
                    else:
                        end = (index)*9
                    
                    start = (index-1) * 9
                else:
                    await interaction.respond(content=f"There are not {index} pages.")
                    index -= 1
                    continue
            else:
                start = 0
                if logamount > 9:
                    end = 9
                else:
                    end = logamount 
            for log in range(start,end):
                embed.add_field(name=f'Action {len(logs)-log}',value = f'{logs[log][1]}\n{logs[log][0]}',inline = True)

            embed.set_footer(text=f"Showing page {index} out of {math.ceil(logamount/9)}")


            if index == 1 and index == math.ceil(logamount/9):
                await interaction.message.edit(embed = embed,components = [
                    [
                        Button(label = "Back",disabled = True,style = 1),
                        Button(label = "Forward",disabled = True,style = 1)
                    ]])
            elif index == 1:
                await interaction.message.edit(embed = embed,components = [
                    [
                        Button(label = "Back",disabled = True,style = 1),
                        Button(label = "Forward",style = 1)
                    ]])
            elif index >= math.ceil(logamount/9):
                await interaction.message.edit(embed = embed,components = [
                    [
                        Button(label = "Back",style = 1),
                        Button(label = "Forward",disabled = True,style = 1)
                    ]])
            else:
                await interaction.message.edit(embed = embed,components = [
                    [
                        Button(label = "Back",style = 1),
                        Button(label = "Forward",style = 1)
                    ]])
            if not interaction.responded:
                await interaction.respond(type= 6)

    @commands.command(aliases = ['modlb'],description = "View the mod tracking leaderboard of the server.",help = 'actionleaderboard')
    @modtrack_role_check()
    async def actionleaderboard(self,ctx):
        users,log = await self.pull_leaderboard(ctx.guild.id)

        embed=discord.Embed(title="Mod Leaderboard", color=discord.Color.random())
        
        count = 1
        amount = len(users) 
        start = 0
        pages = amount//10 + 1
        index = 1
        if amount <= 10:
            end = amount
        else:
            end = 11
        for user in users[start:end]:
            logs = log[user]
            embed.add_field(name=f"{count}",value=f'<@{user}> {logs} actions',inline=False)
            count += 1

            if count >= 11:
                break
                
        embed.set_footer(text = f'Page {index} of {amount//10 + 1}')
        if pages == 1:
            await ctx.reply(embed = embed,components = [
                        [
                            Button(label = "Back",disabled = True,style = 1),
                            Button(label = "Forward",disabled = True,style = 1)
                        ]
                    ])    
        else:
            message = await ctx.reply(embed = embed,components = [
                        [
                            Button(label = "Back",disabled = True,style = 1),
                            Button(label = "Forward",style = 1)
                        ]
                    ])    

            def check(i):
                if i.message.id == message.id:
                    if (i.component.label.startswith("Forward") or i.component.label.startswith("Back")):
                        return True
                    else:
                        return False
                else:
                    return False
            
            while True:
                try:
                    interaction = await self.client.wait_for("button_click", timeout = 120.0,check = check)
                except asyncio.TimeoutError:
                    try:
                        await message.edit("Message no longer Active",embed = embed,components = [
                            [
                                Button(label = "Back",disabled = True,style = 1),
                                Button(label = "Forward",disabled = True,style = 1)
                            ]
                        ])
                        break
                    except:
                        break

                if not interaction.user.id == ctx.message.author.id:
                    embed=discord.Embed(description=f"Only {ctx.message.author.mention} can use these buttons!", color=discord.Color.red())
                    await interaction.respond(embed = embed)
                    continue

                if interaction.component.label == "Forward":
                    index += 1
                else:
                    if index == 1:
                        embed=discord.Embed(description=f"Hey, there aren't negative page numbers", color=discord.Color.red())
                        await interaction.respond(embed = embed)
                        continue
                    else:
                        index -= 1
                embed=discord.Embed(title="Mod Leaderboard", color=discord.Color.random())
                start = (index-1) * 10
                
                if amount >= start + 10:
                    end = start + 10
                else:
                    end = amount
                #await ctx.send(f"Index is now {index}\nStarting at {start} and ending at {end}\nThere are {pages} pages and {amount} users.")
                count = start + 1
                for user in users[start:end]:
                    logs = log[user]
                    embed.add_field(name=f"{count}",value=f'<@{user}> {logs} actions',inline=False)
                    count += 1
                embed.set_footer(text = f'Page {index} of {amount//10 + 1}')
                if index == 1 and index == pages:
                    await interaction.message.edit(embed = embed,components = [
                        [
                            Button(label = "Back",disabled = True,style = 1),
                            Button(label = "Forward",disabled = True,style = 1)
                        ]])
                elif index == 1:
                    await interaction.message.edit(embed = embed,components = [
                        [
                            Button(label = "Back",disabled = True,style = 1),
                            Button(label = "Forward",style = 1)
                        ]])
                elif index >= pages:
                    await interaction.message.edit(embed = embed,components = [
                        [
                            Button(label = "Back",style = 1),
                            Button(label = "Forward",disabled = True,style = 1)
                        ]])
                else:
                    await interaction.message.edit(embed = embed,components = [
                        [
                            Button(label = "Back",style = 1),
                            Button(label = "Forward",style = 1)
                        ]])
                if not interaction.responded:
                    await interaction.respond(type= 6)
                
def setup(client):
    client.add_cog(ModTracking(client))