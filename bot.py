import os
import discord
from discord.ext import commands
import yt_dlp
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# سيرفر وهمي صغير لإرضاء منصة Render ومنع خطأ البورتات
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

# تشغيل السيرفر الوهمي في الخلفية
threading.Thread(target=run_server, daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="", intents=intents)

PRESET_SONGS = [
    {'title': 'آجي نرويلك', 'url': 'https://www.youtube.com/watch?v=N4T_r6i4mYQ'},
    {'title': 'فالقلب حاضرة', 'url': 'https://www.youtube.com/watch?v=XSNGi95Dp80'},
    {'title': 'فالجيب', 'url': 'https://www.youtube.com/watch?v=_mLBgoFJGV8'},
    {'title': 'FIDÉLITÉ [Live]', 'url': 'https://www.youtube.com/watch?v=GUuXt7g2dT4'},
    {'title': 'الحايك مطروز', 'url': 'https://www.youtube.com/watch?v=wGojegOFdDI'},
    {'title': 'قاصد بأنغامي', 'url': 'https://www.youtube.com/watch?v=IrZNobnKyYQ'},
    {'title': 'La Stella Brillerà', 'url': 'https://www.youtube.com/watch?v=JhCDliMUxuM'}
]

class SongSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for i, song in enumerate(PRESET_SONGS):
            options.append(
                discord.SelectOption(
                    label=song['title'], 
                    value=str(i), 
                    description=f"تشغيل الأغنية رقم {i+1}"
                )
            )
        super().__init__(placeholder='🎵 اختر الأغنية التي تريد تشغيلها...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            song_index = int(self.values[0])
            selected_song = PRESET_SONGS[song_index]
            
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.followup.send("❌ يجب عليك الدخول إلى روم صوتي أولاً!", ephemeral=True)
                return

            voice_channel = interaction.user.voice.channel
            voice_client = interaction.guild.voice_client
            
            if voice_client is None:
                voice_client = await voice_channel.connect()
            else:
                if voice_client.channel != voice_channel:
                    await voice_client.move_to(voice_channel)

            await interaction.followup.send(f"⏳ جاري تجهيز وتشغيل: **{selected_song['title']}**...", ephemeral=True)

            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(selected_song['url'], download=False)
                audio_url = info['url']

            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }

            source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            
            if voice_client.is_playing():
                voice_client.stop()

            voice_client.play(source, after=lambda e: print(f'انتهى التشغيل: {e}'))
            
            await interaction.followup.send(f"🎶 يتم الآن تشغيل: **{selected_song['title']}**", ephemeral=False)

        except Exception as e:
            print(f"❌ حدث خطأ: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {e}", ephemeral=True)

class SongSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SongSelect())

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التأكد من استقبال كلمة play! بشكل دقيق بغض النظر عن المسافات
    if message.content.strip().lower() == "play!":
        embed = discord.Embed(
            title="🔴 Ultras Fanatic Reds - راديو الأغاني الرسمية",
            description="اختر من القائمة المنسدلة أدناه الأغنية التي تريد تشغيلها:",
            color=discord.Color.red()
        )
        
        view = SongSelectView()
        await message.channel.send(embed=embed, view=view)

token = os.getenv("TOKEN")
if not token:
    print("❌ خطأ: لم يتم العثور على متغير البيئة TOKEN.")
else:
    bot.run(token)
