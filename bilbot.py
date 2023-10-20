import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Select
from discord.commands import Option, OptionChoice
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_TOKEN = os.getenv('DATABASE_TOKEN')
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

COUNCIL_GUILD_ID = 1107434690882842645

# Set up the bot with the proper intents to read message content and reactions
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix="+", intents=intents)

#Slash command to display an invocation from a specified project
@bot.slash_command(guild_ids=[COUNCIL_GUILD_ID], description="Display the current Council guilds")
async def listguilds(ctx):
    await ctx.response.defer()

    conn = psycopg2.connect(DATABASE_TOKEN, sslmode='require')
    cur = conn.cursor()
    cur.execute("select * from home_guilds order by priority desc")
    guilds = cur.fetchall()
    cur.close()
    conn.close()

    tiers = [[],[],[],[],[]]

    for guild in guilds:
        tiers[guild[1]-1].append(guild)

    for tier in range(1,6):
        message = ""
        if tiers[tier-1] != []:
            for guild in tiers[tier-1]:
                message += "**{0}**\nRecruit Priority: {1}\nCherries: {2}\nNew Guild Status: {3}\n\n".format(guild[0], str(guild[2]), str(guild[3]), str(guild[4]))
            embed = discord.Embed(title = "Tier {} Guilds".format(str(tier)), description = message)
            await ctx.send(embed = embed)

    return

bot.run(BOT_TOKEN)