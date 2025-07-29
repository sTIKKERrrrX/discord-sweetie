import discord
import os
from discord.ext import commands
import asyncio
import yt_dlp
from myserver import server_on

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# เก็บคิวเพลงสำหรับแต่ละเซิร์ฟเวอร์
song_queues = {}

def get_queue(ctx):
    return song_queues.setdefault(ctx.guild.id, asyncio.Queue())

async def play_next(ctx):
    queue = get_queue(ctx)

    if queue.empty():
        await ctx.send("📭 คิวเพลงหมดแล้ว")
        return

    info = await queue.get()

    url2 = info['url']
    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)

    def after_playing(error):
        if error:
            print(f"Error: {error}")
        fut = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f"Next song error: {e}")

    ctx.voice_client.play(source, after=after_playing)
    await ctx.send(f"▶️ กำลังเล่น: **{info.get('title')}**")

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')

    # ตั้งสถานะข้อความทั่วไป
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="เพลง คำสั่งบอท !play ")
    )

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)
        await ctx.send(f"✅ เข้าห้องเสียง: {channel}")
    else:
        await ctx.send("❗ เข้าห้อง voice ก่อน!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 ออกจากห้องแล้ว")
    else:
        await ctx.send("❗ บอทยังไม่อยู่ในห้อง")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.invoke(bot.get_command("join"))

    queue = get_queue(ctx)

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)

    await queue.put(info)
    await ctx.send(f"🎵 เพิ่มเพลง: **{info.get('title')}**")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ ข้ามเพลงแล้ว")
    else:
        await ctx.send("❗ ไม่มีเพลงที่กำลังเล่น")

@bot.command()
async def stop(ctx):
    queue = get_queue(ctx)
    while not queue.empty():
        queue.get_nowait()

    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("🛑 หยุดและล้างคิวแล้ว")
server_on()

# 🔑 ใส่โทเคนของบอทคุณตรงนี้
bot.run(os.getenv('TOKEN'))