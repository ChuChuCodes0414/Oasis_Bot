import discord
from discord.ext import commands
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
            "ππππ£π ππ€ πππππ ππ π₯ππ πππππ₯ π¨πππ π‘π¦ππ‘ππππ€ πππ π¨ ππͺ ππ π ππππππ₯.",
            "ππ βππππ π¨πππ πͺπ π¦ πππ₯ π₯π  ππππ ππ πππͺπ₯ππππ π₯πππ₯ πͺπ π¦ π¨πππ₯ π₯π  ππ.",
            "πΌπ§ππ£πͺ πππͺ ππ€ βππππ π¨πππ ππ€π'π₯ ππ₯? π½π π£ π€π ππ π π π¦π€.",
            "πΎππ π€π₯π€ πππ ππ πππππ€ ππ ππ π₯π  π‘πππͺ π π πππ₯π πππ£βπ€ πππππ πππͺ!",
            "ππππ£π ππ€ π€π πππ₯ππππ πππ¦ππ₯πππ ππ π₯ππ πππππ₯ π π π₯ππ ππ π π.",
            "πΈππͺπ ππ ππ π¦ππ π€ππ π₯πππ₯ π₯ππ π¨πππ π¨ππ€ π π€π‘πππππ π¨πππ π₯πππ€ πππππ₯, πππ π₯ππ πππ£ππππ€π€ π₯π π π π π π π€π‘πππππ ππππ πππππ¦π€π ππ₯ π¨ππ€ πΈππ βππππ π¨π€' πΌπ§π.",
            "ππππ£π ππ£π πππππ₯π€ π¨πππ π₯ππ π¨π ππ§ππ€ ππ£π π€πππππ₯ πππ π πππͺ π₯ππ ππ π π ππ π¨ππ€.",
            "πππͺ πͺπ π¦π£ πππππͺ π€π¦π‘π‘ππͺ πππ€π₯ πͺπ π¦ π¨πππ πππ₯π  π₯ππ βππ£ππ€π₯πππ€ π€πππ€π π.",
            "π»π¦π£πππ π₯ππ πππͺ, π ππ π'π₯ ππππππ§π ππ πππ π€π₯π€. πΈπ₯ πππππ₯, π'π π πππ₯π₯ππ ππ π£π π π‘ππ-ππππππ.",
            "πΈ πππππͺ π πππͺ ππππ‘π€ π₯ππ ππ ππ€π₯ππ£π€ ππ¨ππͺ.",
            "ππ£πππ π π£ π₯π£πππ₯, πππ π π π€π¨πππ₯π€, πππ π€π₯π€ ππ£π π¨ππππππ ππ π¨π π₯ππ π€π₯π£πππ₯.",
            "ππππ₯ππ§ππ£ πͺπ π¦ ππ , ππ π'π₯ ππππ ππ€ππππ‘.",
            "βππ§π πͺπ π¦ ππ ππ π₯π  π€πππ π‘π¦ππ‘πππ πππ£π ππ€?",
            "ππ₯'π€ βππππ π¨πππ, ππ§ππ£πͺπ ππ'π€ πππ₯ππ₯πππ π₯π  π ππ ππ π π π€πππ£π.",
            "πΌπππ πͺπππ£, π₯ππ πΎπ£πππ₯ βπ¦ππ‘πππ π£ππ€ππ€ π π¦π₯ π π π₯ππ π‘π¦ππ‘πππ π‘ππ₯ππ π₯πππ₯ ππ π₯πππππ€ ππ€ π₯ππ ππ π€π₯ π€πππππ£π.",
            "ππππ£π π₯πππ£π ππ€ ππ  ππππππππ₯ππ π π₯πππ£π ππ€ ππ  ππ π£π£π π£.",
            "π»πππ‘ πππ₯π  π₯ππ πππ£ππππ€π€ π‘πππ£πππ, ππ ππ π π€π₯π π π π₯πππ£π, π¨π ππππ£πππ, ππππ£πππ, ππ π¦ππ₯πππ, ππ£ππππππ ππ£ππππ€ ππ  ππ π£π₯ππ ππ§ππ£ πππ£ππ π₯π  ππ£πππ ππππ π£π.",
            "πππ πππ π π ππ€ ππππ.",
            "βππ‘π‘πͺ βππ¦ππ₯πππ!",
            "ππ₯π π‘ ππ ππ π£ π π€π‘πππ.",
            "βππππ€π π‘ππ£π πππ ππ£π π ππ€ ππ₯ π₯ππ ππ π π£.",
            "πΉπ π€π¦π£π π₯π  ππ ππππ£ π₯π£πππ π π£ π₯π£πππ₯!",

            "π½πππ π₯ππ π₯ππππ π₯πππ₯ ππ¦π€π₯ ππ π£πππ, πππ€π₯ πͺπ π¦π£ ππππ£π₯ ππ ππππππ π¨ππ₯π ππ£πππ.",            
            "ππ₯'π€ ππ€ ππ¦ππ ππ¦π π₯π  π€πππ£π ππ€ π₯π  ππ π€πππ£ππ.",            
            "π»ππ£ππππ€π€ πππππ€ πππ£π π€π€ π₯ππ ππππ, πππ ππππππππ₯ βπ π¦π£ ππ€ πππ π€π ππ₯ ππππ.",            
            "πππ π¦πππ§ππ£π€π ππ€ ππ¦ππ π π πππππππ π₯πππππ€ π‘ππ₯ππππ₯ππͺ π¨πππ₯πππ ππ π£ π π¦π₯ π¨ππ₯π€ π₯π  ππ£π π¨ π€πππ£π‘ππ£.",            
            "π»π  πͺπ π¦ ππππππ§π ππ πππ€π₯πππͺ? ππππ₯ ππ§ππ π₯ππ π‘π π¨ππ£π€ π π π₯πππ πππ ππ πππ₯ππ£ππ ππ π£ π π€πππππ π‘π¦π£π‘π π€π?",            
            "βππππ π¨πππ ππ€ π π‘π‘π π£π₯π¦πππ₯πͺ π₯π  ππ π£πππππͺ ππ£πππ₯ππ§π.",            "ππππ π₯ππ π¨ππ₯ππππ€ π¨πππ₯ π¨πππ₯π«πππ.",            
            "βππ§ππ£ π₯π£π¦π€π₯ πππͺπ₯ππππ π₯πππ₯ πππ π₯ππππ ππ π£ ππ₯π€πππ ππ πͺπ π¦ πππ'π₯ π€ππ π¨πππ£π ππ₯ ππππ‘π€ ππ₯π€ ππ£πππ.",            
            "π π¨π π¦ππ ππππ, ππ π πππͺ, π₯π  π₯πππ πͺπ π¦ π π π π€π₯π£ππππ ππ π¦π£πππͺ.",            
            "βππππ π¨πππ ππ€ ππ π₯ π πππͺ πππ π¦π₯ π‘π¦π₯π₯πππ π π π ππ π€π₯π¦ππ, ππ¦π₯ ππ₯'π€ πππ π¦π₯ πππππππ π₯ππ ππππππππ₯ππ π πππ ππ π€π₯π¦ππ π¨ππ₯πππ π π¦π£π€πππ§ππ€.",            
            "ππ ππ¦πππ ππππππ€ πππ ππππ¦πππ ππ π¦π£πππ, π₯πππͺ'π π¨πππ£ π₯ππππ£ ππ π€π₯π¦πππ€ ππ§ππ£πͺ πππͺ π π π₯ππ πͺπππ£, ππ π₯ ππ¦π€π₯ π π βππππ π¨πππ.",            
            "ππ βππππ π¨πππ, π¨ππ₯ππππ€ ππ ππ π₯π£π¦π; π¨πππ πππ π€π₯π€ ππ€πππ‘π ππ£π π ππ£ππππ€. πΌπππ ππ ππ€π₯ππ£ ππππππ€ ππ π₯ππ π‘ππ£π.",            
            "πππππ π¨π€ ππ¦π₯π₯ππ£, πππ€π₯ π£ππ‘ππππ€; πππ£ππππ€π€ π‘π¦π£π£π€ ππ€ ππππππππ₯ π€ππππ€.",            
            "πππππ ππ€ π£πππππͺ π§ππ£πͺ π€πππ‘ππ, πππ πͺπ π¦'π§π ππ π₯ π₯π  ππ  ππ€ π¨πππ₯ π€π πππ₯ππππ πππ π₯πππ πππ₯ πͺπ π¦π£π€πππ πππ§π ππ₯.",            
            "π'ππ π€π₯π π‘ π¨πππ£πππ πππππ π¨πππ π₯πππͺ ππππ π πππ£πππ£ ππ ππ π£.",            
            "πππ ππ π π πππ€ ππ¨π πππ π¨ππ₯π π₯ππ π€ππππ‘ π π π₯ππ π€π¦π, π₯ππ πππππ₯ πππ€ ππππ ππ£π πππ; π₯ππ π€π‘πππ πππ€ ππππ¦π.",            
            "πππ π¦π€ππ π₯π  π₯πππ ππ π₯πππ₯ π ππ¦ππ ππ π π π¨ππ€ π¨πππ ππͺπ€π₯ππ£ππ π¦π€ π₯πππππ€ πππ‘π‘ππ πππ π¨ππ€πππ€ ππ ππ π₯π£π¦π.",            
            "πππ ππππ π£ππ€π πππππ, πππ₯π€ πππͺ, π₯ππ£π£π π£ π€π₯π£ππππ€ πππ π€ππ£ππππ€ ππππ , ππ π£ π₯π πππππ₯ ππ₯'π€ βππππ π¨πππ.",            
            "ππππ£π ππ€ π πππππ ππ ππ§ππ£πͺ π ππ π π π¦π€ π¨ππ  ππ€ π€π₯πππ π π₯π£πππ-π π£-π₯π£πππ₯ππ£ ππ π ππππ ππ π£ π ππ£ππππ₯ππͺ-πππ₯ ππ£π ππ₯ π‘π π£ππ.",            
            "πΉπ πππ£πππ, ππ π§ππ£πͺ πππ£πππ.",            
            "πππ πππ£π₯πππ£ π¨π'π§π ππ π₯π₯ππ ππ£π π π₯ππ πππππ πππ ππͺπ€π₯ππ£πͺ π π π π¦π£ π‘ππ€π₯, π₯ππ ππ π£π π¨π'π§π ππ ππ π₯π  ππππ βππππ π¨πππ."
        ]
        self.phrases = [
            "There is magic in the night when pumpkins glow by moonlight.",
            "On Halloween you get to become anything that you want to be.",
            "Every day is Halloween isn't it? For some of us.",
            "Ghosts and goblins come to play on Octoberβs final day!",
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
            "πππ πππππππ",
            "πππππππ₯",
            "πππ¨ππ₯πππππ",
            "πππ π πππ¦π£πππππ",
            "πππ π ππͺ",
            "ππππππππ",
            "ππ π€π₯π¦πππ",
            "ππ π¨ππ£πππͺ",
            "ππ£πππ‘ππ π π¦π₯",
            "ππ£πππ‘πͺ",
            "πππ£π",
            "ππππππͺ",
            "πππππͺππ",
            "πππ§ππππ€π",
            "πππ£π",
            "πππ£π₯πͺ",
            "πππ€ππππ ππππ",
            "πππ€ππ¦ππ€ππ",
            "ππ£πππππ¦π",
            "ππ£ππ€π€ππ-π¦π‘",
            "πππ£ππ",
            "πππππππ₯ππ",
            "ππ§ππ",
            "ππππ£πͺ",
            "ππ£ππππ₯πππππ",
            "ππ£ππππ₯ππ¦π",
            "ππ¦π",
            "πππ π€π₯ππͺ",
            "πππ π¦πππ€π",
            "πππ¦ππ₯ππ",
            "ππ π¨ππππ",
            "ππ¦π£ππππ",
            "πππππππ",
            "πππ€πππ",
            "ππ ππ€π₯π£π π¦π€",
            "ππ π ππππ₯",
            "ππ π£π π€π",
            "ππ π£π₯ππ",
            "ππ¦πππππππ",
            "ππͺπ€π₯ππ£ππ π¦π€",
            "ππͺπ€π₯ππππ",
            "πππππ₯π₯πππ",
            "ππ ππ₯π¦π£πππ",
            "π ππππ π¦π€",
            "π π£ππππ",
            "π‘π π€π€ππ€π€ππ",
            "π€πππ£ππ",
            "π€πππ£πͺ",
            "π€ππ£ππππππ",
            "π€ππππ π¨πͺ",
            "π€ππ£πππ",
            "π€π‘πππ-πππππππ",
            "π€π‘π π πππππππ π¦π€",
            "π€π‘π π πππ",
            "π€π‘π π ππͺ",
            "π€π’π¦πππππ€π",
            "π€π₯π π£ππͺ",
            "π€π₯π£ππππ",
            "π₯ππ£π£πππππ",
            "π¦πππππ",
            "π¨πππππ",
            "π¨πππ",
            "πππ₯",
            "π€π‘ππ£ππ₯",
            "πππ€πππ₯",
            "ππ ππππ",
            "ππ¦π£π€ππ",
            "π‘π¦ππ‘πππ",
            "π€ππ¦ππ",
            "π€π‘ππππ£",
            "πππ‘π",
            "π¨ππ£ππ¨π ππ",
            "π¨ππ«ππ£π",
            "π«π ππππ",
            "π ππππ π¦π€",
            "π ππ₯π πππ£",
            "ππ£π π¨",
            "π₯ππ£πππ₯π¦ππ",
            "π‘ππ©ππ",
            "π§πππ‘ππ£π",
            "ππ π ππππ€",
            "πππππ¦π‘",
            "π€πππ‘ππ€ππππ₯ππ£",
            "ππ π£π£πππͺ",
            "ππππ€πππ",   
            "πππππ",   
            "πππ π πππ¦π£πππππ",    
            "ππ πππͺπππ",    
            "ππ£π π π",    
            "ππππππ",    
            "πππ¦πππ£π π",    
            "πππππ₯ππ£πͺ",    
            "πππ ππ",    
            "ππππππππ£",    
            "πππππ€",    
            "πππππ",    
            "ππ ππππ",   
            "πΎπ£ππ βπππ‘ππ£",    
            "ππππ₯ππ£π",    
            "πππππ₯πππ£π",    
            "π‘ππππ₯π π",    
            "π€ππͺπ₯ππ",    
            "π€ππ ππ",    
            "π€π¨πππ₯π€",    
            "π¨ππ"
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
                title = "π¨ Lengendary BOSS!"
                description = "Jeez this thing has a lot of health! Take it down to grab it's pumpkin!"
                footer = "Kill the boss to receieve 10,000 pumpkins!! This boss has a 1% Chance of Spawning."
                multiplier = 100
                final = 10000
                health = 2000
            elif type <= 110:
                type = "epic"
                title = "πͺ Epic Boss!"
                description = "Nice, it has pumpkin. Hit the button to grab it's pumpkin!"
                footer = "Kill the boss to receieve 2,000 pumpkins! This boss has a 10% Chance of Spawning."
                multiplier = 20
                final = 2000
                health = 400
            elif type <= 310:
                type = "rare"
                title = "π¦ Rare Boss!"
                description = "Not quite the rarest boss, but it still has pumpkin! Let's go for it."
                footer = "Kill the boss to receieve 500 pumpkins! This boss has a 20% Chance of Spawning."
                multiplier = 5
                final = 500
                health = 200
            elif type <= 610:
                type = "uncommon"
                title = "π© Uncommon Boss"
                description = "Not quite the rarest boss, but it still has pumpkin! Let's go for it."
                footer = "Kill the boss to receieve 100 pumpkins! This boss has a 30% Chance of Spawning."
                multiplier = 1
                final = 100
                health = 150
            else:
                type = "common"
                title = "β¬ Common Boss"
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
        embed.timestamp = datetime.datetime.now()

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

    