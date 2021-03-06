import discord
from discord import ui
from discord.ext import commands, menus
from itertools import starmap, chain

class MyHelp(commands.HelpCommand):
    def get_command_brief(self, command):
        return command.help or "Command is not documented."

    async def send_bot_help(self, mapping):
        message = self.get_destination()
        embed = discord.Embed(title = f"Bot Help",description = f"Categories Listed Below | `{len(list(chain.from_iterable(mapping.values())))}` Commands Loaded",color = discord.Color.random())
        for cog, commands in mapping.items():
            if cog and cog.qualified_name not in ['Dev','Jishaku','LoggingError','HelpCommand']:
                embed.add_field(name = cog.qualified_name,value = cog.short + "\n" + f"`{len(commands)} Commands`")
        embed.set_footer(text = "Use [prefix]help <category> to see the commands in the category.")
        await message.reply(embed = embed)
        
    async def send_cog_help(self, cog):
        message = self.get_destination()
        all_commands = cog.get_commands()
        formatter = HelpPageSource(all_commands, self,cog.qualified_name)
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(self.context)

    async def send_command_help(self, command):
        message = self.get_destination()
        embed = discord.Embed(title = command.name,description = command.help,color = discord.Color.random())
        embed.add_field(name = "Command Syntax",value = f"`{self.get_command_signature(command)}`",inline = False)
        embed.add_field(name = "Aliases",value = f'`{", ".join(command.aliases)}`' if command.aliases else "`None`",inline = False)
        embed.add_field(name = "Documentation",value = command.brief,inline = False)
        await message.reply(embed = embed)

    async def send_group_help(self, group):
        message = self.get_destination()
        embed = discord.Embed(title = f"Group Command: {group.name}",description = group.help,color = discord.Color.random())
        build = ""
        for command in group.commands:
            build += f"**{command.name}**\n{command.help}\n"
        embed.add_field(name = "Subcommands",value = build)
        embed.set_footer(text = "Use [prefix]help <parent command(s)> <subcommand> for more information!")
        await message.reply(embed = embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=error)
        message = self.get_destination()
        await message.reply(embed=embed)

    def get_destination(self):
        return self.context.message

class MyMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source, *, delete_message_after=False):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.message)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value
    
    async def send_initial_message(self, ctx, message):
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await message.reply(**kwargs)
    
    async def on_timeout(self):
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author

    @ui.button(emoji='<:doubleleft:930948763885899797>', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction,button):
        await self.show_page(0)
        await interaction.response.defer()

    @ui.button(emoji='<:arrowleft:930948708458172427>', style=discord.ButtonStyle.blurple)
    async def before_page(self, interaction,button):
        await self.show_checked_page(self.current_page - 1)
        await interaction.response.defer()

    @ui.button(emoji='<:arrowright:930948684718432256>', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction,button):
        await self.show_checked_page(self.current_page + 1)
        await interaction.response.defer()

    @ui.button(emoji='<:doubleright:930948740557193256>', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction, button):
        await self.show_page(self._source.get_max_pages() - 1)
        await interaction.response.defer()
    
    @ui.button(label='End Interaction', style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction, button):
        await interaction.response.defer()
        self.stop()
        for child in self.children: 
            child.disabled = True   
        await self.message.edit(view=self) 

class HelpPageSource(menus.ListPageSource):
    def __init__(self, data, helpcommand,cogname):
        super().__init__(data, per_page=6)
        self.helpcommand = helpcommand
        self.cogname = cogname

    def format_command_help(self, no, command):
        if command.hidden == True:
            return ""
        name = command.name
        docs = self.helpcommand.get_command_brief(command)
        return f"**{no}. {name}**\n{docs}"
    
    async def format_page(self, menu, entries):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        for entry in entries:
            if entry.hidden == True:
                entries.remove(entry)
        iterator = starmap(self.format_command_help, enumerate(entries, start=starting_number))
        page_content = "\n".join(iterator)
        embed = discord.Embed(
            title=f"{self.cogname} Commands [{page + 1}/{max_page}]", 
            description=page_content,
            color=0xffcccb
        )
        embed.set_footer(text=f"Use [prefix]help <command> for more information on each command.")  # author.avatar in 2.0
        return embed


class HelpCommand(commands.Cog):
    def __init__(self,client):
        self.client = client
        help_command = MyHelp()
        help_command.cog = self # Instance of YourCog class
        client.help_command = help_command
    

async def setup(client):
    await client.add_cog(HelpCommand(client))