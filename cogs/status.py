import discord
from discord.ext import commands
import json
import datetime

class Status(commands.Cog):
    """
        Bot status, pings, updates.
    """
    def __init__(self,client):
        self.client = client
        self.short = "<:status:950594213391790152> | Bot Status"

    def get_prefix(self,client,guild):
        with open('prefixes.json','r') as f:
            prefixes = json.load(f)
        return prefixes[str(guild.id)]
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot Status Cog Loaded.')

    @commands.command(help = "Returns a message.")
    async def ping(self,ctx):
        embed = discord.Embed(title = "Pong 🏓",color = discord.Color.random())
        embed.set_footer(text = "For more detailed information, use pingmore.")
        await ctx.reply(embed = embed)
    
    @commands.command(help = "Get the bot's ping.")
    async def pingmore(self,ctx):
        apiping = round(self.client.latency*1000)
        embed = discord.Embed(title = "Pong 🏓",description = f"API Ping: `{apiping}ms`",color = discord.Color.random())
        embed.set_footer(text = "Note: This message can be misleading.")
        message = await ctx.reply(embed = embed)
        latency = ctx.message.created_at - message.created_at
        embed = discord.Embed(title = "Pong 🏓",description = f"API Ping: `{apiping}ms`\nMessage Latency: `{latency.microseconds*0.001}ms`",color = discord.Color.random())
        embed.set_footer(text = "Note: This message can be misleading.")
        await message.edit(embed = embed)

    @commands.command(help = "Quick information about the bot.")
    async def botinfo(self,ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"{self.client.user.name}",description=f"Bot Information", color=discord.Color.random())
        embed.add_field(name="Name", value=f"{self.client.user.name}", inline=True) 
        embed.add_field(name="Creator", value=f"ChuGames#0001", inline=True)
        embed.add_field(name="Current Version", value=f"2.0.0", inline=False)
        embed.add_field(name="Description", value=f"A helpful bot with a variety of features, from private channels to mod logging. Ping the bot to find out the prefix!", inline=False)
        embed.add_field(name="Server Count", value=f"{len(self.client.guilds)} servers", inline=False)
        embed.add_field(name="Member Count", value=f"{len(self.client.users)} servers", inline=False)
        embed.add_field(name="Found any Bugs?", value=f"Join the [support server](https://discord.com/invite/9pmGDc8pqQ)", inline=False)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)

    @commands.command(help = "Invite the bot or join the support server.")
    async def invite(self,ctx):
        embed = discord.Embed(title = "Invite links",description = "Invite the bot",color = discord.Color.random())
        embed.add_field(name = 'Oasis Bot Invite',value = "Currently Unvailable\n[Read More Here](https://pastebin.com/TUBAdUhT)")
        embed.add_field(name = 'Serenity Bot Invite',value = '[Bot Invite](https://discord.com/api/oauth2/authorize?client_id=752335987761217576&permissions=8&scope=bot)',inline = False)
        embed.add_field(name = 'Support Server',value = '[Server Invite](https://discord.com/invite/9pmGDc8pqQ)',inline = False)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text = f'{ctx.guild.name}',icon_url = ctx.message.channel.guild.icon)
        await ctx.reply(embed = embed)
    
    @commands.command(help = "Rules for the bot. By using the bot, you agree to these rules.")
    async def botrules(self,ctx):
        embed = discord.Embed(title = "Oasis Bot Rules",description = "By continuing to use this bot, you agree to the following rules.",color = discord.Color.random())
        embed.add_field(name = "1. Spamming",value = "You shall, under no circumstances, attempt to 'spam' commands or 'break' the bot. This includes any user macros to gain an unfair advantage through any bot features",inline = False)
        embed.add_field(name = "2. Bugs/Exploits",value = "You shall not continually use any known bugged out commands, or exploit any commands that are deemed 'bugged' or not function in any way. Please report any bugs/exploits via the support server.",inline = False)
        embed.add_field(name = "3. Harassment/Slurs",value = "You shall not use this bot to harass any other user for any reason, or to send slurs through any bot feature.",inline = False)
        embed.add_field(name = "4. Language",value = "Any excessive abusive language advertised through the bot is strictly prohibited. This includes, but is not limited to, advertisements or swears.",inline = False)
        embed.add_field(name = "5. Cross-Trading",value = "Some limited events may bring tradeable currency to the bot. Any attempt to trade this currency for other bot currency, real-life money, or other forms of transfer are strictly prohibited.",inline = False)
        embed.add_field(name = "6. Discord TOS",value = "You are required to follow all terms outlined in the Discord Terms of Service while using this bot.",inline = False)
        embed.add_field(name = "7. Staff Respect",value = "All staff decisions from the Oasis Bot Team are final, and no witch-hunting of any kind is allowed.",inline = False)
        embed.set_footer(text = "Staff members reserve the right to limit or remove your access to the bot, and all decisions are final.")
        await ctx.reply(embed = embed)
    
    @commands.command(help = "Privacy information, data collection information.")
    async def privacy(self,ctx):
        embed = discord.Embed(title = "Privacy Policy/Information",description = "This is our privacy and data collection information. Please review this if you are concerned or interested about data collection.",color = discord.Color.random())
        embed.add_field(name = "What data is collected?",value = "To make information clearer, this information will be split into guild and user data, and then temporary and 'permanent' data. The bot collects different pieces of data from all categories to function. This data is essential for the bot to store anything long term.",inline = False)
        embed.add_field(name = "Guild Data",value = "The main data we store in terms of your guild/server is settings data, such as setup roles or channels. These are stored in the forms of discord provided id, and are stored when you run a command to change a setting. This data is stored permanetely until you remove it. The rest of your guild data is linked to a user.",inline = False)
        embed.add_field(name = "User Data",value = "More user data is stored than guild data. User data includes things like fight statistics, mod tracking data, event data, and more. This data is stored permanently until a user chooses to remove it. For a full list of what commands store data, you may request one in the bot support server.",inline = False)
        embed.add_field(name = "Temporary User Data",value = "For use in the 'sniper' function, message content and information is stored temporarily. This includes, but is not limited to, text, embeds, images, and files. Message content is also captured in some settings functions, as well as some drop events. This data is never stored permanently, and is deleted after a setup period of time.",inline = False)
        embed.add_field(name = "User Data Requests",value = "Users can always request a full list of their data if they wish. To do so, they should go to the bot support server, and request in the support channel. Please note this request may take some time. Users will only be able to request their own data that correlates to their user id.",inline = False)
        embed.add_field(name = "Guild Data Request",value = "**Server Owners Only** can request a full list of their guild data. This includes mainly the guild settings or event data. This **does not** include any user specific data, as users themselves must request this. This request can also be made in the bot support server, and may take a while to process.",inline = False)
        embed.add_field(name = "Data Removal",value = "Users and server owners can request the deletion of their data completely if they wish, and should make this request in the bot support server in the support channel.",inline = False)
        embed.set_footer(text = "Any concerns can be posted in the bot support server, or directly dmed to the bot owner.")
        await ctx.reply(embed = embed)

async def setup(client):
    await client.add_cog(Status(client))

