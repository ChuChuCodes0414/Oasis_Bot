import discord
from discord.ext import commands
from discord.commands import slash_command
import json
import firebase_admin
from firebase_admin import db
import asyncio
import datetime


class HelpRewrite(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Help Rewrite Cog Loaded.')
    
    class Dropdown(discord.ui.Select):
        def __init__(self):

            # Set the options that will be presented inside the dropdown
            options = [
                discord.SelectOption(
                    label="Channels", description="Discord text channel management."
                ),
                discord.SelectOption(
                    label="Dank Cafe", description="Custom commands for .gg/dankcafe"
                ),
                discord.SelectOption(
                    label="Event Logging", description="Events management system for event managers."
                ),
                discord.SelectOption(
                    label="Fun", description="Fun commands and events to keep yourself entertained."
                ),
                discord.SelectOption(
                    label="Invites", description="Invite tracking and logging for your server."
                ),
                discord.SelectOption(
                    label="Lottery", description="Automatic dank memer lottery tracking."
                ),
                discord.SelectOption(
                    label="Mod", description="Simple and easy to use mod commands."
                ),
                discord.SelectOption(
                    label="Mod Tracking", description="Mod action logging for your mods or staff team."
                ),
                discord.SelectOption(
                    label="Music", description="Music commands with support for youtube, spotify, and more."
                ),
                discord.SelectOption(
                    label="Private Channels", description="Private channel management for adding and removing members."
                ),
                discord.SelectOption(
                    label="Settings", description="Configuration and settings for your server."
                ),
                discord.SelectOption(
                    label="Sniper", description="Powerful sniping commands including purges and images!"
                ),
                discord.SelectOption(
                    label="Status", description="Bot status commands to check if the bot is alive."
                ),
                discord.SelectOption(
                    label="Utility", description="Utility commands to check member or server info."
                ),
                discord.SelectOption(
                    label="War", description="A fun event to take you and your friends to war!"
                ),
                discord.SelectOption(
                    label="Winter", description="Limited time event that drops gingerbread for your server."
                ),
            ]

            super().__init__(
                placeholder="Choose your favourite colour...",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.send_message(
                f"You clicked {self.values[0]}"
            )
    
    class DropdownView(discord.ui.View):
        def __init__(self):
            super().__init__()

            # Adds the dropdown to our view object.
            self.add_item(HelpRewrite.Dropdown())
    
    @slash_command(guild_ids=[870125583886065674])
    async def helprewrite(
        self,
        ctx,
    ):
        view = self.DropdownView()
        await ctx.respond("Help",view = view)

def setup(client):
    client.add_cog(HelpRewrite(client))