import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
from myserver import server_on

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1399412621706264721
LEAVE_CHANNEL_ID = 1399424077365510267

FONT_BIG = "arialbd.ttf"
FONT_MED = "arial.ttf"

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')

    # ตั้งสถานะข้อความทั่วไป
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="สอบถามติดต่อคุณติ๊ก ")
    )

@bot.event
async def on_member_join(member):
    async with aiohttp.ClientSession() as session:
        async with session.get(str(member.display_avatar.with_format("png").with_size(256).url)) as resp:
            avatar_bytes = await resp.read()

    # พื้นหลังดำลึก
    bg = Image.new("RGBA", (800, 300), (20, 20, 25, 255))
    draw = ImageDraw.Draw(bg)

    # วงแสงชมพูนวลหลัง avatar
    glow = Image.new("RGBA", (220, 220), (255, 105, 180, 70))  # สีชมพูโปร่งแสง
    glow = glow.resize((220, 220))
    bg.paste(glow, (40, 40), glow)

    # ตัดวงกลม avatar
    avatar = Image.open(io.BytesIO(avatar_bytes)).resize((180, 180)).convert("RGBA")
    mask = Image.new("L", (180, 180), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 180, 180), fill=255)
    bg.paste(avatar, (60, 60), mask)

    # โหลดฟอนต์
    try:
        font_big = ImageFont.truetype(FONT_BIG, 70)
        font_med = ImageFont.truetype(FONT_MED, 40)
    except:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()

    # เขียนข้อความ สีชมพูสดใสกับขาว
    draw.text((270, 80), "WELCOME", font=font_big, fill=(255, 105, 180))  # ชมพูร้อนแรง
    draw.text((270, 170), "TO SWEETIE X", font=font_med, fill=(255, 255, 255))  # ขาวสะอาด

    # บันทึกภาพ
    with io.BytesIO() as image_binary:
        bg.save(image_binary, "PNG")
        image_binary.seek(0)

        embed = discord.Embed(
            title="【::::: ยินดีต้อนรับ :::::】 ",
            description=f"{member.mention} ::: เข้าสู่ Sweetie X ::: ",
            color=discord.Color.from_rgb(255, 105, 180)  # ชมพู
        )
        embed.set_image(url="attachment://welcome.png")
        embed.set_footer(text=" ::: พร้อมจะลุยหรือยัง ? :::")

        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed, file=discord.File(image_binary, filename="welcome.png"))

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(LEAVE_CHANNEL_ID)
    if channel:
        await channel.send(f"👋 {member.display_name} 【 ::: GOOD BYE ! SEE YOU AGAIN ! ::: 】")

server_on()


bot.run(os.getenv('TOKEN'))