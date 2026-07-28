import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة الأناشيد مع روابط التحميل المباشرة من Google Drive
SONGS = {
    "اليد فاليد": "https://drive.google.com/uc?export=download&id=1H3Esa2sWouZrtkOQFKGwVRdkifomMdMP",
    # يمكنك إضافة باقي الأناشيد هنا بنفس الطريقة:
    # "اسم النشيد 2": "رابط_التحميل_المباشر",
}

# تصميم القائمة المنسدلة
class SongSelect(discord.ui.Select):
    def __init__(self):
        # إنشاء الخيارات بناءً على أسماء الأناشيد الموجودة
        options = [
            discord.SelectOption(label=song_name, description="تشغيل هذا النشيد 🔴⚪")
            for song_name in SONGS.keys()
        ]
        super().__init__(placeholder="اختر نشيداً لتشغيله...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        song_name = self.values[0]
        
        # التحقق من أن المستخدم متصل بقناة صوتية
        if not interaction.user.voice:
            await interaction.response.send_message("يجب أن تكون متصلاً بقناة صوتية أولاً!", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        
        if interaction.guild.voice_client is None:
            vc = await channel.connect()
        else:
            vc = interaction.guild.voice_client

        audio_url = SONGS[song_name]

        if vc.is_playing():
            vc.stop()

        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
        vc.play(source, after=lambda e: print(f"انتهى تشغيل: {song_name}"))

        await interaction.response.send_message(f"جاري تشغيل النشيد: **{song_name}** 🔴⚪", ephemeral=False)

# واجهة تحتوي على القائمة المنسدلة
class SongView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SongSelect())

@bot.command(name="menu")
async def menu(ctx):
    """أمر لإظهار قائمة الأناشيد المنسدلة في الشات"""
    await ctx.send("قائمة أناشيد **Ultras Fanatic Reds** 🔴⚪\nاختر النشيد الذي تريد تشغيله:", view=SongView())

@bot.command(name="leave")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("تم قطع الاتصال بالقناة الصوتية.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# bot.run("YOUR_BOT_TOKEN")
