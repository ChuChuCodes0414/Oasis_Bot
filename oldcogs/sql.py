import discord
import asyncio
import asyncpg
from discord.ext import commands

class SQL(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('SQL Cog Loaded.')

    @commands.command()
    @commands.is_owner()
    async def sql(self,ctx,*,query):
        async with self.client.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query)
        await ctx.add_reaction("✅")
    
def setup(client):
    client.add_cog(SQL(client))