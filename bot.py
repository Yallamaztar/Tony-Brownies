import discord 
from discord.ext import commands
from discord.ui import View, Select
from discord import option

import os, json
from datetime import datetime
import aiohttp
import uuid
import asyncio
from dotenv import load_dotenv

from src.utils import (
    clear, 
    loadJson, 
    writeJson,
    createEmbed,
    menu,
    initRoles,
    initNottKick
)

# Loading env vars
load_dotenv()
TOKEN   = os.getenv('TOKEN')
BASEURI = os.getenv('BASEURI')
SND_ID  = os.getenv('SND_ID')
FFA_ID  = os.getenv('FFA_ID')
COOKIE  = os.getenv('HEADERS')

# Loading Config, could be done better
with open('src/config.json') as f:
    config = json.load(f)
GUILD_ID: int = config['guild_id']
logs = []

# change to your server role ids
OWNER_ID = 1190796076379283536 
SENIOR_ID = 1190794949353029664
ADMIN_ID = 1190703210973904957

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# On bot ready
@bot.event
async def on_ready():
    await clear()
    await menu(bot)
    await bot.change_presence(activity=discord.Game(name="with myself"), status=discord.Status.idle)
    
# On bot join
@bot.event
async def on_guild_join(guild):
    guildId = guild.id
    guildName = guild.name.capitalize()

    config_data = await loadJson('src/config.json')
    config_data['guild_id'] = guildId

    roles = await initRoles(guild)
    config_data['roles'] = roles

    await writeJson(config_data, 'src/config.json')

    print(f"\n[ \x1B[38;2;245;0;245mJoined\x1b[0m ]")
    print(f"[ \x1B[38;2;245;0;245mServer:\x1b[0m {guildName} ]")
    print(f"[ \x1B[38;2;245;0;245mGuild:\x1b[0m {guildId} ]")

# On bot command
@bot.event
async def on_application_command(ctx: discord.ApplicationContext):
    await clear()
    await menu(bot)
    
    id = str(uuid.uuid4())
    author = ctx.author.mention
    command_name = ctx.command.name
    timestamp = datetime.now().strftime("%Y-%m-%d - %H:%M:%S")
    
    print("\n[ \x1B[38;2;245;0;245mCommand Received\x1b[0m ]")
    print(f"[ \x1B[38;2;245;0;245mID:\x1b[0m {id} ]")
    print(f"[ \x1B[38;2;245;0;245mFrom:\x1b[0m {ctx.author.name} | {ctx.author.mention} ]")
    print(f"[ \x1B[38;2;245;0;245mCommand:\x1b[0m /{ctx.command} ] ")
    print(f"[ \x1B[38;2;245;0;245mTimestamp:\x1b[0m {timestamp} ]")

    data = {
        "id": id,
        "author": author,
        "command": command_name,
        "timestamp": timestamp
    }
    
    logs.append(data)
    await writeJson(logs, 'src/logs.json')
    
    await asyncio.sleep(5)
    await clear()
    await menu(bot)

@bot.event 
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.id != 1233410655055511654:
        return
    else:
        await message.delete()

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext,
                                       error: commands.CheckFailure):
    if (type(error) == commands.MissingAnyRole):
        await ctx.send_response(
            'You do not have the permissions to access this command!',
            ephemeral=True,
        )
    elif (type(error) == commands.CommandOnCooldown):
        await ctx.send_response(
            f'This command is on cooldown! Try again in {error.args[0].split(" ")[-1].replace("s", "")} seconds!',
            ephemeral=True,
        )
    else:
        raise error

