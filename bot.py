import os
import discord
from discord.ext import commands
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="", intents=intents)

PRESET_SONGS = [
    {
        'title': 'آجي نرويلك', 
        'url': 'https://www.youtube.com/watch?v=N4T_r6i4mYQ'
    },
    {
        'title': 'فالقلب حاضرة', 
        'url': 'https://www.youtube.com/watch?v=XSNGi95Dp80'
    },
    {
        'title': 'فالجيب', 
        'url': 'https://www.youtube.com/watch?v=_mLBgoFJGV8'
    },
    {
        'title': 'FIDÉLITÉ [Live]', 
        'url': 'https://www.youtube.com/watch?v=GUuXt7g2dT4'
    },
    {
        'title': 'الحايك مطروز', 
        'url': 'https://www.youtube.com/watch?v=wGojegOFdDI'
    },
    {
        'title': 'قاصد بأنغامي', 
        'url': 'https://www.youtube.com/watch?v=IrZNobnKyYQ'
    },
    {
        'title': 'La Stella Brillerà', 
        'url': 'https://www.youtube.com/watch?v=JhCDliMUxuM'
    }
]

class SongSelectView(discord.ui.View):
    def __init__(self, songs):
        super().__init__(timeout=180)
        for i, song in enumerate(songs):
            # تم اختصار النص لكي يظهر كاملاً وبشكل أنيق على الأزرار
            button = discord.ui.Button(
                label=f"{i+1}. {song['title']}", 
                style=discord.ButtonStyle.danger,
                custom_id=str(i)
            )
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        # الرد الفوري لمنع خطأ التفاعل (Échec de l'interaction)
        await interaction.response.defer(ephemeral=True)

        song_index = int(interaction.data['custom_id'])
        selected_song = PRESET_SONGS[song_index]
        
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ يجب عليك الدخول إلى روم صوتي أولاً!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await voice_channel.connect()
        else:
            await voice_client.move_to(voice_channel)

        await interaction.followup.send(f"⏳ جاري تجهيز وتشغيل: **{selected_song['title']}**...", ephemeral=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
        }
        
        try:
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
            await interaction.followup.send(f"❌ حدث خطأ أثناء تشغيل الأغنية: {e}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.strip().lower() == "play!":
        embed = discord.Embed(
            title="🔴 Ultras Fanatic Reds - راديو الأغاني الرسمية",
            description="اختر الأغنية التي تريد تشغيلها في الروم الصوتي:",
            color=discord.Color.red()
        )
        
        description_list = ""
        for i, song in enumerate(PRESET_SONGS):
            description_list += f"**{i+1}.** {song['title']}\n"
        
        embed.add_field(name="الأناشيد المتاحة:", value=description_list, inline=False)
        
        view = SongSelectView(PRESET_SONGS)
        await message.channel.send(embed=embed, view=view)

    await bot.process_commands(message)

token = os.getenv("TOKEN")
if not token:
    print("❌ خطأ: لم يتم العثور على متغير البيئة TOKEN.")
else:
    bot.run(token)
