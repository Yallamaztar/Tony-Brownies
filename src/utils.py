import os, platform
import json
import asyncio, aiohttp
import yt_dlp

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

async def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

async def initRoles(guild):
    roles_data = []
    for role in guild.roles:
        roles_data.append({"name": role.name, "id": role.id})
    return roles_data   
        
async def loadJson(filePath: str):
    with open(filePath) as f:
        return json.load(f)
    
async def writeJson(data, filePath: str): 
    with open(filePath, 'w') as f:
        return json.dump(data, f, indent=4)
    
async def createEmbed(discord, file_path): 
    with open(file_path, 'r') as f:
        embed_config = json.load(f)
        
    embed = discord.Embed.from_dict(embed_config['embeds'][0])
    embed.color = discord.Color.blue()
    
    if 'username' in embed_config:
        embed.set_author(name=embed_config['username'], icon_url=embed_config.get('avatar_url', None))
    return embed

async def menu(bot, alert=None):
    print('''\n
\x1B[38;2;245;0;245m ████████╗ ██████╗ ███╗   ██╗██╗   ██╗    ██████╗  ██████╗ ████████╗    
\x1B[38;2;225;0;245m ╚══██╔══╝██╔═══██╗████╗  ██║╚██╗ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝    
\x1B[38;2;205;0;245m    ██║   ██║   ██║██╔██╗ ██║ ╚████╔╝     ██████╔╝██║   ██║   ██║       
\x1B[38;2;185;0;245m    ██║   ██║   ██║██║╚██╗██║  ╚██╔╝      ██╔══██╗██║   ██║   ██║       
\x1B[38;2;165;0;245m    ██║   ╚██████╔╝██║ ╚████║   ██║       ██████╔╝╚██████╔╝   ██║       
\x1B[38;2;145;0;245m    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝   ╚═╝       ╚═════╝  ╚═════╝    ╚═╝ \x1b[0m      
    ''')
    print(f'[ \x1B[38;2;245;0;245mConnected\x1b[0m ]\n[ \x1B[38;2;245;0;245mBot:\x1b[0m {bot.user.name} ]\n[ \x1B[38;2;245;0;245mID:\x1b[0m {bot.user.id} ]')
                                                      
BROWNIES_BASEURI = "http://141.11.196.83:1624"

# SnD
BROWNIES_SND = f"{BROWNIES_BASEURI}/Console/Execute?serverId=14111196834977&"
BROWNIES_SND_STATUS = "http://141.11.196.83:1624/api/Status/?id=14111196834977"

# FFA
BROWNIES_FFA = f"{BROWNIES_BASEURI}/Console/Execute?serverId=14111196834979&"
BROWNIES_FFA_STATUS = "http://141.11.196.83:1624/api/Status/?id=14111196834979"

nott_users = ["Notthepro", "xxmlggyatxx", "mlgproconfirmed", "yesthebot"]

async def browniesStatus(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()
            players = [player['name'] for player in data[0]['players']]
            return players
        
async def initNottKick(reason):
    snd_name = await browniesStatus(BROWNIES_SND_STATUS)
    for name in snd_name:
        if name in nott_users:
            await antiNottScript(BROWNIES_SND, name, reason)
    ffa_name = await browniesStatus(BROWNIES_FFA_STATUS)
    for name in ffa_name:
        if name in nott_users:
            await antiNottScript(BROWNIES_FFA, name, reason)

async def antiNottScript(url, name, reason):
    header = {'Cookie': os.getenv('HEADERS')}
    params = { "command": f"!w {name} ^0^F{reason}" }
    async with aiohttp.ClientSession(headers=header) as session:
        for _ in range(4):
            async with session.get(url, params=params) as req:
                print(req)
            await asyncio.sleep(0.5)


AUDIO_QUEUE   = []
queue_size = 0

async def downloadYtAudio(url):
    opts = {
        'format': 'bestaudio/best',
        'noplaylist': 'True',
        'outtmpl': 'src/tmp/%(title)s.%(ext)s'
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def searchYt(video, ctx):
    check = video.split('/')
    link = False

# async def main():
#     await downloadYtAudio("https://www.youtube.com/watch?v=XJ1vxDFkNIY")

# if __name__ == '__main__':
#     asyncio.run(main())