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

# أمر التشغيل بالاسم !play (يمكنك كتابة جزء من الاسم فقط)
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

    server = ctx.guild
    voice_client = server.voice_client

    await ctx.send(f"جاري البحث عن: **{search}** 🔍...")

    # إعدادات البحث والتشغيل عبر yt-dlp
    YDL_OPTIONS = {
        'format': 'bestaudio',
        'noplaylist': 'True',
        'default_search': 'ytsearch1',
    }
    
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(search, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            
            url2 = info['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            
            if voice_client.is_playing():
                voice_client.stop()
                
            voice_client.play(source)
            await ctx.send(f"🎶 جاري تشغيل الآن: **{info.get('title', 'المقطع')}**")
        except Exception as e:
            await ctx.send("❌ حدث خطأ أثناء البحث أو تشغيل الأغنية.")
            print(e)

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

# تشغيل البوت بأمان من متغيرات البيئة
bot.run(os.environ.get('DISCORD_TOKEN'))
