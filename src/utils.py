import os, platform
import json
import asyncio, time

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
    print(f'[ Admin Panel ] [ v1.1 ] {f"[ {alert} ]" if alert else ""}\n')
    print(f'[ \x1B[38;2;245;0;245mConnected\x1b[0m ]\n[ \x1B[38;2;245;0;245mBot:\x1b[0m {bot.user.name} ]\n[ \x1B[38;2;245;0;245mID:\x1b[0m {bot.user.id} ]')
    print("[1] Broadcast a message\n")


