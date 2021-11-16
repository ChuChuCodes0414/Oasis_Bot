import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button
import datetime
import math
import firebase_admin
from firebase_admin import db
import random
import asyncio

class Halloween(commands.Cog):
    '''
        Halloween drops for halloween! Use help command for more info.
    '''
    def __init__(self,client):
        self.client = client
        self.pumpkin = "<:Pumpkin:902370683248603158>"
        self.choices = ["button","phrase","unscramble","boss","word"]
        self.titles = ["Quick, pumpkins are being dropped!","Someone dropped some pumpkins!","You found pumpkins in a bag!","Trick or Treat!","Oh, free pumpkins!"]
        self.phrasestext = [
            "𝕋𝕙𝕖𝕣𝕖 𝕚𝕤 𝕞𝕒𝕘𝕚𝕔 𝕚𝕟 𝕥𝕙𝕖 𝕟𝕚𝕘𝕙𝕥 𝕨𝕙𝕖𝕟 𝕡𝕦𝕞𝕡𝕜𝕚𝕟𝕤 𝕘𝕝𝕠𝕨 𝕓𝕪 𝕞𝕠𝕠𝕟𝕝𝕚𝕘𝕙𝕥.",
            "𝕆𝕟 ℍ𝕒𝕝𝕝𝕠𝕨𝕖𝕖𝕟 𝕪𝕠𝕦 𝕘𝕖𝕥 𝕥𝕠 𝕓𝕖𝕔𝕠𝕞𝕖 𝕒𝕟𝕪𝕥𝕙𝕚𝕟𝕘 𝕥𝕙𝕒𝕥 𝕪𝕠𝕦 𝕨𝕒𝕟𝕥 𝕥𝕠 𝕓𝕖.",
            "𝔼𝕧𝕖𝕣𝕪 𝕕𝕒𝕪 𝕚𝕤 ℍ𝕒𝕝𝕝𝕠𝕨𝕖𝕖𝕟 𝕚𝕤𝕟'𝕥 𝕚𝕥? 𝔽𝕠𝕣 𝕤𝕠𝕞𝕖 𝕠𝕗 𝕦𝕤.",
            "𝔾𝕙𝕠𝕤𝕥𝕤 𝕒𝕟𝕕 𝕘𝕠𝕓𝕝𝕚𝕟𝕤 𝕔𝕠𝕞𝕖 𝕥𝕠 𝕡𝕝𝕒𝕪 𝕠𝕟 𝕆𝕔𝕥𝕠𝕓𝕖𝕣’𝕤 𝕗𝕚𝕟𝕒𝕝 𝕕𝕒𝕪!",
            "𝕋𝕙𝕖𝕣𝕖 𝕚𝕤 𝕤𝕠𝕞𝕖𝕥𝕙𝕚𝕟𝕘 𝕙𝕒𝕦𝕟𝕥𝕚𝕟𝕘 𝕚𝕟 𝕥𝕙𝕖 𝕝𝕚𝕘𝕙𝕥 𝕠𝕗 𝕥𝕙𝕖 𝕞𝕠𝕠𝕟.",
            "𝔸𝕟𝕪𝕠𝕟𝕖 𝕔𝕠𝕦𝕝𝕕 𝕤𝕖𝕖 𝕥𝕙𝕒𝕥 𝕥𝕙𝕖 𝕨𝕚𝕟𝕕 𝕨𝕒𝕤 𝕒 𝕤𝕡𝕖𝕔𝕚𝕒𝕝 𝕨𝕚𝕟𝕕 𝕥𝕙𝕚𝕤 𝕟𝕚𝕘𝕙𝕥, 𝕒𝕟𝕕 𝕥𝕙𝕖 𝕕𝕒𝕣𝕜𝕟𝕖𝕤𝕤 𝕥𝕠𝕠𝕜 𝕠𝕟 𝕒 𝕤𝕡𝕖𝕔𝕚𝕒𝕝 𝕗𝕖𝕖𝕝 𝕓𝕖𝕔𝕒𝕦𝕤𝕖 𝕚𝕥 𝕨𝕒𝕤 𝔸𝕝𝕝 ℍ𝕒𝕝𝕝𝕠𝕨𝕤' 𝔼𝕧𝕖.",
            "𝕋𝕙𝕖𝕣𝕖 𝕒𝕣𝕖 𝕟𝕚𝕘𝕙𝕥𝕤 𝕨𝕙𝕖𝕟 𝕥𝕙𝕖 𝕨𝕠𝕝𝕧𝕖𝕤 𝕒𝕣𝕖 𝕤𝕚𝕝𝕖𝕟𝕥 𝕒𝕟𝕕 𝕠𝕟𝕝𝕪 𝕥𝕙𝕖 𝕞𝕠𝕠𝕟 𝕙𝕠𝕨𝕝𝕤.",
            "𝕄𝕒𝕪 𝕪𝕠𝕦𝕣 𝕔𝕒𝕟𝕕𝕪 𝕤𝕦𝕡𝕡𝕝𝕪 𝕝𝕒𝕤𝕥 𝕪𝕠𝕦 𝕨𝕖𝕝𝕝 𝕚𝕟𝕥𝕠 𝕥𝕙𝕖 ℂ𝕙𝕣𝕚𝕤𝕥𝕞𝕒𝕤 𝕤𝕖𝕒𝕤𝕠𝕟.",
            "𝔻𝕦𝕣𝕚𝕟𝕘 𝕥𝕙𝕖 𝕕𝕒𝕪, 𝕀 𝕕𝕠𝕟'𝕥 𝕓𝕖𝕝𝕚𝕖𝕧𝕖 𝕚𝕟 𝕘𝕙𝕠𝕤𝕥𝕤. 𝔸𝕥 𝕟𝕚𝕘𝕙𝕥, 𝕀'𝕞 𝕒 𝕝𝕚𝕥𝕥𝕝𝕖 𝕞𝕠𝕣𝕖 𝕠𝕡𝕖𝕟-𝕞𝕚𝕟𝕕𝕖𝕕.",
            "𝔸 𝕔𝕒𝕟𝕕𝕪 𝕒 𝕕𝕒𝕪 𝕜𝕖𝕖𝕡𝕤 𝕥𝕙𝕖 𝕞𝕠𝕟𝕤𝕥𝕖𝕣𝕤 𝕒𝕨𝕒𝕪.",
            "𝕋𝕣𝕚𝕔𝕜 𝕠𝕣 𝕥𝕣𝕖𝕒𝕥, 𝕓𝕒𝕘 𝕠𝕗 𝕤𝕨𝕖𝕖𝕥𝕤, 𝕘𝕙𝕠𝕤𝕥𝕤 𝕒𝕣𝕖 𝕨𝕒𝕝𝕜𝕚𝕟𝕘 𝕕𝕠𝕨𝕟 𝕥𝕙𝕖 𝕤𝕥𝕣𝕖𝕖𝕥.",
            "𝕎𝕙𝕒𝕥𝕖𝕧𝕖𝕣 𝕪𝕠𝕦 𝕕𝕠, 𝕕𝕠𝕟'𝕥 𝕗𝕒𝕝𝕝 𝕒𝕤𝕝𝕖𝕖𝕡.",
            "ℍ𝕒𝕧𝕖 𝕪𝕠𝕦 𝕔𝕠𝕞𝕖 𝕥𝕠 𝕤𝕚𝕟𝕘 𝕡𝕦𝕞𝕡𝕜𝕚𝕟 𝕔𝕒𝕣𝕠𝕝𝕤?",
            "𝕀𝕥'𝕤 ℍ𝕒𝕝𝕝𝕠𝕨𝕖𝕖𝕟, 𝕖𝕧𝕖𝕣𝕪𝕠𝕟𝕖'𝕤 𝕖𝕟𝕥𝕚𝕥𝕝𝕖𝕕 𝕥𝕠 𝕠𝕟𝕖 𝕘𝕠𝕠𝕕 𝕤𝕔𝕒𝕣𝕖.",
            "𝔼𝕒𝕔𝕙 𝕪𝕖𝕒𝕣, 𝕥𝕙𝕖 𝔾𝕣𝕖𝕒𝕥 ℙ𝕦𝕞𝕡𝕜𝕚𝕟 𝕣𝕚𝕤𝕖𝕤 𝕠𝕦𝕥 𝕠𝕗 𝕥𝕙𝕖 𝕡𝕦𝕞𝕡𝕜𝕚𝕟 𝕡𝕒𝕥𝕔𝕙 𝕥𝕙𝕒𝕥 𝕙𝕖 𝕥𝕙𝕚𝕟𝕜𝕤 𝕚𝕤 𝕥𝕙𝕖 𝕞𝕠𝕤𝕥 𝕤𝕚𝕟𝕔𝕖𝕣𝕖.",
            "𝕎𝕙𝕖𝕣𝕖 𝕥𝕙𝕖𝕣𝕖 𝕚𝕤 𝕟𝕠 𝕚𝕞𝕒𝕘𝕚𝕟𝕒𝕥𝕚𝕠𝕟 𝕥𝕙𝕖𝕣𝕖 𝕚𝕤 𝕟𝕠 𝕙𝕠𝕣𝕣𝕠𝕣.",
            "𝔻𝕖𝕖𝕡 𝕚𝕟𝕥𝕠 𝕥𝕙𝕖 𝕕𝕒𝕣𝕜𝕟𝕖𝕤𝕤 𝕡𝕖𝕖𝕣𝕚𝕟𝕘, 𝕝𝕠𝕟𝕘 𝕀 𝕤𝕥𝕠𝕠𝕕 𝕥𝕙𝕖𝕣𝕖, 𝕨𝕠𝕟𝕕𝕖𝕣𝕚𝕟𝕘, 𝕗𝕖𝕒𝕣𝕚𝕟𝕘, 𝕕𝕠𝕦𝕓𝕥𝕚𝕟𝕘, 𝕕𝕣𝕖𝕒𝕞𝕚𝕟𝕘 𝕕𝕣𝕖𝕒𝕞𝕤 𝕟𝕠 𝕞𝕠𝕣𝕥𝕒𝕝 𝕖𝕧𝕖𝕣 𝕕𝕒𝕣𝕖𝕕 𝕥𝕠 𝕕𝕣𝕖𝕒𝕞 𝕓𝕖𝕗𝕠𝕣𝕖.",
            "𝕋𝕙𝕖 𝕓𝕝𝕠𝕠𝕕 𝕚𝕤 𝕝𝕚𝕗𝕖.",
            "ℍ𝕒𝕡𝕡𝕪 ℍ𝕒𝕦𝕟𝕥𝕚𝕟𝕘!",
            "𝕊𝕥𝕠𝕡 𝕚𝕟 𝕗𝕠𝕣 𝕒 𝕤𝕡𝕖𝕝𝕝.",
            "ℙ𝕝𝕖𝕒𝕤𝕖 𝕡𝕒𝕣𝕜 𝕒𝕝𝕝 𝕓𝕣𝕠𝕠𝕞𝕤 𝕒𝕥 𝕥𝕙𝕖 𝕕𝕠𝕠𝕣.",
            "𝔹𝕖 𝕤𝕦𝕣𝕖 𝕥𝕠 𝕙𝕠𝕝𝕝𝕖𝕣 𝕥𝕣𝕚𝕔𝕜 𝕠𝕣 𝕥𝕣𝕖𝕒𝕥!",

            "𝔽𝕚𝕟𝕕 𝕥𝕙𝕖 𝕥𝕙𝕚𝕟𝕘 𝕥𝕙𝕒𝕥 𝕞𝕦𝕤𝕥 𝕓𝕖 𝕣𝕖𝕒𝕕, 𝕝𝕖𝕤𝕥 𝕪𝕠𝕦𝕣 𝕙𝕖𝕒𝕣𝕥 𝕓𝕖 𝕗𝕚𝕝𝕝𝕖𝕕 𝕨𝕚𝕥𝕙 𝕕𝕣𝕖𝕒𝕕.",            
            "𝕀𝕥'𝕤 𝕒𝕤 𝕞𝕦𝕔𝕙 𝕗𝕦𝕟 𝕥𝕠 𝕤𝕔𝕒𝕣𝕖 𝕒𝕤 𝕥𝕠 𝕓𝕖 𝕤𝕔𝕒𝕣𝕖𝕕.",            
            "𝔻𝕒𝕣𝕜𝕟𝕖𝕤𝕤 𝕗𝕒𝕝𝕝𝕤 𝕒𝕔𝕣𝕠𝕤𝕤 𝕥𝕙𝕖 𝕝𝕒𝕟𝕕, 𝕋𝕙𝕖 𝕄𝕚𝕕𝕟𝕚𝕘𝕙𝕥 ℍ𝕠𝕦𝕣 𝕚𝕤 𝕔𝕝𝕠𝕤𝕖 𝕒𝕥 𝕙𝕒𝕟𝕕.",            
            "𝕋𝕙𝕖 𝕦𝕟𝕚𝕧𝕖𝕣𝕤𝕖 𝕚𝕤 𝕗𝕦𝕝𝕝 𝕠𝕗 𝕞𝕒𝕘𝕚𝕔𝕒𝕝 𝕥𝕙𝕚𝕟𝕘𝕤 𝕡𝕒𝕥𝕚𝕖𝕟𝕥𝕝𝕪 𝕨𝕒𝕚𝕥𝕚𝕟𝕘 𝕗𝕠𝕣 𝕠𝕦𝕥 𝕨𝕚𝕥𝕤 𝕥𝕠 𝕘𝕣𝕠𝕨 𝕤𝕙𝕒𝕣𝕡𝕖𝕣.",            
            "𝔻𝕠 𝕪𝕠𝕦 𝕓𝕖𝕝𝕚𝕖𝕧𝕖 𝕚𝕟 𝕕𝕖𝕤𝕥𝕚𝕟𝕪? 𝕋𝕙𝕒𝕥 𝕖𝕧𝕖𝕟 𝕥𝕙𝕖 𝕡𝕠𝕨𝕖𝕣𝕤 𝕠𝕗 𝕥𝕚𝕞𝕖 𝕔𝕒𝕟 𝕓𝕖 𝕒𝕝𝕥𝕖𝕣𝕖𝕕 𝕗𝕠𝕣 𝕒 𝕤𝕚𝕟𝕘𝕝𝕖 𝕡𝕦𝕣𝕡𝕠𝕤𝕖?",            
            "ℍ𝕒𝕝𝕝𝕠𝕨𝕖𝕖𝕟 𝕚𝕤 𝕠𝕡𝕡𝕠𝕣𝕥𝕦𝕟𝕚𝕥𝕪 𝕥𝕠 𝕓𝕖 𝕣𝕖𝕒𝕝𝕝𝕪 𝕔𝕣𝕖𝕒𝕥𝕚𝕧𝕖.",            "𝕎𝕙𝕖𝕟 𝕥𝕙𝕖 𝕨𝕚𝕥𝕔𝕙𝕖𝕤 𝕨𝕖𝕟𝕥 𝕨𝕒𝕝𝕥𝕫𝕚𝕟𝕘.",            
            "ℕ𝕖𝕧𝕖𝕣 𝕥𝕣𝕦𝕤𝕥 𝕒𝕟𝕪𝕥𝕙𝕚𝕟𝕘 𝕥𝕙𝕒𝕥 𝕔𝕒𝕟 𝕥𝕙𝕚𝕟𝕜 𝕗𝕠𝕣 𝕚𝕥𝕤𝕖𝕝𝕗 𝕚𝕗 𝕪𝕠𝕦 𝕔𝕒𝕟'𝕥 𝕤𝕖𝕖 𝕨𝕙𝕖𝕣𝕖 𝕚𝕥 𝕜𝕖𝕖𝕡𝕤 𝕚𝕥𝕤 𝕓𝕣𝕒𝕚𝕟.",            
            "𝕀 𝕨𝕠𝕦𝕝𝕕 𝕝𝕚𝕜𝕖, 𝕚𝕗 𝕀 𝕞𝕒𝕪, 𝕥𝕠 𝕥𝕒𝕜𝕖 𝕪𝕠𝕦 𝕠𝕟 𝕒 𝕤𝕥𝕣𝕒𝕟𝕘𝕖 𝕛𝕠𝕦𝕣𝕟𝕖𝕪.",            
            "ℍ𝕒𝕝𝕝𝕠𝕨𝕖𝕖𝕟 𝕚𝕤 𝕟𝕠𝕥 𝕠𝕟𝕝𝕪 𝕒𝕓𝕠𝕦𝕥 𝕡𝕦𝕥𝕥𝕚𝕟𝕘 𝕠𝕟 𝕒 𝕔𝕠𝕤𝕥𝕦𝕞𝕖, 𝕓𝕦𝕥 𝕚𝕥'𝕤 𝕒𝕓𝕠𝕦𝕥 𝕗𝕚𝕟𝕕𝕚𝕟𝕘 𝕥𝕙𝕖 𝕚𝕞𝕒𝕘𝕚𝕟𝕒𝕥𝕚𝕠𝕟 𝕒𝕟𝕕 𝕔𝕠𝕤𝕥𝕦𝕞𝕖 𝕨𝕚𝕥𝕙𝕚𝕟 𝕠𝕦𝕣𝕤𝕖𝕝𝕧𝕖𝕤.",            
            "𝕀𝕗 𝕙𝕦𝕞𝕒𝕟 𝕓𝕖𝕚𝕟𝕘𝕤 𝕙𝕒𝕕 𝕘𝕖𝕟𝕦𝕚𝕟𝕖 𝕔𝕠𝕦𝕣𝕒𝕘𝕖, 𝕥𝕙𝕖𝕪'𝕕 𝕨𝕖𝕒𝕣 𝕥𝕙𝕖𝕚𝕣 𝕔𝕠𝕤𝕥𝕦𝕞𝕖𝕤 𝕖𝕧𝕖𝕣𝕪 𝕕𝕒𝕪 𝕠𝕗 𝕥𝕙𝕖 𝕪𝕖𝕒𝕣, 𝕟𝕠𝕥 𝕛𝕦𝕤𝕥 𝕠𝕟 ℍ𝕒𝕝𝕝𝕠𝕨𝕖𝕖𝕟.",            
            "𝕆𝕟 ℍ𝕒𝕝𝕝𝕠𝕨𝕖𝕖𝕟, 𝕨𝕚𝕥𝕔𝕙𝕖𝕤 𝕔𝕠𝕞𝕖 𝕥𝕣𝕦𝕖; 𝕨𝕚𝕝𝕕 𝕘𝕙𝕠𝕤𝕥𝕤 𝕖𝕤𝕔𝕒𝕡𝕖 𝕗𝕣𝕠𝕞 𝕕𝕣𝕖𝕒𝕞𝕤. 𝔼𝕒𝕔𝕙 𝕞𝕠𝕟𝕤𝕥𝕖𝕣 𝕕𝕒𝕟𝕔𝕖𝕤 𝕚𝕟 𝕥𝕙𝕖 𝕡𝕒𝕣𝕜.",            
            "𝕊𝕙𝕒𝕕𝕠𝕨𝕤 𝕞𝕦𝕥𝕥𝕖𝕣, 𝕞𝕚𝕤𝕥 𝕣𝕖𝕡𝕝𝕚𝕖𝕤; 𝕕𝕒𝕣𝕜𝕟𝕖𝕤𝕤 𝕡𝕦𝕣𝕣𝕤 𝕒𝕤 𝕞𝕚𝕕𝕟𝕚𝕘𝕙𝕥 𝕤𝕚𝕘𝕙𝕤.",            
            "𝕄𝕒𝕘𝕚𝕔 𝕚𝕤 𝕣𝕖𝕒𝕝𝕝𝕪 𝕧𝕖𝕣𝕪 𝕤𝕚𝕞𝕡𝕝𝕖, 𝕒𝕝𝕝 𝕪𝕠𝕦'𝕧𝕖 𝕘𝕠𝕥 𝕥𝕠 𝕕𝕠 𝕚𝕤 𝕨𝕒𝕟𝕥 𝕤𝕠𝕞𝕖𝕥𝕙𝕚𝕟𝕘 𝕒𝕟𝕕 𝕥𝕙𝕖𝕟 𝕝𝕖𝕥 𝕪𝕠𝕦𝕣𝕤𝕖𝕝𝕗 𝕙𝕒𝕧𝕖 𝕚𝕥.",            
            "𝕀'𝕝𝕝 𝕤𝕥𝕠𝕡 𝕨𝕖𝕒𝕣𝕚𝕟𝕘 𝕓𝕝𝕒𝕔𝕜 𝕨𝕙𝕖𝕟 𝕥𝕙𝕖𝕪 𝕞𝕒𝕜𝕖 𝕒 𝕕𝕒𝕣𝕜𝕖𝕣 𝕔𝕠𝕝𝕠𝕣.",            
            "𝕋𝕙𝕖 𝕞𝕠𝕠𝕟 𝕙𝕒𝕤 𝕒𝕨𝕠𝕜𝕖𝕟 𝕨𝕚𝕥𝕙 𝕥𝕙𝕖 𝕤𝕝𝕖𝕖𝕡 𝕠𝕗 𝕥𝕙𝕖 𝕤𝕦𝕟, 𝕥𝕙𝕖 𝕝𝕚𝕘𝕙𝕥 𝕙𝕒𝕤 𝕓𝕖𝕖𝕟 𝕓𝕣𝕠𝕜𝕖𝕟; 𝕥𝕙𝕖 𝕤𝕡𝕖𝕝𝕝 𝕙𝕒𝕤 𝕓𝕖𝕘𝕦𝕟.",            
            "𝕊𝕙𝕖 𝕦𝕤𝕖𝕕 𝕥𝕠 𝕥𝕖𝕝𝕝 𝕞𝕖 𝕥𝕙𝕒𝕥 𝕒 𝕗𝕦𝕝𝕝 𝕞𝕠𝕠𝕟 𝕨𝕒𝕤 𝕨𝕙𝕖𝕟 𝕞𝕪𝕤𝕥𝕖𝕣𝕚𝕠𝕦𝕤 𝕥𝕙𝕚𝕟𝕘𝕤 𝕙𝕒𝕡𝕡𝕖𝕟 𝕒𝕟𝕕 𝕨𝕚𝕤𝕙𝕖𝕤 𝕔𝕠𝕞𝕖 𝕥𝕣𝕦𝕖.",            
            "𝕋𝕙𝕖 𝕕𝕖𝕒𝕕 𝕣𝕚𝕤𝕖 𝕒𝕘𝕒𝕚𝕟, 𝕓𝕒𝕥𝕤 𝕗𝕝𝕪, 𝕥𝕖𝕣𝕣𝕠𝕣 𝕤𝕥𝕣𝕚𝕜𝕖𝕤 𝕒𝕟𝕕 𝕤𝕔𝕣𝕖𝕒𝕞𝕤 𝕖𝕔𝕙𝕠, 𝕗𝕠𝕣 𝕥𝕠𝕟𝕚𝕘𝕙𝕥 𝕚𝕥'𝕤 ℍ𝕒𝕝𝕝𝕠𝕨𝕖𝕖𝕟.",            
            "𝕋𝕙𝕖𝕣𝕖 𝕚𝕤 𝕒 𝕔𝕙𝕚𝕝𝕕 𝕚𝕟 𝕖𝕧𝕖𝕣𝕪 𝕠𝕟𝕖 𝕠𝕗 𝕦𝕤 𝕨𝕙𝕠 𝕚𝕤 𝕤𝕥𝕚𝕝𝕝 𝕒 𝕥𝕣𝕚𝕔𝕜-𝕠𝕣-𝕥𝕣𝕖𝕒𝕥𝕖𝕣 𝕝𝕠𝕠𝕜𝕚𝕟𝕘 𝕗𝕠𝕣 𝕒 𝕓𝕣𝕚𝕘𝕙𝕥𝕝𝕪-𝕝𝕚𝕥 𝕗𝕣𝕠𝕟𝕥 𝕡𝕠𝕣𝕔𝕙.",            
            "𝔹𝕖 𝕒𝕗𝕣𝕒𝕚𝕕, 𝕓𝕖 𝕧𝕖𝕣𝕪 𝕒𝕗𝕣𝕒𝕚𝕕.",            
            "𝕋𝕙𝕖 𝕗𝕒𝕣𝕥𝕙𝕖𝕣 𝕨𝕖'𝕧𝕖 𝕘𝕠𝕥𝕥𝕖𝕟 𝕗𝕣𝕠𝕞 𝕥𝕙𝕖 𝕞𝕒𝕘𝕚𝕔 𝕒𝕟𝕕 𝕞𝕪𝕤𝕥𝕖𝕣𝕪 𝕠𝕗 𝕠𝕦𝕣 𝕡𝕒𝕤𝕥, 𝕥𝕙𝕖 𝕞𝕠𝕣𝕖 𝕨𝕖'𝕧𝕖 𝕔𝕠𝕞𝕖 𝕥𝕠 𝕟𝕖𝕖𝕕 ℍ𝕒𝕝𝕝𝕠𝕨𝕖𝕖𝕟."
        ]
        self.phrases = [
            "There is magic in the night when pumpkins glow by moonlight.",
            "On Halloween you get to become anything that you want to be.",
            "Every day is Halloween isn't it? For some of us.",
            "Ghosts and goblins come to play on October’s final day!",
            "There is something haunting in the light of the moon.",
            "Anyone could see that the wind was a special wind this night, and the darkness took on a special feel because it was All Hallows' Eve.",
            "There are nights when the wolves are silent and only the moon howls.",
            "May your candy supply last you well into the Christmas season.",
            "During the day, I don't believe in ghosts. At night, I'm a little more open-minded.",
            "A candy a day keeps the monsters away.",
            "Trick or treat, bag of sweets, ghosts are walking down the street.",
            "Whatever you do, don't fall asleep.",
            "Have you come to sing pumpkin carols?",
            "It's Halloween, everyone's entitled to one good scare.",
            "Each year, the Great Pumpkin rises out of the pumpkin patch that he thinks is the most sincere.",
            "Where there is no imagination there is no horror.",
            "Deep into the darkness peering, long I stood there, wondering, fearing, doubting, dreaming dreams no mortal ever dared to dream before.",
            "The blood is life.",
            "Happy Haunting!",
            "Stop in for a spell.",
            "Please park all brooms at the door.",
            "Be sure to holler trick or treat!",
            "Find the thing that must be read, lest your heart be filled with dread.",
            "It's as much fun to scare as to be scared.",
            "Darkness falls across the land, The Midnight Hour is close at hand.",
            "The universe is full of magical things patiently waiting for out wits to grow sharper.",
            "Do you believe in destiny? That even the powers of time can be altered for a single purpose?",
            "Halloween is opportunity to be really creative.",
            "When the witches went waltzing.",
            "Never trust anything that can think for itself if you can't see where it keeps its brain.",
            "I would like, if I may, to take you on a strange journey.",
            "Halloween is not only about putting on a costume, but it's about finding the imagination and costume within ourselves.",
            "If human beings had genuine courage, they'd wear their costumes every day of the year, not just on Halloween.",
            "On Halloween, witches come true; wild ghosts escape from dreams. Each monster dances in the park.",
            "Shadows mutter, mist replies; darkness purrs as midnight sighs.",
            "Magic is really very simple, all you've got to do is want something and then let yourself have it.",
            "I'll stop wearing black when they make a darker color.",
            "The moon has awoken with the sleep of the sun, the light has been broken; the spell has begun.",
            "She used to tell me that a full moon was when mysterious things happen and wishes come true.",
            "The dead rise again, bats fly, terror strikes and screams echo, for tonight it's Halloween.",
            "There is a child in every one of us who is still a trick-or-treater looking for a brightly-lit front porch.",
            "Be afraid, be very afraid.",
            "The farther we've gotten from the magic and mystery of our past, the more we've come to need Halloween."
        ]
        self.wordstext = [
            "𝕒𝕓𝕠𝕞𝕚𝕟𝕒𝕓𝕝𝕖",
            "𝕒𝕟𝕔𝕚𝕖𝕟𝕥",
            "𝕓𝕖𝕨𝕚𝕥𝕔𝕙𝕚𝕟𝕘",
            "𝕓𝕝𝕠𝕠𝕕𝕔𝕦𝕣𝕕𝕝𝕚𝕟𝕘",
            "𝕓𝕝𝕠𝕠𝕕𝕪",
            "𝕔𝕙𝕚𝕝𝕝𝕚𝕟𝕘",
            "𝕔𝕠𝕤𝕥𝕦𝕞𝕖𝕕",
            "𝕔𝕠𝕨𝕒𝕣𝕕𝕝𝕪",
            "𝕔𝕣𝕖𝕖𝕡𝕖𝕕 𝕠𝕦𝕥",
            "𝕔𝕣𝕖𝕖𝕡𝕪",
            "𝕕𝕒𝕣𝕜",
            "𝕕𝕖𝕒𝕕𝕝𝕪",
            "𝕕𝕖𝕔𝕒𝕪𝕖𝕕",
            "𝕕𝕖𝕧𝕚𝕝𝕚𝕤𝕙",
            "𝕕𝕚𝕣𝕖",
            "𝕕𝕚𝕣𝕥𝕪",
            "𝕕𝕚𝕤𝕖𝕞𝕓𝕠𝕕𝕚𝕖𝕕",
            "𝕕𝕚𝕤𝕘𝕦𝕚𝕤𝕖𝕕",
            "𝕕𝕣𝕖𝕒𝕕𝕗𝕦𝕝",
            "𝕕𝕣𝕖𝕤𝕤𝕖𝕕-𝕦𝕡",
            "𝕖𝕖𝕣𝕚𝕖",
            "𝕖𝕟𝕔𝕙𝕒𝕟𝕥𝕖𝕕",
            "𝕖𝕧𝕚𝕝",
            "𝕗𝕚𝕖𝕣𝕪",
            "𝕗𝕣𝕚𝕘𝕙𝕥𝕖𝕟𝕚𝕟𝕘",
            "𝕗𝕣𝕚𝕘𝕙𝕥𝕗𝕦𝕝",
            "𝕗𝕦𝕟",
            "𝕘𝕙𝕠𝕤𝕥𝕝𝕪",
            "𝕘𝕙𝕠𝕦𝕝𝕚𝕤𝕙",
            "𝕙𝕒𝕦𝕟𝕥𝕖𝕕",
            "𝕙𝕠𝕨𝕝𝕚𝕟𝕘",
            "𝕝𝕦𝕣𝕜𝕚𝕟𝕘",
            "𝕞𝕒𝕘𝕚𝕔𝕒𝕝",
            "𝕞𝕒𝕤𝕜𝕖𝕕",
            "𝕞𝕠𝕟𝕤𝕥𝕣𝕠𝕦𝕤",
            "𝕞𝕠𝕠𝕟𝕝𝕚𝕥",
            "𝕞𝕠𝕣𝕠𝕤𝕖",
            "𝕞𝕠𝕣𝕥𝕒𝕝",
            "𝕞𝕦𝕞𝕞𝕚𝕗𝕚𝕖𝕕",
            "𝕞𝕪𝕤𝕥𝕖𝕣𝕚𝕠𝕦𝕤",
            "𝕞𝕪𝕤𝕥𝕚𝕔𝕒𝕝",
            "𝕟𝕚𝕘𝕙𝕥𝕥𝕚𝕞𝕖",
            "𝕟𝕠𝕔𝕥𝕦𝕣𝕟𝕒𝕝",
            "𝕠𝕞𝕚𝕟𝕠𝕦𝕤",
            "𝕠𝕣𝕒𝕟𝕘𝕖",
            "𝕡𝕠𝕤𝕤𝕖𝕤𝕤𝕖𝕕",
            "𝕤𝕔𝕒𝕣𝕖𝕕",
            "𝕤𝕔𝕒𝕣𝕪",
            "𝕤𝕔𝕣𝕖𝕒𝕞𝕚𝕟𝕘",
            "𝕤𝕙𝕒𝕕𝕠𝕨𝕪",
            "𝕤𝕙𝕣𝕚𝕝𝕝",
            "𝕤𝕡𝕖𝕝𝕝-𝕓𝕚𝕟𝕕𝕚𝕟𝕘",
            "𝕤𝕡𝕠𝕠𝕜𝕒𝕝𝕚𝕔𝕚𝕠𝕦𝕤",
            "𝕤𝕡𝕠𝕠𝕜𝕖𝕕",
            "𝕤𝕡𝕠𝕠𝕜𝕪",
            "𝕤𝕢𝕦𝕖𝕒𝕞𝕚𝕤𝕙",
            "𝕤𝕥𝕠𝕣𝕞𝕪",
            "𝕤𝕥𝕣𝕒𝕟𝕘𝕖",
            "𝕥𝕖𝕣𝕣𝕚𝕗𝕚𝕖𝕕",
            "𝕦𝕟𝕕𝕖𝕒𝕕",
            "𝕨𝕚𝕔𝕜𝕖𝕕",
            "𝕨𝕚𝕝𝕕",
            "𝕓𝕒𝕥",
            "𝕤𝕡𝕚𝕣𝕚𝕥",
            "𝕔𝕒𝕤𝕜𝕖𝕥",
            "𝕔𝕠𝕗𝕗𝕚𝕟",
            "𝕔𝕦𝕣𝕤𝕖𝕕",
            "𝕡𝕦𝕞𝕡𝕜𝕚𝕟",
            "𝕤𝕜𝕦𝕝𝕝",
            "𝕤𝕡𝕚𝕕𝕖𝕣",
            "𝕔𝕒𝕡𝕖",
            "𝕨𝕖𝕣𝕖𝕨𝕠𝕝𝕗",
            "𝕨𝕚𝕫𝕒𝕣𝕕",
            "𝕫𝕠𝕞𝕓𝕚𝕖",
            "𝕠𝕞𝕚𝕟𝕠𝕦𝕤",
            "𝕠𝕔𝕥𝕠𝕓𝕖𝕣",
            "𝕔𝕣𝕠𝕨",
            "𝕥𝕒𝕣𝕒𝕟𝕥𝕦𝕝𝕒",
            "𝕡𝕚𝕩𝕚𝕖",
            "𝕧𝕒𝕞𝕡𝕚𝕣𝕖",
            "𝕘𝕠𝕠𝕕𝕚𝕖𝕤",
            "𝕞𝕒𝕜𝕖𝕦𝕡",
            "𝕤𝕙𝕒𝕡𝕖𝕤𝕙𝕚𝕗𝕥𝕖𝕣",
            "𝕙𝕠𝕣𝕣𝕚𝕗𝕪",
            "𝕓𝕒𝕟𝕤𝕙𝕖𝕖",   
            "𝕓𝕝𝕒𝕔𝕜",   
            "𝕓𝕝𝕠𝕠𝕕𝕔𝕦𝕣𝕕𝕝𝕚𝕟𝕘",    
            "𝕓𝕠𝕘𝕖𝕪𝕞𝕒𝕟",    
            "𝕓𝕣𝕠𝕠𝕞",    
            "𝕔𝕒𝕟𝕕𝕝𝕖",    
            "𝕔𝕒𝕦𝕝𝕕𝕣𝕠𝕟",    
            "𝕔𝕖𝕞𝕖𝕥𝕖𝕣𝕪",    
            "𝕔𝕝𝕠𝕒𝕜",    
            "𝕗𝕒𝕞𝕚𝕝𝕚𝕒𝕣",    
            "𝕗𝕒𝕟𝕘𝕤",    
            "𝕗𝕚𝕖𝕟𝕕",    
            "𝕘𝕠𝕓𝕝𝕚𝕟",   
            "𝔾𝕣𝕚𝕞 ℝ𝕖𝕒𝕡𝕖𝕣",    
            "𝕝𝕒𝕟𝕥𝕖𝕣𝕟",    
            "𝕟𝕚𝕘𝕙𝕥𝕞𝕒𝕣𝕖",    
            "𝕡𝕙𝕒𝕟𝕥𝕠𝕞",    
            "𝕤𝕔𝕪𝕥𝕙𝕖",    
            "𝕤𝕙𝕠𝕔𝕜",    
            "𝕤𝕨𝕖𝕖𝕥𝕤",    
            "𝕨𝕖𝕓"
        ]
        self.words = [
            "abominable",
            "ancient",
            "bewitching",
            "bloodcurdling",
            "bloody",
            "chilling",
            "costumed",
            "cowardly",
            "creeped out",
            "creepy",
            "dark",
            "deadly",
            "decayed",
            "devilish",
            "dire",
            "dirty",
            "disembodied",
            "disguised",
            "dreadful",
            "dressed-up",
            "eerie",
            "enchanted",
            "evil",
            "fiery",
            "frightening",
            "frightful",
            "fun",
            "ghostly",
            "ghoulish",
            "haunted",
            "howling",
            "lurking",
            "magical",
            "masked",
            "monstrous",
            "moonlit",
            "morose",
            "mortal",
            "mummified",
            "mysterious",
            "mystical",
            "nighttime",
            "nocturnal",
            "ominous",
            "orange",
            "possessed",
            "scared",
            "scary",
            "screaming",
            "shadowy",
            "shrill",
            "spell-binding",
            "spookalicious",
            "spooked",
            "spooky",
            "squeamish",
            "stormy",
            "strange",
            "terrified",
            "undead",  
            "wicked",
            "wild",
            "bat",
            "spirit",
            "casket",
            "coffin",
            "cursed",
            "pumpkin",
            "skull",
            "spider",
            "cape",
            "werewolf",
            "wizard",
            "zombie",
            "ominous",
            "october",
            "crow",
            "tarantula",
            "pixie",
            "vampire",
            "goodies",
            "makeup",
            "shapeshifter",
            "horrify",
            "banshee",
            "black",
            "bloodcurdling",
            "bogeyman",
            "broom",
            "candle",
            "cauldron",
            "cemetery",
            "cloak",
            "familiar",
            "fangs",
            "fiend",
            "goblin",
            "Grim Reaper",
            "lantern",
            "nightmare",
            "phantom",
            "scythe",
            "shock",
            "sweets",
            "web"
        ]
        self.active = []
        self.disabled = {}
        self.slowmode = []
    
    @commands.Cog.listener()
    async def on_ready(self):
        ref = db.reference("/",app = firebase_admin._apps['settings'])
        data = ref.get()

        for guild,guilddata in data.items():
            halloween = guilddata.get("halloween",None)
            if halloween:
                if halloween.get("enabled",False):
                    self.active.append(int(guild))
                disabled = halloween.get("disabled",[])
                build = []
                for channel in disabled:
                    build.append(int(channel))
                if len(build) > 0:
                    self.disabled[int(guild)] = build

        print('Halloween Cog Loaded, and channels cached.')
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def halloweencache(self,ctx):
        await ctx.send(self.active)
        await ctx.send(self.disabled)
        await ctx.send(f"{len(self.phrases)} | {len(self.phrasestext)}")
        await ctx.send(f"{len(self.words)} | {len(self.wordstext)}")

    async def add_pumpkin(self,guild,user,amount):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        data = ref.child("halloween").child(str(guild.id)).child(str(user.id)).get() or 0
        ref.child("halloween").child(str(guild.id)).child(str(user.id)).set(data + amount)
        return True
        
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.guild.id not in self.active or message.author.bot or message.channel.id in self.disabled.get(message.guild.id,[]):
            return

        chance = random.randint(1,100)
        if message.guild.id == 798822518571925575:
            try:
                author = message.author
                role = message.guild.get_role(902509950901829652)
                if role in author.roles:
                    if not chance <= 3:
                        return
                elif not chance<= 2:
                    return
            except:
                pass
        elif not chance <= 2:
            return

        event = self.choices[random.randint(0,len(self.choices)-1)]

        if event == "button":
            title = self.titles[random.randint(0,len(self.titles))-1]
            embed = discord.Embed(title = title,description = "Be the first to click the button to claim!",color = discord.Color.orange())
            message = await message.channel.send(embed = embed,components = [Button(label = "Claim Pumpkins",style = 4)])

            def check(i):
                if i.message.id == message.id:
                    return True
                else:
                    return False

            try:
                interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
            except asyncio.TimeoutError:
                return await message.edit("The drop timed out. Are yall dead?",embed = embed, components = [Button(label = "Claim pumpkin",style = 4,disabled = True)])
                
            await message.edit("Drop Claimed!",embed = embed, components = [Button(label = "Claim Pumpkins",style = 4,disabled = True)])

            amount = random.randint(50,100)
            embed = discord.Embed(description = f"{interaction.user.mention} Claimed **{amount} {self.pumpkin}**",color = discord.Color.green())
            embed.set_footer(text = "Use [prefix]pumpkin to see how much pumpkins you have!")
            await self.add_pumpkin(message.guild,interaction.user,amount)
            return await interaction.respond(embed = embed,ephemeral = False)
        elif event == "phrase":
            title = self.titles[random.randint(0,len(self.titles))-1]
            num = random.randint(0,len(self.phrases)-1)
            phrase = self.phrases[num]
            phrasetext = self.phrasestext[num]

            embed = discord.Embed(title = title,description = f"Type the phrase\n\n{phrasetext}\n\nto pick it up!",color = discord.Color.orange())
            message = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == message.channel.id and i.content == phrasetext:
                    return True
                if i.channel.id == message.channel.id and i.content == phrase:
                    return True
                else:
                    return False
            
            while True:
                try:
                    message = await self.client.wait_for("message",timeout = 30.0,check = check)
                except asyncio.TimeoutError:
                    return await message.edit("The drop timed out. Are yall dead?")

                if message.content == phrasetext:
                    await message.reply("You cheating mf, nice try.")
                else:
                    break
            
            amount = random.randint(300,500)
            embed = discord.Embed(description = f"{message.author.mention} Claimed **{amount} {self.pumpkin}**",color = discord.Color.green())
            embed.set_footer(text = "Use [prefix]pumpkin to see how much pumpkins you have!")
            await self.add_pumpkin(message.guild,message.author,amount)
            await message.reply(embed = embed)
        elif event == "word":
            title = self.titles[random.randint(0,len(self.titles))-1]
            num = random.randint(0,len(self.words)-1)
            word = self.words[num]
            wordtext = self.wordstext[num]

            embed = discord.Embed(title = title,description = f"Type the word\n\n{wordtext}\n\nto pick it up!",color = discord.Color.orange())
            message = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == message.channel.id and i.content == wordtext:
                    return True
                if i.channel.id == message.channel.id and i.content == word:
                    return True
                else:
                    return False

            while True:
                try:
                    message = await self.client.wait_for("message",timeout = 30.0,check = check)
                except asyncio.TimeoutError:
                    return await message.edit("The drop timed out. Are yall dead?")

                if message.content == wordtext:
                    await message.reply("You cheating mf, nice try.")
                else:
                    break
            
            amount = random.randint(100,200)
            embed = discord.Embed(description = f"{message.author.mention} Claimed **{amount} {self.pumpkin}**",color = discord.Color.green())
            embed.set_footer(text = "Use [prefix]pumpkin to see how much pumpkins you have!")
            await self.add_pumpkin(message.guild,message.author,amount)
            await message.reply(embed = embed)
        elif event == "unscramble":
            title = self.titles[random.randint(0,len(self.titles))-1]
            word = self.words[random.randint(0,len(self.words)-1)]
            scrambled = list(word)
            random.shuffle(scrambled)
            scrambled = ''.join(scrambled)

            embed = discord.Embed(title = title,description = f"Unscramble\n\n{scrambled}\n\nto pick it up!",color = discord.Color.orange())
            message = await message.channel.send(embed = embed)

            def check(i):
                if i.channel.id == message.channel.id and i.content == word:
                    return True
                else:
                    return False
            
            try:
                message = await self.client.wait_for("message",timeout = 30.0,check = check)
            except asyncio.TimeoutError:
                return await message.edit("The drop timed out. Are yall dead?")
            
            amount = random.randint(300,600)
            embed = discord.Embed(description = f"{message.author.mention} Claimed **{amount} {self.pumpkin}**",color = discord.Color.green())
            embed.set_footer(text = "Use [prefix]pumpkin to see how much pumpkins you have!")
            await self.add_pumpkin(message.guild,message.author,amount)
            await message.reply(embed = embed)
        elif event == "boss":
            type = random.randint(0,1000)

            if type <= 10:
                type = "legendary"
                title = "🟨 Lengendary BOSS!"
                description = "Jeez this thing has a lot of health! Take it down to grab it's pumpkin!"
                footer = "Kill the boss to receieve 10,000 pumpkins!! This boss has a 1% Chance of Spawning."
                multiplier = 100
                final = 10000
                health = 2000
            elif type <= 110:
                type = "epic"
                title = "🟪 Epic Boss!"
                description = "Nice, it has pumpkin. Hit the button to grab it's pumpkin!"
                footer = "Kill the boss to receieve 2,000 pumpkins! This boss has a 10% Chance of Spawning."
                multiplier = 20
                final = 2000
                health = 400
            elif type <= 310:
                type = "rare"
                title = "🟦 Rare Boss!"
                description = "Not quite the rarest boss, but it still has pumpkin! Let's go for it."
                footer = "Kill the boss to receieve 500 pumpkins! This boss has a 20% Chance of Spawning."
                multiplier = 5
                final = 500
                health = 200
            elif type <= 610:
                type = "uncommon"
                title = "🟩 Uncommon Boss"
                description = "Not quite the rarest boss, but it still has pumpkin! Let's go for it."
                footer = "Kill the boss to receieve 100 pumpkins! This boss has a 30% Chance of Spawning."
                multiplier = 1
                final = 100
                health = 150
            else:
                type = "common"
                title = "⬜ Common Boss"
                description = "Might as well take a shot at this, it's free pumpkin."
                footer = "Kill the boss to receieve 50 pumpkins! This boss has a 39% Chance of spawning"
                multiplier = 0.5
                final = 50
                health = 100
            
            embed = discord.Embed(title = title,description = description,color = discord.Color.dark_orange())
            embed.set_footer(text = footer)
            embed.add_field(name = "Health",value = f"{health}/{health}")
            current = health
            message = await message.channel.send(embed = embed,components = [Button(label = "Hit Boss",style = 4)])

            def check(i):
                if i.message.id == message.id:
                    return True
                else:
                    return False

            hitters = {}
            while True:
                try:
                    try:
                        interaction = await self.client.wait_for("button_click", timeout = 30.0,check = check)
                    except asyncio.TimeoutError:
                        return await message.edit("The boss ran. Are yall dead?",embed = embed, components = [Button(label = "Hit Boss",style = 4,disabled = True)])

                    kick = random.randint(5,30)
                    current -= kick

                    if current <= 0:
                        current = 0
                        finalkick = interaction.user
                        embed.clear_fields()
                        embed.add_field(name = "Health",value = f"{current}/{health}")
                        await message.edit(embed = embed)
                        await interaction.respond(type = 6)
                        hitters[interaction.user] = hitters.get(interaction.user,0) + 0
                        await message.edit("The boss was defeated!",embed = embed, components = [Button(label = "Hit Boss",style = 4,disabled = True)])
                        break
                    
                    embed.clear_fields()
                    embed.add_field(name = "Health",value = f"{current}/{health}")
                    await message.edit(embed = embed)
                    await interaction.respond(type = 6)
                    hitters[interaction.user] = hitters.get(interaction.user,0) + kick
                except:
                    pass
            
            pot = len(hitters) * 100 * multiplier
            description = ""
            for hitter,kicked in hitters.items():
                if hitter == finalkick:
                    given = int(final + pot * (kicked/health))
                    msg = f"**{hitter.name}** got the final hit! They got **{given} {self.pumpkin}**\n"
                    await self.add_pumpkin(message.guild,hitter,given)
                else:
                    given = int(pot * (kicked/health))
                    msg = f"**{hitter.name}** got **{given} {self.pumpkin}**\n"
                    await self.add_pumpkin(message.guild,hitter,given)
            
                description += msg
            embed = discord.Embed(description = description,color = discord.Color.dark_orange())
            await message.reply(embed = embed)
            
    @commands.command(help = "pumpkin [user]",description = "Shows the amount of pumpkins you or another user has.")
    async def pumpkin(self,ctx,user:discord.Member = None):
        user = user or ctx.author
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        data = ref.child("halloween").child(str(ctx.guild.id)).child(str(user.id)).get() or 0

        embed = discord.Embed(title = f"{user.name}'s pumpkin",description = f"`{data}` {self.pumpkin}")
        await ctx.reply(embed = embed)

    @commands.command(help = "pumpkinleaderboard",description = "Who has most pumpkins in the server?")
    async def pumpkinleaderboard(self,ctx):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        log = ref.child("halloween").child(str(ctx.guild.id)).get() 
        if log:
            users,log =  sorted(log, key=log.get, reverse=True) , log
        else:
            users,log = {},{}

        build = ""
        count = 1
        for user in users:
            amount = log[user]
            build += f"{count}. <@{user}>: `{amount}` pumpkin {self.pumpkin}\n"
            count += 1

            if count >= 11:
                break

        embed = discord.Embed(title = f"Leaderboard for {ctx.guild.name} Halloween Event",description = build,color = discord.Color.random())
        embed.timestamp = datetime.datetime.utcnow()

        await ctx.reply(embed = embed)

    @commands.command(help = "givepumpkin <amount> <user>",description = "Give pumpkin to other people.")
    async def givepumpkin(self,ctx,amount:float,user:discord.Member):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        amount = int(amount)
        if amount <= 0:
            embed = discord.Embed(description = f"You need to give out a positive amount, don't try to break me.",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        giver = ref.child("halloween").child(str(ctx.guild.id)).child(str(ctx.author.id)).get() or 0

        if giver <= amount:
            embed = discord.Embed(description = f"You only have `{giver}`{self.pumpkin}, how are you planning to give out `{amount}`?",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        giver -= amount
        ref.child("halloween").child(str(ctx.guild.id)).child(str(ctx.author.id)).set(giver)
        receiever = ref.child("halloween").child(str(ctx.guild.id)).child(str(user.id)).get() or 0
        receiever += amount
        ref.child("halloween").child(str(ctx.guild.id)).child(str(user.id)).set(receiever)

        embed = discord.Embed(description = f"{ctx.author.mention}, you gave {user.mention} `{amount}`{self.pumpkin}.\nYou now have `{giver}`{self.pumpkin} and they have `{receiever}`{self.pumpkin}")
        await ctx.reply(embed = embed)
    
    @commands.command(help = "agivepumpkin <amount> <user>",description = "As an admin, give candy to someone. Basically god mode.")
    @commands.has_permissions(administrator= True)
    async def agivepumpkin(self,ctx,amount:float,user:discord.Member):
        ref = db.reference("/",app = firebase_admin._apps['elead'])
        amount = int(amount)
        if amount <= 0:
            embed = discord.Embed(description = f"You need to give out a positive amount, don't try to break me.",color = discord.Color.red())
            return await ctx.reply(embed = embed)

        receiever = ref.child("halloween").child(str(ctx.guild.id)).child(str(user.id)).get() or 0
        receiever += amount
        ref.child("halloween").child(str(ctx.guild.id)).child(str(user.id)).set(receiever)

        embed = discord.Embed(description = f"{ctx.author.mention}, you generated and gave {user.mention} `{amount}`{self.pumpkin}.\nThey have `{receiever}`{self.pumpkin}")
        await ctx.reply(embed = embed)

    @commands.command(help = "pumpkintoggle <enable or disable>",description = "Allow or disable drops in your server.")
    @commands.has_permissions(administrator = True)
    async def pumpkintoggle(self,ctx,choice):
        if choice.lower() == 'enable':
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            ref.child(str(ctx.guild.id)).child("halloween").child("enabled").set(True)
            self.active.append(ctx.guild.id)
            embed = discord.Embed(description = f"Candy drops are enabled guild wide!",color = discord.Color.green())
            embed.set_footer(text = "Disable drops in a channel with [prefix]dropsdisable")
            return await ctx.reply(embed = embed)
        if choice.lower() == "disable" and ctx.guild.id in self.active:
            ref = db.reference("/",app = firebase_admin._apps['settings'])
            ref.child(str(ctx.guild.id)).child("halloween").child("enabled").set(False)
            self.active.remove(ctx.guild.id)
            embed = discord.Embed(description = f"Candy drops are disabled guild wide!",color = discord.Color.green())
            return await ctx.reply(embed = embed)
        elif choice.lower() == "disable":
            embed = discord.Embed(description = f"Candy drops are not enabled here!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        
        embed = discord.Embed(description = f"You have 2 choices: `enable` or `disable`. Pick one.",color = discord.Color.red())
        return await ctx.reply(embed = embed)

    @commands.command(help = "pumpkindisable [channel]",description = "Disable drops in a channel.")
    @commands.has_permissions(administrator = True)
    async def pumpkindisable(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel

        if channel.id in self.disabled.get(ctx.guild.id,[]):
            embed = discord.Embed(description = f"{channel.mention} already was disabled for drops!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        
        disabled = self.disabled.get(ctx.guild.id,[])
        disabled.append(channel.id)
        self.disabled[ctx.guild.id] = disabled

        ref = db.reference("/",app = firebase_admin._apps['settings'])
        channels = ref.child(str(ctx.guild.id)).child("halloween").child("disabled").get() or []
        channels.append(channel.id)
        ref.child(str(ctx.guild.id)).child("halloween").child("disabled").set(channels)

        embed = discord.Embed(description = f"{channel.mention} is now disabled for pumpkin drops!",color = discord.Color.green())
        return await ctx.reply(embed = embed)

    @commands.command(help = "pumpkinenable [channel]",description = "Removes disable in a channel.")
    @commands.has_permissions(administrator = True)
    async def pumpkinenable(self,ctx,channel:discord.TextChannel = None):
        channel = channel or ctx.channel

        if channel.id not in self.disabled.get(ctx.guild.id,[]):
            embed = discord.Embed(description = f"{channel.mention} already was enabled for drops!",color = discord.Color.red())
            return await ctx.reply(embed = embed)
        
        disabled = self.disabled.get(ctx.guild.id,[])
        disabled.remove(channel.id)
        self.disabled[ctx.guild.id] = disabled

        ref = db.reference("/",app = firebase_admin._apps['settings'])
        channels = ref.child(str(ctx.guild.id)).child("halloween").child("disabled").get() or []
        channels.remove(channel.id)
        ref.child(str(ctx.guild.id)).child("halloween").child("disabled").set(channels)

        embed = discord.Embed(description = f"{channel.mention} is now enabled for pumpkin drops!",color = discord.Color.green())
        return await ctx.reply(embed = embed)



def setup(client):
    client.add_cog(Halloween(client))

    