import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button
import datetime
import math
import firebase_admin
from firebase_admin import db
import random

class Currency(commands.Cog):
    '''
        Currency commands, with the Palm Coins being the main form of exchange.
    '''
    def __init__(self,client):
        self.client = client
        self.palmcoin = "<:PalmCoin:873408317521793044>"
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Currency Cog Loaded.')

    async def change_coins(self,ctx,member,amount):
        ref = db.reference("/",app = firebase_admin._apps['profile'])

        currentbal = ref.child(str(member.id)).child("currency").child("balance").get() or 0

        ref.child(str(member.id)).child("currency").child("balance").set(currentbal + amount)

    async def deposit_coins(self,ctx,member,amount):
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        currentbal = await self.get_balance(ctx,member)
        currentbankbal,bankcapacity = await self.get_bank_info(ctx,member)

        if amount == "all" or amount == "max":
            amount = currentbal 
            if amount + currentbankbal > bankcapacity:
                amount = (bankcapacity - currentbankbal)
        else:
            try:
                amount = int(float(amount))
            except:
                return await ctx.reply("Hey, your input has to be a valid number or amount like `all`.")

        if amount <= 0:
            return await ctx.reply("Hey, that amount has to be greater than 0.")

        if currentbal < amount:
            return await ctx.reply(f"Your amount should be something less than or equal to what you have in your wallet ({self.palmcoin} {'{:,}'.format(currentbal)})")
        elif amount + currentbankbal > bankcapacity:
            return await ctx.reply(f"Your bank cannot hold that much coins! Your bank capacity is {self.palmcoin} {'{:,}'.format(bankcapacity)}")

        ref.child(str(member.id)).child("currency").child("bank").child("balance").set(currentbankbal+amount)
        ref.child(str(member.id)).child("currency").child("balance").set(currentbal-amount)

        await ctx.reply(f"Deposited **{self.palmcoin} {amount}**, current bank balance is **{self.palmcoin} {currentbankbal+amount}**")

    async def withdraw_coins(self,ctx,member,amount):
        ref = db.reference("/",app = firebase_admin._apps['profile'])
        currentbankbal,bankcapacity = await self.get_bank_info(ctx,member)
        currentbal = await self.get_balance(ctx,member)

        if amount == "all" or amount == "max":
            amount = currentbankbal
        else:
            try:
                amount = int(float(amount))
            except:
                return await ctx.reply("Hey, your input has to be a valid number or amount like `all`.")
        
        if amount <= 0:
            return await ctx.reply("Hey, that amount has to be greater than 0.")

        if amount > currentbankbal:
            return await ctx.reply(f"You can only withdraw how much you have ({self.palmcoin} {currentbankbal})")
        
        ref.child(str(member.id)).child("currency").child("bank").child("balance").set(currentbankbal-amount)
        ref.child(str(member.id)).child("currency").child("balance").set(currentbal+amount)
        
        await ctx.reply(f"Withdrawed **{self.palmcoin} {amount}**, current bank balance is **{self.palmcoin} {currentbankbal-amount}**")


    async def get_balance(self,ctx,member):
        ref = db.reference("/",app = firebase_admin._apps['profile'])

        currentbal = ref.child(str(member.id)).child("currency").child("balance").get() or 0

        return currentbal

    async def get_bank_info(self,ctx,member):
        ref = db.reference("/",app = firebase_admin._apps['profile'])

        bankbalance = ref.child(str(member.id)).child("currency").child("bank").child("balance").get() or 0
        bankcapacity = ref.child(str(member.id)).child("currency").child("bank").child("capacity").get() or 0

        return bankbalance,bankcapacity

    async def give_coins(self,ctx,giver,receiver,amount):
        currentbal = await self.get_balance(ctx,giver)
        if amount == "all" or amount == "max":
            amount = currentbal
        else:
            try:
                amount = int(float(amount))
            except:
                return await ctx.reply("Hey, your input has to be a valid number or amount like `all`.")
        
        if amount <= 0:
            return await ctx.reply("Hey, that amount has to be greater than 0.")
        if currentbal < amount:
            return await ctx.reply(f"Hey, you cannot give more money than you have! You currently have {self.palmcoin} {'{:,}'.format(currentbal)}")

        await self.change_coins(ctx,giver,0 - amount)
        await self.change_coins(ctx,receiver,amount)

        return await ctx.reply(f"{giver} You gave {self.palmcoin} {'{:,}'.format(amount)} to {receiver}")

    @commands.command(description = "Beg for a random amount of coins.",help = "beg")
    @commands.cooldown(1, 30,commands.BucketType.user)
    async def beg(self,ctx):
        amount = random.randint(100,2000)

        await self.change_coins(ctx,ctx.author,amount)

        emb = discord.Embed(title = "You begged a little bit",description = f"You received **{amount}** {self.palmcoin}",color = discord.Color.green())

        await ctx.reply(embed = emb)

    @commands.command(aliases = ['bal'],description = "Check your wallet and your bank balance.",help = "balance [member]")
    async def balance(self,ctx,member:discord.Member=None):
        member = member or ctx.author
        balance = await self.get_balance(ctx,member)
        bankbalance,bankcapacity = await self.get_bank_info(ctx,member)
        formattedbankbalance = '{:,}'.format(bankbalance)
        formattedbankcapacity = '{:,}'.format(bankcapacity)
        formattedbal = '{:,}'.format(balance)
        emb = discord.Embed(title = f"{member.name}'s Balance",description = f"**Wallet:** {self.palmcoin} `{formattedbal}`\n**Bank:** {self.palmcoin} `{formattedbankbalance}/{formattedbankcapacity}`")

        if balance <= 50000:
            footer = "Imagine being poor"
        elif balance <= 100000:
            footer = "Still slightly poor"
        elif balance <= 500000:
            footer = "An average person"
        elif balance <= 1000000:
            footer = "A slightly above average person"
        elif balance <= 10000000:
            footer = "Pretty rich balance"
        elif balance <= 100000000:
            footer = "Damn you rich"
        else:
            footer = "Are you hacking???"

        
        emb.set_footer(text = footer)
        emb.timestamp = datetime.datetime.utcnow()
        await ctx.reply(embed = emb)

    @commands.command(aliases = ['dep'],description = "Deposit some of your coins into your bank.",help = "deposit <amount>")
    async def deposit(self,ctx,amount):
        await self.deposit_coins(ctx,ctx.author,amount)

    @commands.command(aliases = ['with'],description = "Withdraw some of the coins from your bank",help = "withdraw <amount>")
    async def withdraw(self,ctx,amount):
        await self.withdraw_coins(ctx,ctx.author,amount)

    @commands.command(aliases = ["share"],description = "Share some of your hard earned coins with a friend",help = "give <amount> <user>")
    async def give(self,ctx,amount,user:discord.Member):
        await self.give_coins(ctx,ctx.author,user,amount)


def setup(client):
    client.add_cog(Currency(client))