import os
import discord
from discord.ext import commands
import random

# إعدادات الصلاحيات الأساسية للبوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة لحفظ المشاركين في الدورة
tournament_participants = []

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")
    print("البوت جاهز لإدارة دورة eFootball 2026 بكفاءة!")

# ==================== الأوامر الأساسية ====================

# 1. أمر التسجيل في الدورة
@bot.command(name="تسجيل", help="سجل اسمك ومعرف اللعبة للمشاركة في الدورة")
async def register(ctx, *, game_id: str):
    for p in tournament_participants:
        if p['member'] == ctx.author:
            await ctx.send(f"⚠️ {ctx.author.mention}, أنت مسجل بالفعل في الدورة!")
            return
    
    tournament_participants.append({"member": ctx.author, "game_id": game_id})
    
    embed = discord.Embed(
        title="⚽ تسجيل ناجح في دورة eFootball 2026",
        description=f"تم تسجيل اللاعب {ctx.author.mention} بنجاح.",
        color=discord.Color.green()
    )
    embed.add_field(name="معرف اللعبة (Konami ID / In-game Name):", value=game_id, inline=False)
    embed.set_footer(text=f"إجمالي عدد المشاركين حالياً: {len(tournament_participants)}")
    
    await ctx.send(embed=embed)

# 2. أمر عرض قائمة المشاركين
@bot.command(name="المشاركين", help="يعرض قائمة بجميع المسجلين في البطولة")
async def list_participants(ctx):
    if not tournament_participants:
        await ctx.send("📭 لا يوجد أي مشاركين مسجلين حتى الآن.")
        return

    embed = discord.Embed(
        title="📋 قائمة المشاركين في دورة eFootball 2026",
        color=discord.Color.blue()
    )
    
    description = ""
    for index, p in enumerate(tournament_participants, start=1):
        description += f"**{index}.** {p['member'].mention} - `ID: {p['game_id']}`\n"
    
    embed.description = description
    embed.set_footer(text=f"العدد الكلي: {len(tournament_participants)} لاعبين")
    
    await ctx.send(embed=embed)

# 3. أمر إعلان مواجهة فردية (للمنظمين فقط)
@bot.command(name="مواجهة", help="يعلن عن مباراة بين لاعبين (للمنظمين فقط)")
@commands.has_permissions(administrator=True)
async def match_vs(ctx, player1: discord.Member, player2: discord.Member, *, round_name: str = "دور المجموعات"):
    embed = discord.Embed(
        title="🔥 مواجهة رسمية جديدة - eFootball 2026",
        description=f"**المرحلة:** {round_name}",
        color=discord.Color.gold()
    )
    embed.add_field(name="اللاعب الأول", value=player1.mention, inline=True)
    embed.add_field(name="VS", value="⚡", inline=True)
    embed.add_field(name="اللاعب الثاني", value=player2.mention, inline=True)
    embed.set_footer(text="يرجى إرسال نتيجة المباراة للإدارة بعد نهايتها.")
    
    await ctx.send(embed=embed)

@match_vs.error
async def match_vs_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ عذراً، هذا الأمر مخصص للمنظمين ومشرفي البطولات فقط.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ يرجى تحديد اللاعبين بشكل صحيح. مثال: `!مواجهة @Player1 @Player2 ربع النهائي`")

# 4. أمر مسح الدورة (للمنظمين)
@bot.command(name="مسح_الدورة", help="يقوم بمسح قائمة المشاركين لبدء بطولة جديدة")
@commands.has_permissions(administrator=True)
async def clear_tournament(ctx):
    global tournament_participants
    tournament_participants.clear()
    await ctx.send("🗑️ تم مسح قائمة المشاركين وتصفير الدورة بنجاح.")

# ==================== الأوامر الإضافية والمتقدمة ====================

# 5. أمر سحب القرعة العشوائي التلقائي
@bot.command(name="قرعة", help="يقوم بإنشاء مواجهات عشوائية بين المسجلين تلقائياً")
@commands.has_permissions(administrator=True)
async def generate_draw(ctx):
    if len(tournament_participants) < 2:
        await ctx.send("⚠️ لا يوجد عدد كافٍ من المشاركين لعمل قرعة (يجب وجود لاعبين على الأقل).")
        return

    shuffled = tournament_participants.copy()
    random.shuffle(shuffled)

    embed = discord.Embed(
        title="🎲 نتائج قرعة دورة eFootball 2026",
        description="تم سحب القرعة بنجاح والمواجهات كالتالي:",
        color=discord.Color.purple()
    )

    match_number = 1
    for i in range(0, len(shuffled) - 1, 2):
        p1 = shuffled[i]
        p2 = shuffled[i+1]
        embed.add_field(
            name=f"المباراة {match_number}",
            value=f"{p1['member'].mention} (`{p1['game_id']}`)  **VS**  {p2['member'].mention} (`{p2['game_id']}`)",
            inline=False
        )
        match_number += 1

    if len(shuffled) % 2 != 0:
        lucky_player = shuffled[-1]
        embed.add_field(
            name="🎫 تأهل تلقائي (Bye)",
            value=f"اللاعب {lucky_player['member'].mention} تأهل مباشرة لعدم وجود خصم في هذه الجولة.",
            inline=False
        )

    embed.set_footer(text="بالتوفيق لجميع المشاركين!")
    await ctx.send(embed=embed)

@generate_draw.error
async def generate_draw_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ عذراً، أمر القرعة مخصص للمنظمين فقط.")

# 6. أمر تسجيل النتيجة وإعلان الفائز
@bot.command(name="نتيجة", help="تسجيل نتيجة مباراة وإعلان الفائز")
@commands.has_permissions(administrator=True)
async def match_result(ctx, winner: discord.Member, winner_score: int, loser: discord.Member, loser_score: int):
    embed = discord.Embed(
        title="📢 نتيجة مباراة رسمية - eFootball 2026",
        description="انتهت المواجهة بالنتيجة التالية:",
        color=discord.Color.teal()
    )
    embed.add_field(name="👑 الفائز", value=f"{winner.mention}\nالأهداف: **{winner_score}**", inline=True)
    embed.add_field(name="❌ الخاسر", value=f"{loser.mention}\nالأهداف: **{loser_score}**", inline=True)
    embed.set_footer(text="مبروك للفائز وهاردلك للخاسر في دورة eFootball!")

    await ctx.send(embed=embed)

@match_result.error
async def match_result_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ الصيغة غير صحيحة. مثال: `!نتيجة @Winner 3 @Loser 1`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ عذراً، هذا الأمر مخصص للمنظمين فقط.")

# 7. أمر انسحاب لاعب وإزالته من البطولة
@bot.command(name="انسحاب", help="إزالة لاعب من قائمة المشاركين بواسطة المنظمين")
@commands.has_permissions(administrator=True)
async def remove_participant(ctx, member: discord.Member):
    global tournament_participants
    
    for p in tournament_participants:
        if p['member'] == member:
            tournament_participants.remove(p)
            await ctx.send(f"🗑️ تم إزالة اللاعب {member.mention} من قائمة المشاركين في الدورة.")
            return
            
    await ctx.send(f"⚠️ اللاعب {member.mention} غير مسجل أصلاً في الدورة.")

@remove_participant.error
async def remove_participant_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ عذراً، هذا الأمر مخصص للمنظمين فقط.")

# جلب التوكن من نظام التشغيل حصراً (لا يوجد توكن مكتوب هنا)
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ خطأ: لم يتم العثور على متغير البيئة DISCORD_TOKEN. تأكد من إضافته في إعدادات الاستضافة.")

bot.run(TOKEN)
