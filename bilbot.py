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
RECRUITING_CHANNEL_ID = 1110679408911593664
GUILDS = []

conn = psycopg2.connect(DATABASE_TOKEN, sslmode='require')
cur = conn.cursor()
cur.execute("SELECT guild_name FROM home_guilds")
results = cur.fetchall()
cur.close()
conn.close()

for i in results:
    GUILDS.append(i[0])

# Set up the bot with the proper intents to read message content and reactions
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix="+", intents=intents)

#Slash command to display the current status of guilds
@bot.slash_command(guild_ids=[COUNCIL_GUILD_ID], description="Display the current Council guilds")
async def listguilds(ctx):
    await ctx.response.defer()

    conn = psycopg2.connect(DATABASE_TOKEN, sslmode='require')
    cur = conn.cursor()
    cur.execute("select * from home_guilds order by priority asc")
    guilds = cur.fetchall()
    cur.close()
    conn.close()

    tiers = [[],[],[],[],[]]

    for guild in guilds:
        tiers[guild[1]-1].append(guild)

    responded = False

    for tier in range(1,6):
        message = ""
        if tiers[tier-1] != []:
            for guild in tiers[tier-1]:
                message += "**{0}**\nRecruit Priority: {1}\nCherries: {2}\nNew Guild Status: {3}\n\n".format(guild[0], str(guild[3]), str(guild[2]), str(guild[4]))
            embed = discord.Embed(title = "Tier {} Guilds".format(str(tier)), description = message)
            if not responded:
                await ctx.respond(embed = embed)
                responded = True
            else:
                await ctx.send(embed = embed)

    return

#TODO
#Slash command to begin the recruitment process
@bot.slash_command(guild_ids=[COUNCIL_GUILD_ID], description="Begin the recruitment process")
async def newbie(ctx, newbiename: Option(str, "What is the recruit's name?"), collectionpower: Option(str, "What is the recruit's collection power?")):
    await ctx.response.defer()

    guild = discord.utils.get(bot.guilds, id=COUNCIL_GUILD_ID)
    channel = guild.get_channel(RECRUITING_CHANNEL_ID)
    thread = await channel.create_thread(name="Testing", message=None, auto_archive_duration=None, type=discord.ChannelType.public_thread, reason=None)

    await thread.send("Sending a test message in a thread")

    await ctx.respond("<#{}> has been created".format(str(thread.id)), ephemeral = True)

    return

#Slash command to update a guild's tier
@bot.slash_command(guild_ids=[COUNCIL_GUILD_ID], description="Update a guild's tier")
async def updatetier(ctx, guildname: discord.Option(str, autocomplete = discord.utils.basic_autocomplete(GUILDS)), newtier: Option(int, "What tier should this guild be?")):
    await ctx.response.defer()

    conn = psycopg2.connect(DATABASE_TOKEN, sslmode='require')
    cur = conn.cursor()
    cur.execute("update home_guilds set guild_tier = {0} where guild_name = '{1}'".format(newtier, guildname))
    conn.commit()
    cur.close()
    conn.close()

    embed = discord.Embed(title = "{} Updated".format(guildname), description = "{0} is now a Tier {1} guild".format(guildname, str(newtier)))
    await ctx.respond(embed = embed)

    return

#TODO Slash command to tell bot that a guild accepted a recruit

#TODO Slash command to tell bot that a guild passed on a recruit

#TODO Slash command to manually update update guild's priority

#TODO Slash command to manually update guild's cherries

#TODO Slash command to update guild's newbie status

#TODO Slash command to update tier min/max collection power

#TODO Slash command to add a new guild

bot.run(BOT_TOKEN)