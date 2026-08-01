import discord
from discord.ext import commands
import os
from datetime import timedelta

# سحب التوكن تلقائياً من إعدادات البيئة في Render
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")

# --- 1. نظام الترحيب بالأعضاء الجدد (مع منشن) ---
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome🫂")
    if not channel:
        channel = discord.utils.get(member.guild.text_channels, name="𝐖𝐄𝐋𝐂𝐎𝐌𝐄🫂")
        
    if channel is not None:
        embed = discord.Embed(
            title="👋 مرحباً بك في سيرفر الفريق!",
            description=f"أهلاً بك يا {member.mention} في سيرفر **{member.guild.name}**! 🎮\n\nنورّت السيرفر، نتمنى لك أوقاتاً ممتعة معنا.",
            color=discord.Color.green()
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"عدد الأعضاء الحالي: {member.guild.member_count}")
        await channel.send(embed=embed)

# --- 2. نظام توديع الأعضاء المغادرين (مع منشن) ---
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="abandonment👋🏻")
    if not channel:
        channel = discord.utils.get(member.guild.text_channels, name="𝐀𝐁𝐀𝐍𝐃𝐀𝐍𝐌𝐄𝐍𝐓👋🏻")
        
    if channel is not None:
        embed = discord.Embed(
            title="📤 لا نريد أن نراك مجددا",
            description=f"العضو {member.mention} غادر السيرفر.",
            color=discord.Color.red()
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"عدد الأعضاء الحالي: {member.guild.member_count}")
        await channel.send(embed=embed)

# --- 3. أوامر الإشراف (Ban, Kick, Timeout) ---

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = discord.Embed(title="🔨 تم حظر العضو", description=f"تم حظر {member.mention} بنجاح.", color=discord.Color.dark_red())
    if reason: embed.add_field(name="السبب", value=reason, inline=False)
    embed.set_footer(text=f"بواسطة: {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = discord.Embed(title="👢 تم طرد العضو", description=f"تم طرد {member.mention}.", color=discord.Color.orange())
    if reason: embed.add_field(name="السبب", value=reason, inline=False)
    embed.set_footer(text=f"بواسطة: {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="timeout", aliases=["mute"])
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason=None):
    duration = timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    embed = discord.Embed(title="⏳ تم إعطاء Timeout للعضو", description=f"تم إسكات {member.mention} لمدة **{minutes} دقيقة**.", color=discord.Color.yellow())
    if reason: embed.add_field(name="السبب", value=reason, inline=False)
    embed.set_footer(text=f"بواسطة: {ctx.author.name}")
    await ctx.send(embed=embed)

# --- 4. أوامر غلق وفتح القنوات (Lock / Unlock) ---

@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    """قفل القناة الحالية لمنع الأعضاء من الكتابة"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(
        title="🔒 تم قفل القناة",
        description="تم إيقاف الكتابة في هذه القناة مؤقتاً.",
        color=discord.Color.dark_orange()
    )
    embed.set_footer(text=f"بواسطة: {ctx.author.name}")
    await ctx.send(embed=embed)

@lock.error
async def lock_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ عذراً، لا تمتلك صلاحية `إدارة القنوات` لاستخدام هذا الأمر.")

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    """فتح القناة الحالية والسماح للأعضاء بالكتابة"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    embed = discord.Embed(
        title="🔓 تم فتح القناة",
        description="تم السماح للكتابة في هذه القناة مرة أخرى.",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"بواسطة: {ctx.author.name}")
    await ctx.send(embed=embed)

@unlock.error
async def unlock_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ عذراً، لا تمتلك صلاحية `إدارة القنوات` لاستخدام هذا الأمر.")

# تشغيل البوت
bot.run(TOKEN)
