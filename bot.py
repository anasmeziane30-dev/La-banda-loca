import os
import discord
from discord.ext import commands
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح باسم: {bot.user}')

@bot.command(name='play', help='لتشغيل الأغنية بكتابة الاسم')
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("❌ يجب أن تكون متصلاً بقناة صوتية أولاً!")
        return

    voice_channel = ctx.author.voice.channel
    
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    voice_client = ctx.guild.voice_client

    await ctx.send(f"جاري البحث عن: **{search}** 🔍...")

    # إعدادات مخصصة لاستخراج رابط الصوت المباشر بدون مشاكل
    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': 'True',
        'default_search': 'ytsearch1',
        'ynosplit': True,
    }

    FFMPEG_OPTIONS = {
        'options': '-vn',
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    }

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(search, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            
            url = info.get('url', None)
            title = info.get('title', 'مقطع صوتي')

        if not url:
            await ctx.send("❌ لم يتم العثور على نتائج لهذا البحث.")
            return

        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        
        if voice_client.is_playing():
            voice_client.stop()
            
        voice_client.play(source)
        await ctx.send(f"🎶 جاري تشغيل الآن: **{title}**")
        
    except Exception as e:
        await ctx.send("❌ حدث خطأ أثناء تشغيل الصوت. تأكد من إعدادات البوت.")
        print(f"Error: {e}")

@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ تم إيقاف الأغنية مؤقتاً.")

@bot.command(name='resume')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ تم استئناف الأغنية.")

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 تم قطع الاتصال والخروج من القناة الصوتية.")

bot.run(os.environ.get('DISCORD_TOKEN'))
