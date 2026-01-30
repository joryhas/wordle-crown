import discord
import re
import os

# --- الإعدادات ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1466614946233057291
# -----------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'---')
    print(f'تم تشغيل البوت بنجاح!')
    print(f'اسم البوت: {client.user.name}')
    print(f'---')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # التحقق من أن الرسالة هي رسالة نتائج ووردل
    if "Your group is on a" in message.content and "yesterday's results" in message.content:
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)

        if not winner_role:
            print("خطأ: لم يتم العثور على الرول. تأكد من الـ ID.")
            return

        # 1. سحب الرول من الجميع
        for member in winner_role.members:
            try:
                await member.remove_roles(winner_role)
            except Exception as e:
                print(f"لم أتمكن من سحب الرول من {member.name}: {e}")

        # 2. استخراج الفائزين
        winners_mentions = []
        lines = message.content.split('\n')
        
        for line in lines:
            if "👑" in line:
                user_ids = re.findall(r'<@!?(\d+)>', line)
                for u_id in user_ids:
                    member = guild.get_member(int(u_id))
                    if member:
                        try:
                            await member.add_roles(winner_role)
                            winners_mentions.append(f"<@{u_id}>")
                        except Exception as e:
                            print(f"فشل إعطاء الرول لـ {member.name}: {e}")
                break

        # 3. إرسال التهنئة
        if winners_mentions:
            mentions_str = " ".join(winners_mentions)
            response = f"مبروك تاج ووردل لكلمة امس 👑 :\n{mentions_str}"
            await message.channel.send(response)

client.run(TOKEN)