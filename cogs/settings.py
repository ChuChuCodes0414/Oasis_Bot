from pyexpat.errors import messages
import discord
from discord.ext import commands
import datetime
import firebase_admin
from firebase_admin import db
import asyncio
import numpy

class Configure(commands.Cog):
    """
        Settings for the bot. There is a lot of things to change and setup, so use help commands to navigate your way through. You need manage server perms to set anything up.
    """

    def __init__(self,client):
        self.client = client
        self.short = "⚙ | Bot Settings"
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Settings Cog Loaded.')

    @commands.group(help = "The base command to configure settings by category.")
    @commands.has_permissions(manage_guild = True)
    async def settings(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply(embed = discord.Embed(description = "You did not select a category to edit!\nCheck `[prefix]help settings` to see the categories.",color = discord.Color.red()))

    @settings.command(help = "Edit all event settings.")
    @commands.has_permissions(manage_guild = True)
    async def events(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        guild_settings = ref.child(str(ctx.message.guild.id)).get()
        view = EventsSettings(ctx,guild_settings)
        embed = await view.generate_embed()
        message = await ctx.send(embed = embed,view = view)
        view.message = message
        timeout = await view.wait()
        if timeout or view.cancel:
            return
        ref.child(str(ctx.message.guild.id)).set(view.guild_settings)
        await message.reply(embed = discord.Embed(description = "Settings updated!",color = discord.Color.green()))
    
    @settings.command(help = "Edit all moderation settings.")
    @commands.has_permissions(manage_guild = True)
    async def moderation(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        guild_settings = ref.child(str(ctx.message.guild.id)).get()
        view = ModerationSettings(ctx,guild_settings)
        embed = await view.generate_embed()
        message = await ctx.send(embed = embed,view = view)
        view.message = message
        timeout = await view.wait()
        if timeout or view.cancel:
            return
        ref.child(str(ctx.message.guild.id)).set(view.guild_settings)
        await message.reply(embed = discord.Embed(description = "Settings updated!",color = discord.Color.green()))
    
    @settings.command(help = "Edit all sniper settings.")
    @commands.has_permissions(manage_guild = True)
    async def sniper(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        guild_settings = ref.child(str(ctx.message.guild.id)).get()
        view = SniperSettings(ctx,guild_settings)
        embed = await view.generate_embed()
        message = await ctx.send(embed = embed,view = view)
        view.message = message
        timeout = await view.wait()
        if timeout or view.cancel:
            return
        ref.child(str(ctx.message.guild.id)).set(view.guild_settings)
        await message.reply(embed = discord.Embed(description = "Settings updated!",color = discord.Color.green()))
    
    @settings.command(help = "Edit all channels settings.")
    @commands.has_permissions(manage_guild = True)
    async def channels(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        guild_settings = ref.child(str(ctx.message.guild.id)).get()
        view = ChannelSettings(ctx,guild_settings)
        embed = await view.generate_embed()
        message = await ctx.send(embed = embed,view = view)
        view.message = message
        timeout = await view.wait()
        if timeout or view.cancel:
            return
        ref.child(str(ctx.message.guild.id)).set(view.guild_settings)
        await message.reply(embed = discord.Embed(description = "Settings updated!",color = discord.Color.green()))
    
    @settings.command(aliases = ['other'],help = "Edit all miscellaneous settings.")
    @commands.has_permissions(manage_guild = True)
    async def miscellaneous(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        guild_settings = ref.child(str(ctx.message.guild.id)).get()
        view = MiscellaneousSettings(ctx,guild_settings)
        embed = await view.generate_embed()
        message = await ctx.send(embed = embed,view = view)
        view.message = message
        timeout = await view.wait()
        if timeout or view.cancel:
            return
        ref.child(str(ctx.message.guild.id)).set(view.guild_settings)
        await message.reply(embed = discord.Embed(description = "Settings updated!",color = discord.Color.green()))
    
    @settings.command(aliases = ['util'],help = "Edit all utility/bump settings.")
    @commands.has_permissions(manage_guild = True)
    async def utility(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        guild_settings = ref.child(str(ctx.message.guild.id)).get()
        view = UtilitySettings(ctx,guild_settings)
        embed = await view.generate_embed()
        message = await ctx.send(embed = embed,view = view)
        view.message = message
        timeout = await view.wait()
        if timeout or view.cancel:
            return
        ref.child(str(ctx.message.guild.id)).set(view.guild_settings)
        if view.guild_settings.get("bumpchannel",None):
            cog = self.client.get_cog("utility")
            cog.active[str(ctx.guild.id)] = str(view.guild_settings.get("bumpchannel"))
        await message.reply(embed = discord.Embed(description = "Settings updated!",color = discord.Color.green()))
    
    @settings.command(help = "Edit all drops settings.")
    @commands.has_permissions(manage_guild = True)
    async def drops(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        guild_settings = ref.child(str(ctx.message.guild.id)).get()
        view = DropsSettings(ctx,guild_settings)
        embed = await view.generate_embed()
        message = await ctx.send(embed = embed,view = view)
        view.message = message
        timeout = await view.wait()
        if timeout or view.cancel:
            return
        ref.child(str(ctx.message.guild.id)).set(view.guild_settings)
        cog = self.client.get_cog("dropsgame")
        cog.settings[str(ctx.guild.id)] = view.drop_settings
        await message.reply(embed = discord.Embed(description = "Settings updated!",color = discord.Color.green()))
    
    @commands.command(help = "Enable certain commands for your server!",usage = "<command> <user,role,channel,or all>",brief = "This command can help you enable commands for your server. Suppose that you disabled a command for everyone, but want your admin team to use it. You might use the command:\n" + 
        "`enable iq @Admin`\nOr if you want to enable the `iq` command for everyone everywhere, you can use\n`enable iq all`\nDo note that any sort of enable will override all disables for a command.")
    @commands.has_permissions(manage_guild = True) 
    async def enable(self,ctx,command,userinput):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        command = self.client.get_command(command)
        if not command:
            return await ctx.reply("That does not look like a valid command name!")
        if userinput == "all":
            if ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("aall").get():
                return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
            ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("aall").set(True)
            embed = discord.Embed(title = "Sucessfully Enabled!",description = f"Enabled the command **{command}** for everyone.")
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
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
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("ausers").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("ausers").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("ausers").set(store)
        elif guild.get_role(userinput):
            userinputobj = guild.get_role(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("aroles").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("aroles").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("aroles").set(store)
        elif guild.get_channel(userinput):
            userinputobj = guild.get_channel(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("achannels").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("achannels").set([userinput])
            else:
                store.append(userinput)
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("achannels").set(store)
        else:
            return await ctx.reply("I could not process your input! Please try again.")

        embed = discord.Embed(title = "Sucessfully Enabled!",description = f"Enabled the command **{command}** for {userinputobj.mention}.")
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)

    @commands.command(help = "Disable certain commands for your server!",usage = "<command> <user,role,channel,or all>",brief = "This command can help you disable commands for your server. Say you do not want people spamming the `iq` command in your general chat. You can disable it using the following:\n" + 
        "`disable iq #general`\nOr if you want to disable the `iq` command for everyone everywhere, you can use\n`disable iq all`\nDo note that any sort of enable will override all disables for a command.")
    @commands.has_permissions(manage_guild = True) 
    async def disable(self,ctx,command,userinput):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        command = self.client.get_command(command)
        if not command:
            return await ctx.reply("That does not look like a valid command name!")
        if userinput == "all":
            if ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("dall").get():
                return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
            ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("dall").set(True)
            embed = discord.Embed(title = "Sucessfully Disabled!",description = f"Disabled the command **{command}** for everyone.")
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
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
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("dusers").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("dusers").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("dusers").set(store)
        elif guild.get_role(userinput):
            userinputobj = guild.get_role(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("droles").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("droles").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("droles").set(store)
        elif guild.get_channel(userinput):
            userinputobj = guild.get_channel(userinput)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("dchannels").get()
            if not store:
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("dchannels").set([userinput])
            else:
                if userinput in store:
                    return await ctx.reply("Hold up, seems that this command already enabled for these parameters!")
                store.append(userinput)
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child("dchannels").set(store)
        else:
            return await ctx.reply("I could not process your input! Please try again.")

        embed = discord.Embed(title = "Sucessfully Disabled!",description = f"Disabled the command **{command}** for {userinputobj.mention}.")
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)

    @commands.group(help = "Manage already exsisting command rules.",brief = "This command allows you to view and edit exsisting rules. You can define rules by using `[prefix]enable` or `[prefix]disable`")
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

    @rules.command(name = "view",help = "View the rules of a certain command.",brief = "View all the rules for a certain command.")
    @commands.has_permissions(manage_guild = True) 
    async def viewrules(self,ctx,command):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        command = self.client.get_command(command)
        if not command:
            return await ctx.reply("That does not look like a valid command name!")
        settings = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).get()
        if not settings:
            return await ctx.reply("Seems like there aren't any rules for this command. Sometimes the command will have a custom check, you can check by exploring `[prefix]help settings view`")
        aroles = settings.get("aroles",None)
        droles = settings.get("droles",None)
        achannels = settings.get("achannels",None)
        dchannels = settings.get("dchannels",None)
        ausers = settings.get("ausers",None)
        dusers = settings.get("dusers",None)
        aall = settings.get("aall",None)
        dall = settings.get("dall",None)

        embed = discord.Embed(title = f"Rules and Permissions for {command.qualified_name}")

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

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)
    
    @rules.command(name = "remove",help = "Remove a certain rule",usage = "<command> <enable or disable> <application>",brief = "The syntax for this command is slightly confusing, but do not worry! Here are some examples:\n" + 
        "`[prefix]rules remove help enable #general`\n> This will remove the rule that enables the command `help` in the general channel.\n\n" + 
        "`[prefix]rules remove iq disable @Chu`\n> This will remove the rule that disables the command `iq` for the user Chu.\n\n" + 
        "`[prefix]rules remove channelinfo enable all`\n> This will remove the rule that allows the command `channelinfo` to be run by all users.")
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
            if ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child(prefix +"all").get():
                ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child(prefix +"all").set({})
            else:
                return await ctx.reply(f"Hold up, this command does not have a rule for {enabledisable} all!")
            embed = discord.Embed(title = "Sucessfully Revmoed!",description = f"Revmoed the {enabledisable} rule for the command **{command}** for everyone.")
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
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
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child(prefix + "users").get()
            if not store:
                return await ctx.reply(f"This command does not even have any {enabledisable} users, what are you thinking?")
            else:
                if userinput1 in store:
                    store.remove(userinput1)
                    ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child(prefix + "users").set(store)
                else:
                    return await ctx.reply(f"That user is not in the {enabledisable} list for this command.")
        elif guild.get_role(userinput1):
            userinputobj = guild.get_role(userinput1)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child(prefix + "roles").get()
            if not store:
                return await ctx.reply(f"This command does not even have any {enabledisable} roles, what are you thinking?")
            else:
                if userinput1 in store:
                    store.remove(userinput1)
                    ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child(prefix + "roles").set(store)
                else:
                    return await ctx.reply(f"That roles is not in the {enabledisable} list for this command.")
        elif guild.get_channel(userinput1):
            userinputobj = guild.get_channel(userinput1)
            store = ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child(prefix + "channels").get()
            if not store:
                return await ctx.reply(f"This command does not even have any {enabledisable} channels, what are you thinking?")
            else:
                if userinput1 in store:
                    store.remove(userinput1)
                    ref.child(str(ctx.guild.id)).child("rules").child(command.qualified_name).child(prefix + "channels").set(store)
                else:
                    return await ctx.reply(f"That channel is not in the {enabledisable} list for this command.")
        else:
            return await ctx.reply("I could not process your input! Please try again.")

        embed = discord.Embed(title = "Sucessfully Removed!",description = f"Removed the {enabledisable} rule for the command **{command}** for {userinputobj.mention}.")
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)

class EventsSettings(discord.ui.View):
    def __init__(self,ctx,guild_settings):
        super().__init__(timeout = 60)
        self.ctx = ctx
        self.guild_settings = guild_settings
        self.cancel = False
        self.message = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def generate_embed(self):
        eventmanager,eventping,eventchannel,eventlog = self.guild_settings.get("event",None),self.guild_settings.get("eping",None),self.guild_settings.get("echannel",None),self.guild_settings.get("elogging",None)
        embed = discord.Embed(title = f"Server Event Settings for {self.ctx.guild.name}")
        if eventmanager:
            embed.add_field(name = "Event Manager Role",value = f"<@&{eventmanager}>")
        else:
            embed.add_field(name = "Event Manager Role",value = f"None")
        if eventping:
            embed.add_field(name = "Event Ping Role",value = f"<@&{eventping}>")
        else:
            embed.add_field(name = "Event Ping Role",value = f"None")
        if eventchannel:
            embed.add_field(name = "Event Announcement Channel",value = f"<#{eventchannel}>")
        else:
            embed.add_field(name = "Event Announcement Channel",value = f"None")
        if eventlog:
            embed.add_field(name = "Event Logging Channel",value = f"<#{eventlog}>")
        else:
            embed.add_field(name = "Event Logging Channel",value = f"None")
        embed.set_footer(text = "Use the menu buttons below to configure server settings.")
        return embed
        
    @discord.ui.button(label = "Event Manager Role",style = discord.ButtonStyle.gray)
    async def setemanrole(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the role you want to set to the **Event Manager Role** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("event")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                role = await commands.converter.RoleConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Event Manager Role** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["event"] = role.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Event Ping Role",style = discord.ButtonStyle.gray)
    async def seteping(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the role you want to set to the **Event Ping Role** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("eping")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                role = await commands.converter.RoleConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Event Ping Role** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["eping"] = role.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Event Announcement Channel",style = discord.ButtonStyle.gray)
    async def setechannel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the channel you want to set to the **Event Announcement Channel** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("echannel")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                channel = await commands.converter.TextChannelConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Event Announcement Channel** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["echannel"] = channel.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Event Logging Channel",style = discord.ButtonStyle.gray)
    async def setelogging(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the channel you want to set to the **Event Logging Channel** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("elogging")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                channel = await commands.converter.TextChannelConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Event Logging Channel** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["elogging"] = channel.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "✅ Confirm",style = discord.ButtonStyle.green,row = 1)
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()

    @discord.ui.button(label = "❌ Cancel",style = discord.ButtonStyle.red,row = 1)
    async def cancel(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.cancel = True
        self.stop()

class ModerationSettings(discord.ui.View):
    def __init__(self,ctx,guild_settings):
        super().__init__(timeout = 60)
        self.ctx = ctx
        self.guild_settings = guild_settings
        self.cancel = False
        self.message = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def generate_embed(self):
        modtrack,modlogging = self.guild_settings.get("modtrack",None),self.guild_settings.get("mlogging",None)
        embed = discord.Embed(title = f"Server Moderation Settings for {self.ctx.guild.name}")
        if modtrack:
            res = ""
            for role in modtrack:
                res += "\n<@&" + str(role) + ">"
            embed.add_field(name = "Modtrack Roles",value = f"{res}")
        else:
            embed.add_field(name = "Modtrack Roles",value = f"None")
        if modlogging:
            embed.add_field(name = "Modtrack Logging Channel",value = f"<#{modlogging}>")
        else:
            embed.add_field(name = "Modtrack Logging Channel",value = f"None")
    
        embed.set_footer(text = "Use the menu buttons below to configure server settings.")
        return embed
    
    @discord.ui.button(label='Mod Track Roles',style = discord.ButtonStyle.gray)
    async def setmodtrack(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = SetupRoles(self.ctx,self.guild_settings.get("modtrack",[]),self.message,"Mod Track")
        embed = await view.formatrolesembed()
        if len(self.guild_settings.get("modtrack",[])) >= 5:
            view.children[0].disabled = True
        await interaction.response.edit_message(embed = embed,view = view)
        timeout = await view.wait()
        if timeout:
            for child in self.children: 
                child.disabled = True   
            await self.message.edit(view=self) 
        self.guild_settings["modtrack"] = view.roles
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Modtrack Logging Channel",style = discord.ButtonStyle.gray)
    async def setmlogging(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the channel you want to set to the **Modtrack Logging Channel** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("mlogging")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                channel = await commands.converter.TextChannelConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Modtrack Logging Channel** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["mlogging"] = channel.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "✅ Confirm",style = discord.ButtonStyle.green,row = 1)
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()

    @discord.ui.button(label = "❌ Cancel",style = discord.ButtonStyle.red,row = 1)
    async def cancel(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.cancel = True
        self.stop()

class SniperSettings(discord.ui.View):
    def __init__(self,ctx,guild_settings):
        super().__init__(timeout = 60)
        self.ctx = ctx
        self.guild_settings = guild_settings
        self.cancel = False
        self.message = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def generate_embed(self):
        snipelb,snipecd = self.guild_settings.get("snipelb",None),self.guild_settings.get("snipecd",None)
        embed = discord.Embed(title = f"Server Sniper Settings for {self.ctx.guild.name}")

        embed.add_field(name = "Snipe Lookback",value = f"{snipelb}")
        embed.add_field(name = "Snipe Cooldown",value = f"{snipecd}")
    
        embed.set_footer(text = "Use the menu buttons below to configure server settings.")
        return embed
    
    @discord.ui.button(label = "Snipe Lookback",style = discord.ButtonStyle.gray)
    async def setsnipelb(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the number you want to set to the **Snipe Lookback** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("snipelb")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                res = int(msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the number you want to set to the ***Snipe Lookback** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["snipelb"] = res
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Snipe Cooldown",style = discord.ButtonStyle.gray)
    async def setsnipecd(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the number you want to set to the **Snipe Cooldown** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("snipecd")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                res = int(msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the number you want to set to the ***Snipe Cooldown** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["snipecd"] = res
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "✅ Confirm",style = discord.ButtonStyle.green,row = 1)
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()

    @discord.ui.button(label = "❌ Cancel",style = discord.ButtonStyle.red,row = 1)
    async def cancel(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.cancel = True
        self.stop()

class ChannelSettings(discord.ui.View):
    def __init__(self,ctx,guild_settings):
        super().__init__(timeout = 120)
        self.ctx = ctx
        self.guild_settings = guild_settings
        self.cancel = False
        self.message = None

    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction):
        return interaction.user == self.ctx.author

    async def generate_embed(self):
        drole,channels,lmessage,ulmessage = self.guild_settings.get("drole",None),self.guild_settings.get("lchannels",[]),self.guild_settings.get("lmessage","This server has been locked down!"),self.guild_settings.get("ulmessage","This server has been unlocked!")
        embed = discord.Embed(title = f"Server Channels Settings for {self.ctx.guild.name}")
        if drole:
            embed.add_field(name = "Default Role",value = f"<@&{drole}>")
        else:
            embed.add_field(name = "Default Role",value = f"None")
        if len(channels) > 0:
            embed.add_field(name = "Lockdown Channels",value = f"{len(channels)} Channels")
        else:
            embed.add_field(name = "Lockdown Channels",value = "None")
        embed.add_field(name = "Default Lockdown Message",value = lmessage,inline = False)
        embed.add_field(name = "Default Unlockdown Message",value = ulmessage,inline = False)
        embed.set_footer(text = "Use the menu buttons below to configure server settings.")
        return embed
    
    @discord.ui.button(label = "Default Role",style = discord.ButtonStyle.gray)
    async def setdrole(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(description = "Input the role you want to set to the **Default Role** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("drole")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                role = await commands.converter.RoleConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Default Role** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["drole"] = role.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label='Lockdown Channels',style = discord.ButtonStyle.gray)
    async def setlchannels(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = SetupChannels(self.ctx,self.guild_settings.get("lchannels",[]),self.message,"Lockdown")
        embed = await view.formatchannelsembed()
        if len(self.guild_settings.get("lchannels",[])) >= 250:
            view.children[0].disabled = True
        await interaction.response.edit_message(embed = embed,view = view)
        timeout = await view.wait()
        if timeout:
            for child in self.children: 
                child.disabled = True   
            await self.message.edit(view=self) 
        self.guild_settings["lchannels"] = view.channels
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Default Lockdown Message",style = discord.ButtonStyle.gray)
    async def setlmessage(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(description = "Input the text you want to set to the **Default Lockdown Message** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("lmessage")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                text = str(msg.content)
                if len(text) >= 500:
                    embed = discord.Embed(description = "Input the text you want to set to the **Default Lockdown Message** now!\n\n⚠ The maximum character limit is 500 characters!")
                    embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                    await self.message.edit(embed = embed)
                    await msg.delete()
                    continue
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the text you want to set to the **Default Lockdown Message** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["lmessage"] = text
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Default Unlockdown Message",style = discord.ButtonStyle.gray)
    async def setulmessage(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed = discord.Embed(description = "Input the text you want to set to the **Default Unlockdown Message** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("ulmessage")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                text = str(msg.content)
                if len(text) >= 500:
                    embed = discord.Embed(description = "Input the text you want to set to the **Default Unlockdown Message** now!\n\n⚠ The maximum character limit is 500 characters!")
                    embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                    await self.message.edit(embed = embed)
                    await msg.delete()
                    continue
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the text you want to set to the **Default Unlockdown Message** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["ulmessage"] = text
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "✅ Confirm",style = discord.ButtonStyle.green,row = 1)
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()

    @discord.ui.button(label = "❌ Cancel",style = discord.ButtonStyle.red,row = 1)
    async def cancel(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.cancel = True
        self.stop()

class MiscellaneousSettings(discord.ui.View):
    def __init__(self,ctx,guild_settings):
        super().__init__(timeout = 60)
        self.ctx = ctx
        self.guild_settings = guild_settings
        self.cancel = False
        self.message = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def generate_embed(self):
        prefix,ilogging,lottery = self.guild_settings.get("prefix",None),self.guild_settings.get("ilogging",None),self.guild_settings.get("lottery",None)
        embed = discord.Embed(title = f"Server Miscellaneous Settings for {self.ctx.guild.name}")
        embed.add_field(name = "Oasis Bot Prefix",value = f"{prefix}")
        if ilogging:
            embed.add_field(name = "Invite Logging Channel",value = f"<#{ilogging}>")
        else:
            embed.add_field(name = "Invite Logging Channel",value = f"None")
        
        if lottery:
            embed.add_field(name = "Lottery Mod Role",value = f"<@&{lottery}>")
        else:
            embed.add_field(name = "Lottery Mod Role",value = f"None")
        
        embed.set_footer(text = "Use the menu buttons below to configure server settings.")
        return embed
    
    @discord.ui.button(label = "Oasis Prefix",style = discord.ButtonStyle.gray)
    async def setsprefix(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the channel you want to set to the **Oasis Prefix** now!")
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
            if len(msg.content) < 4 and len(msg.content) > 0:
                await msg.delete()
                break
            else:
                embed = discord.Embed(description = "Input the role you want to set to the **Oasis Prefix** now!\n\n⚠ Your prefix must be a max of 3 characters!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["prefix"] = msg.content
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Invite Logging Channel",style = discord.ButtonStyle.gray)
    async def setilogging(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the channel you want to set to the **Invite Logging Channel** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("ilogging")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                channel = await commands.converter.TextChannelConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Invite Logging Channel** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["ilogging"] = channel.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Default Heist Role",style = discord.ButtonStyle.gray)
    async def setdheistdrole(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the role you want to set to the **Default Heist Role** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("dheistdrole")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                role = await commands.converter.RoleConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Default Heist Role** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["dheistdrole"] = role.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Lottery Mod Role",style = discord.ButtonStyle.gray)
    async def setlottery(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the role you want to set to the **Lottery Mod Role** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("lottery")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                role = await commands.converter.RoleConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Lottery Mod Role** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["lottery"] = role.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "✅ Confirm",style = discord.ButtonStyle.green,row = 2)
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()

    @discord.ui.button(label = "❌ Cancel",style = discord.ButtonStyle.red,row = 2)
    async def cancel(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.cancel = True
        self.stop()

class UtilitySettings(discord.ui.View):
    def __init__(self,ctx,guild_settings):
        super().__init__(timeout = 60)
        self.ctx = ctx
        self.guild_settings = guild_settings
        self.cancel = False
        self.message = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def generate_embed(self):
        bump,bumpchannel = self.guild_settings.get("bumpping",None), self.guild_settings.get("bumpchannel")
        embed = discord.Embed(title = f"Server Utility Settings for {self.ctx.guild.name}")

        if bump:
            embed.add_field(name = "Bump Ping Role",value = f"<@&{bump}>")
        else:
            embed.add_field(name = "Bump Ping Role",value = f"None")
        
        if bumpchannel:
            embed.add_field(name = "Bump Channel",value = f"<#{bumpchannel}>")
        else:
            embed.add_field(name = "Bump Channel",value = f"None")

        return embed
    
    @discord.ui.button(label = "Bump Ping Role",style = discord.ButtonStyle.gray)
    async def setbumppingrole(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the role you want to set to the **Bump Ping Role** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("bumpping")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                role = await commands.converter.RoleConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Bump Ping Role** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["bumpping"] = role.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Bump Channel",style = discord.ButtonStyle.gray)
    async def setbchannel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the channel you want to set to the **Bump Channel** now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                try:
                    self.guild_settings.pop("bumpchannel")
                except:
                    pass
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                channel = await commands.converter.TextChannelConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the role you want to set to the **Bump Channel** now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.guild_settings["bumpchannel"] = channel.id
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "✅ Confirm",style = discord.ButtonStyle.green,row = 2)
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.stop()

    @discord.ui.button(label = "❌ Cancel",style = discord.ButtonStyle.red,row = 2)
    async def cancel(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.cancel = True
        self.stop()

class DropsSettings(discord.ui.View):
    def __init__(self,ctx,guild_settings):
        super().__init__(timeout = 60)
        self.ctx = ctx
        self.guild_settings = guild_settings
        self.drop_settings = guild_settings.get("drops",{})
        self.cancel = False
        self.message = None
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def generate_embed(self):
        active,emoji,name,channels = self.drop_settings.get("active",None),self.drop_settings.get("emoji",None),self.drop_settings.get("name",None), self.drop_settings.get("channels",[])
        embed = discord.Embed(title = f"Server Drops Settings for {self.ctx.guild.name}")

        embed.add_field(name = "Active",value = active or "False")

        embed.add_field(name = "Currency Emoji",value = emoji)
        
        embed.add_field(name = "Currency Name",value = name)

        embed.add_field(name = "Drops Channels",value = f"{len(channels)} Channels")

        return embed
    
    @discord.ui.button(label = "Active",style = discord.ButtonStyle.gray)
    async def setactive(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the setting you want to set to the **Active** setting now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, \"true\" to turn drops on, \"false\" to turn drops off.")
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
            if msg.content.lower() == "true":
                await msg.delete()
                self.drop_settings["active"] = True
                if not self.drop_settings.get("emoji",None):
                    self.drop_settings["emoji"] = "<:PalmCoin:873408317521793044>"
                if not self.drop_settings.get("name",None):
                    self.drop_settings["name"] = "Palm Coin"
                break
            elif msg.content.lower() == "false":
                await msg.delete()
                self.drop_settings["active"] = False
                break
            else:
                embed = discord.Embed(description = "Input the setting you want to set to the **Active** setting now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, \"true\" to turn drops on, \"false\" to turn drops off.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Currency Emoji",style = discord.ButtonStyle.gray)
    async def currencyemoji(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the emoji you want to set to the **Currency Emoji** setting now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                self.drop_settings["emoji"] = "<:PalmCoin:873408317521793044>"
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                emoji = await commands.converter.EmojiConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the emoji you want to set to the **Currency Emoji** setting now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.drop_settings["emoji"] = str(emoji)
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "Currency Name",style = discord.ButtonStyle.gray)
    async def currencyname(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Input the text you want to set to the **Currency Name** setting now!")
        embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
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
            if msg.content.lower() == "remove":
                await msg.delete()
                self.drop_settings["name"] = "Palm Coin"
                embed = await self.generate_embed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                name = str(msg.content.lower())
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Input the text you want to set to the **Currency Name** setting now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel your input, or \"remove\" to remove what you currently have setup.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.drop_settings["name"] = name
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label='Drops Channels',style = discord.ButtonStyle.gray)
    async def setdropschannels(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = SetupChannels(self.ctx,self.drop_settings.get("channels",[]),self.message,"Drops")
        embed = await view.formatchannelsembed()
        if len(self.drop_settings.get("channels",[])) >= 250:
            view.children[0].disabled = True
        await interaction.response.edit_message(embed = embed,view = view)
        timeout = await view.wait()
        if timeout:
            for child in self.children: 
                child.disabled = True   
            await self.message.edit(view=self) 
        self.drop_settings["channels"] = view.channels
        embed = await self.generate_embed()
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label = "✅ Confirm",style = discord.ButtonStyle.green,row = 2)
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.guild_settings["drops"] = self.drop_settings
        self.stop()

    @discord.ui.button(label = "❌ Cancel",style = discord.ButtonStyle.red,row = 2)
    async def cancel(self,interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 
        self.cancel = True
        self.stop()

class SetupRoles(discord.ui.View):
    def __init__(self,ctx,roles,message,type):
        super().__init__()
        self.ctx = ctx
        self.roles = roles
        self.message = message
        self.type = type
    
    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def formatrolesembed(self):
        embed = discord.Embed(title = f"{self.type} Roles Settings")
        res = ""
        if len(self.roles) > 0:
            for role in self.roles:
               res += f"<@&{role}>\n"
            embed.description = res
        else:
            embed.description = "No current roles defined!"
        embed.set_footer(text = "Use the buttons below to continue.")
        return embed
    
    @discord.ui.button(label='Add Role', style= discord.ButtonStyle.green)
    async def addrole(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type in your role now!")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
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
                embed = await self.formatrolesembed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                role = await commands.converter.RoleConverter().convert(self.ctx,msg.content)
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Type in your role now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel input.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.roles.append(role.id)
        embed = await self.formatrolesembed()
        if len(self.roles) >= 5:
            self.children[0].disabled = True
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label='Remove Role', style= discord.ButtonStyle.red)
    async def removerole(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type in your role to remove now!")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
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
                embed = await self.formatrolesembed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                role = await commands.converter.RoleConverter().convert(self.ctx,msg.content)
                if role.id not in self.roles:
                    embed = discord.Embed(description = "Type in your role now!\n\n⚠ That role is not in the current list!")
                    embed.set_footer(text = "Type \"cancel\" to cancel input.")
                    await self.message.edit(embed = embed)
                    await msg.delete()
                    continue
                await msg.delete()
                break
            except:
                embed = discord.Embed(description = "Type in your role now!\n\n⚠ I could not process your input!")
                embed.set_footer(text = "Type \"cancel\" to cancel input.")
                await self.message.edit(embed = embed)
                await msg.delete()
                continue
        self.roles.remove(role.id)
        embed = await self.formatrolesembed()
        if len(self.roles) >= 5:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False
        await self.message.edit(embed = embed,view = self)

    @discord.ui.button(label='Save', style= discord.ButtonStyle.green,row = 1)
    async def savemethods(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.stop()

class SetupChannels(discord.ui.View):
    def __init__(self,ctx,channels,message,type):
        super().__init__()
        self.ctx = ctx
        self.channels = channels
        self.message = message
        self.type = type
    
    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author
    
    async def formatchannelsembed(self):
        embed = discord.Embed(title = f"{self.type} Channels Settings")
        res = ""
        if len(self.channels) > 0:
            for channel in self.channels:
               res += f"<#{channel}>\n"
            embed.description = res
        else:
            embed.description = "No current channels defined!"
        embed.set_footer(text = "Use the buttons below to continue.")
        return embed
    
    @discord.ui.button(label='Add Channel', style= discord.ButtonStyle.green)
    async def addchannel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type in your channel now! You can also input a category id to add that entire category.")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
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
                embed = await self.formatchannelsembed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                channel = await commands.converter.TextChannelConverter().convert(self.ctx,msg.content)
                self.channels.append(channel.id)
            except:
                try:
                    category = await commands.converter.CategoryChannelConverter().convert(self.ctx,msg.content)
                    channels = category.text_channels
                    if len(channels) + len(self.channels) > 250:
                        embed = discord.Embed(description = "Type in your channel now! You can also input a category id to add that entire category.\n\n⚠ Adding this category exceeds the limit of 50 channels!")
                        embed.set_footer(text = "Type \"cancel\" to cancel input.")
                        await self.message.edit(embed = embed)
                        await msg.delete()
                        continue
                    else:
                        self.channels.extend([x.id for x in channels])
                except:
                    embed = discord.Embed(description = "Type in your channel now! You can also input a category id to add that entire category.\n\n⚠ I could not process your input!")
                    embed.set_footer(text = "Type \"cancel\" to cancel input.")
                    await self.message.edit(embed = embed)
                    await msg.delete()
                    continue
            await msg.delete()
            break
        self.channels = numpy.unique(self.channels)
        if isinstance(self.channels, numpy.ndarray):
            self.channels =  self.channels.tolist()
        embed = await self.formatchannelsembed()
        if len(self.channels) >= 250:
            self.children[0].disabled = True
        await self.message.edit(embed = embed,view = self)
    
    @discord.ui.button(label='Remove Channel', style= discord.ButtonStyle.red)
    async def removechannel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description = "Type in your channel to remove now! You can also type in a category id to remove that entire category.")
        embed.set_footer(text = "Type \"cancel\" to cancel input.")
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
                embed = await self.formatchannelsembed()
                await self.message.edit(embed = embed,view = self)
                return
            try:
                channel = await commands.converter.TextChannelConverter().convert(self.ctx,msg.content)
                if channel.id not in self.channels:
                    embed = discord.Embed(description = "Type in your role now! You can also type in a category id to remove that entire category.\n\n⚠ That channel is not in the current list!")
                    embed.set_footer(text = "Type \"cancel\" to cancel input.")
                    await self.message.edit(embed = embed)
                    await msg.delete()
                    continue
                self.channels.remove(channel.id)
            except:
                try:
                    category = await commands.converter.CategoryChannelConverter().convert(self.ctx,msg.content)
                    channels = category.text_channels
                    self.channels = [channel for channel in self.channels if channel not in [x.id for x in channels]]
                except:
                    embed = discord.Embed(description = "Type in your channel now! You can also type in a category id to remove that entire category.\n\n⚠ I could not process your input!")
                    embed.set_footer(text = "Type \"cancel\" to cancel input.")
                    await self.message.edit(embed = embed)
                    await msg.delete()
                    continue
            await msg.delete()
            break
        embed = await self.formatchannelsembed()
        if len(self.channels) >= 250:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False
        await self.message.edit(embed = embed,view = self)

    @discord.ui.button(label='Save', style= discord.ButtonStyle.green,row = 1)
    async def savemethods(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.stop()

async def setup(client):
    await client.add_cog(Configure(client))