@bot.slash_command(guild_ids=[GUILD_ID], name="setup", description="Setup tony bot")
@commands.has_any_role(OWNER_ID)
async def setupTony(ctx: discord.ApplicationContext):  
    options = []
    for guild in bot.guilds:
        for channel in guild.text_channels:
            options.append(discord.SelectOption(label=channel.name, value=str(channel.id)))
    
    select = Select(
        placeholder="Select the console channel",
        options=options,
    )
        
    async def successSetup(interaction):
        channelId = select.values[0]
        channel = bot.get_channel(int(channelId))

        config_data = await loadJson('src/config.json')
        config_data['channel_id'] = channelId
        config_data['channel_name'] = str(channel)
        await writeJson(config_data, 'src/config.json')
        
        message = await channel.send("@everyone")
        await channel.send(embed=await createEmbed(discord, 'src/embeds/helper.json'))
        await channel.send(embed=await createEmbed(discord, 'src/embeds/console.json'))
        await interaction.response.defer()
        
    select.callback = successSetup
    view = View()
    view.add_item(select)
    await ctx.respond(embed=await createEmbed(discord, 'src/embeds/setup.json'), view=view, ephemeral=True)

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="ban", description="Ban a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="b", description="Ban a player")
@commands.has_any_role(OWNER_ID, SENIOR_ID)
@option("server", description="ffa or snd", choices=["ffa", "snd"])
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xuid>')")
@option("reason", description="Reason")
async def ban(ctx, server, player, reason):
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        server.lower()
        if server == "ffa":
            params = {"serverId": "14111196834979", "command": f"!b {player} {reason}"}
        elif server == "snd":
            params = {"serverId": "14111196834977", "command": f"!b {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully banned player with Id: {player} for reason: {reason}", ephemeral=True)
            else:
                await ctx.respond(f"Server Down Or Player Not Found: {req.status}", ephemeral=True)
                return 

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="unban", description="Unban a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="ub", description="Unban a player")
@commands.has_any_role(OWNER_ID, SENIOR_ID)
@option("server", description="ffa or snd", choices=["ffa", "snd"])
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xuid>')")
@option("reason", description="Reason")
async def unban(ctx, server, player, reason):
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        server.lower()
        if server == "ffa":
            params = {"serverId": "14111196834979", "command": f"!ub {player} {reason}"}
        elif server == "snd":
            params = {"serverId": "14111196834977", "command": f"!ub {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully unbanned player: {player} for reason: {reason}", ephemeral=True)  
            else:
                await ctx.respond(f"Server Down Or Player Not Found: {req.status}", ephemeral=True)
                return 

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="tempban", description="Tempban a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="tb", description="Tempban a player")
@commands.has_any_role(OWNER_ID, SENIOR_ID, ADMIN_ID)
@option("server", description="ffa or snd", choices=["ffa", "snd"])
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xuid>')")
@option("duration", description="<duration (m|h|d|w|y)>")
@option("reason", description="Reason")
async def tempban(ctx, server, player, duration, reason):
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        server.lower()
        if server == "ffa":
            params = {"serverId": "14111196834979", "command": f"!tb {player} {duration} {reason}"}
        elif server == "snd":
            params = {"serverId": "14111196834977", "command": f"!tb {player} {duration} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully tempbanned player: {player} for reason: {reason}", ephemeral=True)  
            else:
                await ctx.respond(f"Server Down Or Player Not Found: {req.status}", ephemeral=True)
                return 

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="flag", description="Flag a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="f", description="Flag a player")
@commands.has_any_role(OWNER_ID, SENIOR_ID, ADMIN_ID)
@option("server", description="ffa or snd", choices=["ffa", "snd"])
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xuid>')")
@option("reason", description="Reason")
async def flag(ctx, server, player, reason):
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        server.lower()
        if server == "ffa":
            params = {"serverId": "14111196834979", "command": f"!flag {player} {reason}"}
        elif server == "snd":
            params = {"serverId": "14111196834977", "command": f"!flag {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully flagged player: {player} for reason: {reason}", ephemeral=True)  
            else:
                await ctx.respond(f"Server Down Or Player Not Found: {req.status}", ephemeral=True)
                return 

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="unflag", description="Unflag a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="uf", description="Unflag a player")
@commands.has_any_role(OWNER_ID, SENIOR_ID, ADMIN_ID)
@option("server", description="ffa or snd", choices=["ffa", "snd"])
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xuid>')")
@option("reason", description="Reason")
async def unflag(ctx, server, player, reason):
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        server.lower()
        if server == "ffa":
            params = {"serverId": "14111196834979", "command": f"!uf {player} {reason}"}
        elif server == "snd":
            params = {"serverId": "14111196834977", "command": f"!uf {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully unflagged player: {player} for reason: {reason}", ephemeral=True)  
            else:
                await ctx.respond(f"Server Down Or Player Not Found: {req.status}", ephemeral=True)
                return  

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="warn", description="Warn a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="w", description="Warn a player")
@commands.has_any_role(OWNER_ID, SENIOR_ID, ADMIN_ID)
@option("server", description="ffa or snd", choices=["ffa", "snd"])
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xuid>')")
@option("reason", description="Reason")
async def warn(ctx, server, player, reason):
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        server.lower()
        if server == "ffa":
            params = {"serverId": "14111196834979", "command": f"!w {player} {reason}"}
        elif server == "snd":
            params = {"serverId": "14111196834977", "command": f"!w {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully Warned player: {player} for reason: {reason}", ephemeral=True)  
            else:
                await ctx.respond(f"Server Down Or Player Not Found: {req.status}", ephemeral=True)
                return 

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="warnclear", description="Clear warnings from a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="wc", description="Clear warnings from a player")
@commands.has_any_role(OWNER_ID, SENIOR_ID, ADMIN_ID)
@option("server", description="ffa or snd", choices=["ffa", "snd"])
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xuid>')")
async def warnclear(ctx, server, player):
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        server.lower()
        if server == "ffa":
            params = {"serverId": "14111196834979", "command": f"!wc {player}"}
        elif server == "snd":
            params = {"serverId": "14111196834977", "command": f"!wc {player}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully Cleared warnings from player: {player}", ephemeral=True)  
            else:
                await ctx.respond(f"Server Down Or Player Not Found: {req.status}", ephemeral=True)
                return 

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="kick", description="Kick a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="k", description="Kick a player")
@commands.has_any_role(OWNER_ID, SENIOR_ID, ADMIN_ID)
@option("server", description="ffa or snd", choices=["ffa", "snd"])
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xuid>')")
@option("reason", description="Reason")
async def kick(ctx, server, player, reason):
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        server.lower()
        if server == "ffa":
            params = {"serverId": "14111196834979", "command": f"!kick {player} {reason}"}
        elif server == "snd":
            params = {"serverId": "14111196834977", "command": f"!kick {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully Warned player: {player} for reason: {reason}", ephemeral=True)  
            else:
                await ctx.respond(f"Server Down Or Player Not Found: {req.status}", ephemeral=True)
                return 

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="say", description="Broadcast message to all clients")
@bot.slash_command(guild_ids=[GUILD_ID], name="s", description="Broadcast message to all clients")
@commands.has_any_role(OWNER_ID, SENIOR_ID, ADMIN_ID)
@option("server", description="ffa or snd", choices=["ffa", "snd"])
@option("message", description="Your message")
async def say(ctx, server, message):
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        server.lower()
        if server == "ffa":
            params = {"serverId": "14111196834979", "command": f"!say {message}"}
        elif server == "snd":
            params = {"serverId": "14111196834977", "command": f"!say {message}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfull", ephemeral=True)
            else:
                await ctx.respond(f"Server Down Or Player Not Found: {req.status}", ephemeral=True)
                return    
            

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.slash_command(guild_ids=[GUILD_ID], name="tony", description="Kick nott GG")
@commands.has_any_role(OWNER_ID, SENIOR_ID)
@option("message", description="Message for nott")
async def tony(ctx, message):
    await initNottKick(message)
    await ctx.respond("lol", ephemeral=True)
    return


@bot.command()
async def nottUpdate(ctx):
    await ctx.message.delete()
    await asyncio.sleep(2)
    await ctx.respond("Senior Admins Now Can Now Kick Notthepro with: '/tony <reason>'", ephemeral=True)
    return


bot.run(TOKEN)