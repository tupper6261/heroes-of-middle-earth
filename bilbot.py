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
TIER_1_RECRUITER_ROLE_ID = 69
TIER_2_RECRUITER_ROLE_ID = 1158768328278560768
TIER_3_RECRUITER_ROLE_ID = 1158768416438636655
TIER_4_RECRUITER_ROLE_ID = 1158768484071780352
TIER_5_RECRUITER_ROLE_ID = 69
TIER_RECRUITER_IDS = [0,TIER_1_RECRUITER_ROLE_ID, TIER_2_RECRUITER_ROLE_ID, TIER_3_RECRUITER_ROLE_ID, TIER_4_RECRUITER_ROLE_ID, TIER_5_RECRUITER_ROLE_ID]
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

#Slash command to begin the recruitment process
@bot.slash_command(guild_ids=[COUNCIL_GUILD_ID], description="Begin the recruitment process")
async def newbie(ctx, newbiename: Option(str, "What is the recruit's name?"), collectionpower: Option(str, "What is the recruit's collection power?")):
    await ctx.response.defer()

    guild = discord.utils.get(bot.guilds, id=COUNCIL_GUILD_ID)
    channel = guild.get_channel(RECRUITING_CHANNEL_ID)
    thread = await channel.create_thread(name="{0} - {1}".format(newbiename, str(collectionpower)), message=None, auto_archive_duration=None, type=discord.ChannelType.public_thread, reason=None)

    conn = psycopg2.connect(DATABASE_TOKEN, sslmode='require')
    cur = conn.cursor()
    cur.execute("select id from home_tiers where cp_min < {0} and cp_max > {1}".format(collectionpower, collectionpower))
    tier = cur.fetchall()[0][0]
    cur.execute("select * from home_guilds where guild_tier = {0} order by priority asc".format(tier))
    guilds = cur.fetchall()

    cur.close()
    conn.close()

    await thread.send("{0} should be placed in a Tier {1} guild. These have been listed below with their priority ranks. <@&{2}>".format(newbiename, str(tier), str(TIER_RECRUITER_IDS[tier])))

    message = ""
    for guild in guilds:
        message += "**{0}**\nRecruit Priority: {1}\nCherries: {2}\nNew Guild Status: {3}\n\n".format(guild[0], str(guild[3]), str(guild[2]), str(guild[4]))
    embed = discord.Embed(title = "Tier {} Guilds".format(str(tier)), description = message)
    await thread.send(embed = embed)

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

    embed = discord.Embed(title = "{} Updated".format(guildname), description = "{0} is now a Tier {1} guild.".format(guildname, str(newtier)))
    await ctx.respond(embed = embed)

    return

#Slash command to manually update update guild's priority
@bot.slash_command(guild_ids=[COUNCIL_GUILD_ID], description="Update a guild's priority")
async def updatepriority(ctx, guildname: discord.Option(str, autocomplete = discord.utils.basic_autocomplete(GUILDS)), newpriority: Option(int, "What priority should this guild be?")):
    await ctx.response.defer()

    conn = psycopg2.connect(DATABASE_TOKEN, sslmode='require')
    cur = conn.cursor()
    cur.execute("update home_guilds set priority = {0} where guild_name = '{1}'".format(newpriority, guildname))
    conn.commit()
    cur.close()
    conn.close()

    embed = discord.Embed(title = "{} Updated".format(guildname), description = "{0} is now at priority {1}.".format(guildname, str(newpriority)))
    await ctx.respond(embed = embed)

    return

#Slash command to manually update guild's cherries
@bot.slash_command(guild_ids=[COUNCIL_GUILD_ID], description="Update a guild's cherry count")
async def updatecherries(ctx, guildname: discord.Option(str, autocomplete = discord.utils.basic_autocomplete(GUILDS)), newcherrycount: Option(int, "How many cherries should this guild have?")):
    await ctx.response.defer()

    conn = psycopg2.connect(DATABASE_TOKEN, sslmode='require')
    cur = conn.cursor()
    cur.execute("update home_guilds set cherries = {0} where guild_name = '{1}'".format(newcherrycount, guildname))
    conn.commit()
    cur.close()
    conn.close()

    if newcherrycount == 1:
        embed = discord.Embed(title = "{} Updated".format(guildname), description = "{0} now has {1} cherry.".format(guildname, str(newcherrycount)))
    else:
        embed = discord.Embed(title = "{} Updated".format(guildname), description = "{0} now has {1} cherries.".format(guildname, str(newcherrycount)))
    await ctx.respond(embed = embed)

    return

#Slash command to manually update guild's new status
@bot.slash_command(guild_ids=[COUNCIL_GUILD_ID], description="Update a guild's new status")
async def updatenewstatus(ctx, guildname: discord.Option(str, autocomplete = discord.utils.basic_autocomplete(GUILDS)), newstatus: Option(bool, "Should this guild have new status?")):
    await ctx.response.defer()

    conn = psycopg2.connect(DATABASE_TOKEN, sslmode='require')
    cur = conn.cursor()
    cur.execute("update home_guilds set new_status = {0} where guild_name = '{1}'".format(newstatus, guildname))
    conn.commit()
    cur.close()
    conn.close()

    if newstatus:
        embed = discord.Embed(title = "{} Updated".format(guildname), description = "{0} is now considered a new guild.".format(guildname, str(newstatus)))
    else:
        embed = discord.Embed(title = "{} Updated".format(guildname), description = "{0} is now not considered a new guild.".format(guildname, str(newstatus)))

    await ctx.respond(embed = embed)

    return

#TODO Slash command to tell bot that a guild accepted a recruit

#TODO Slash command to tell bot that a guild passed on a recruit

#TODO Slash command to update tier min/max collection power

#TODO Slash command to add a new guild

bot.run(BOT_TOKEN)