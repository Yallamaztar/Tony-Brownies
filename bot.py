import discord 
from discord.ext import commands
from discord.ui import View, Select
from discord import option

import os, json
from datetime import datetime
import aiohttp
import uuid
import asyncio, threading
from dotenv import load_dotenv

from src.utils import (
    clear, 
    loadJson, 
    writeJson,
    createEmbed,
    menu,
    initRoles
)

load_dotenv()
with open('src/config.json') as f:
    config = json.load(f)
GUILD_ID: int = config['guild_id']
BASEURI = os.getenv('BASEURI')
COOKIE = os.getenv('HEADERS')

logs = []

# change to your server role ids
owner = 1190796076379283536 
senior = 1190794949353029664
admin = 1190703210973904957

bot = commands.Bot(command_prefix="!", Intents=discord.Intents.all())

@bot.event
async def on_ready():
    await clear()
    await menu(bot)
    await bot.change_presence(activity=discord.Game(name="Playing with myself"), status=discord.Status.idle)
    
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
    

@bot.event
async def on_application_command(ctx: discord.ApplicationContext):
    await clear()
    await menu(bot)
    
    id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d - %H:%M:%S")
    author = ctx.author.mention
    command_name = ctx.command.name
    
    print("\n[ \x1B[38;2;245;0;245mCommand Received\x1b[0m ]")
    print(f"[ \x1B[38;2;245;0;245mID:\x1b[0m {id} ]")
    print(f"[ \x1B[38;2;245;0;245mFrom:\x1b[0m {ctx.author.mention} ]")
    print(ctx.message)
    print(f"[ \x1B[38;2;245;0;245mCommand:\x1b[0m {ctx.command} ]")
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

@bot.slash_command(guild_ids=[GUILD_ID], name="setup", description="Setup tony bot")
async def setupTony(ctx: discord.ApplicationContext):  
    options = []
    for guild in bot.guilds:
        if guild.owner != ctx.author:
            await ctx.respond("You dont have permission to run this command", ephemeral=True)
            break
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
        
        await message.delete()
        
    select.callback = successSetup
    view = View()
    view.add_item(select)
    await ctx.respond(embed=await createEmbed(discord, 'src/embeds/setup.json'), view=view, ephemeral=True)
    
    

# ban a player
@bot.slash_command(guild_ids=[GUILD_ID], name="ban", description="Ban a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="b", description="Ban a player")
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xui>')")
@option("reason", description="Reason")
async def ban(ctx, player, reason):
    if ctx.author.id != senior or ctx.author.id != owner:
        await ctx.respond("You dont have permission to run this command", ephemeral=True)
        return
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        params = {"serverId": "14111196834977", "command": f"!b {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully banned player with Id: {player} for reason: {reason}", ephemeral=True)

@bot.slash_command(guild_ids=[GUILD_ID], name="unban", description="Unban a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="ub", description="Unban a player")
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xui>')")
@option("reason", description="Reason")
async def unban(ctx, player, reason):
    if ctx.author.id != senior or ctx.author.id != owner:
        await ctx.respond("You dont have permission to run this command", ephemeral=True)
        return
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        params = {"serverId": "14111196834977", "command": f"!ub {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully unbanned player: {player} for reason: {reason}", ephemeral=True)  

@bot.slash_command(guild_ids=[GUILD_ID], name="tempban", description="Tempban a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="tb", description="Tempban a player")
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xui>')")
@option("duration", description="<duration (m|h|d|w|y)>")
@option("reason", description="Reason")
async def tempban(ctx, player, duration, reason):
    if ctx.author.id != senior or ctx.author.id != owner or ctx.author.id != admin:
        await ctx.respond("You dont have permission to run this command", ephemeral=True)
        return
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        params = {"serverId": "14111196834977", "command": f"!tb {player} {duration} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully tempbanned player: {player} for reason: {reason}", ephemeral=True)  
    
@bot.slash_command(guild_ids=[GUILD_ID], name="flag", description="Flag a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="f", description="Flag a player")
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xui>')")
@option("reason", description="Reason")
async def flag(ctx, player, reason):
    if ctx.author.id != senior or ctx.author.id != owner or ctx.author.id != admin:
        await ctx.respond("You dont have permission to run this command", ephemeral=True)
        return
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        params = {"serverId": "14111196834977", "command": f"!f {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully flagged player: {player} for reason: {reason}", ephemeral=True)  
    
@bot.slash_command(guild_ids=[GUILD_ID], name="unflag", description="Unflag a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="uf", description="Unflag a player")
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xui>')")
@option("reason", description="Reason")
async def unflag(ctx, player, reason):
    if ctx.author.id != senior or ctx.author.id != owner or ctx.author.id != admin:
        await ctx.respond("You dont have permission to run this command", ephemeral=True)
        return
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        params = {"serverId": "14111196834977", "command": f"!uf {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully unflagged player: {player} for reason: {reason}", ephemeral=True)  
                
@bot.slash_command(guild_ids=[GUILD_ID], name="warn", description="Warn a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="w", description="Warn a player")
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xui>')")
@option("reason", description="Reason")
async def warn(ctx, player, reason):
    if ctx.author.id != senior or ctx.author.id != owner or ctx.author.id != admin:
        await ctx.respond("You dont have permission to run this command", ephemeral=True)
        return
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        params = {"serverId": "14111196834977", "command": f"!w {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully Warned player: {player} for reason: {reason}", ephemeral=True)  

@bot.slash_command(guild_ids=[GUILD_ID], name="warnclear", description="Clear warnings from a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="wc", description="Clear warnings from a player")
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xui>')")
async def warnclear(ctx, player):
    if ctx.author.id != senior or ctx.author.id != owner or ctx.author.id != admin:
        await ctx.respond("You dont have permission to run this command", ephemeral=True)
        return
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        params = {"serverId": "14111196834977", "command": f"!wc {player}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully Cleared warnings from player: {player}", ephemeral=True)  

@bot.slash_command(guild_ids=[GUILD_ID], name="kick", description="Kick a player")
@bot.slash_command(guild_ids=[GUILD_ID], name="k", description="Kick a player")
@option("player", description="Name or Xuid (if using xuid, please enter like '@<xui>')")
@option("reason", description="Reason")
async def kick(ctx, player, reason):
    if ctx.author.id != senior or ctx.author.id != owner or ctx.author.id != admin:
        await ctx.respond("You dont have permission to run this command", ephemeral=True)
        return
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        params = {"serverId": "14111196834977", "command": f"!k {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfully Warned player: {player} for reason: {reason}", ephemeral=True)  

@bot.slash_command(guild_ids=[GUILD_ID], name="say", description="Broadcast message to all clients")
@bot.slash_command(guild_ids=[GUILD_ID], name="s", description="Broadcast message to all clients")
@option("message", description="Your message")
async def s(ctx, player, reason):
    if ctx.author.id != senior or ctx.author.id != owner or ctx.author.id != admin:
        await ctx.respond("You dont have permission to run this command", ephemeral=True)
        return
    header = {'Cookie': COOKIE}
    async with aiohttp.ClientSession(headers=header) as session:
        url = "http://141.11.196.83:1624/Console/Execute"
        params = {"serverId": "14111196834977", "command": f"!s {player} {reason}"}
        async with session.get(url, params=params) as req:
            if req.status == 200:
                await ctx.respond(f"Successfull", ephemeral=True)
                




bot.run(os.getenv('TOKEN'))