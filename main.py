import discord
import re

# --- الإعدادات (ضع بياناتك هنا) ---
TOKEN = 'MTQ2NjY0NjE2MDQ0MDY5Mjg4Mg.GiTdAu.gWf0RxD_03Z_6UgwqR853aHHiXyl4x-MxXpPmw'
WINNER_ROLE_ID = 1426023878576046110  # استبدل هذا الرقم بـ ID الرول اللي تبيه
# -------------------------------

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
    # نتأكد إن البوت ما يرد على نفسه
    if message.author == client.user:
        return

    # التحقق من أن الرسالة هي رسالة نتائج ووردل
    if "Your group is on a" in message.content and "yesterday's results" in message.content:
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)

        if not winner_role:
            print("خطأ: لم يتم العثور على الرول. تأكد من الـ ID.")
            return

        # 1. سحب الرول من الجميع (تصفير الفائزين السابقين)
        for member in winner_role.members:
            try:
                await member.remove_roles(winner_role)
            except Exception as e:
                print(f"لم أتمكن من سحب الرول من {member.name}: {e}")

        # 2. استخراج الفائزين من السطر اللي فيه التاج 👑
        winners_mentions = []
        lines = message.content.split('\n')
        
        for line in lines:
            if "👑" in line:
                # استخراج كل الـ IDs الموجودة في السطر
                user_ids = re.findall(r'<@!?(\d+)>', line)
                for u_id in user_ids:
                    member = guild.get_member(int(u_id))
                    if member:
                        try:
                            await member.add_roles(winner_role)
                            winners_mentions.append(f"<@{u_id}>")
                        except Exception as e:
                            print(f"فشل إعطاء الرول لـ {member.name}: {e}")
                break # نوقف بحث بعد ما نلقى سطر التاج

        # 3. إرسال رسالة التهنئة
        if winners_mentions:
            mentions_str = " ".join(winners_mentions)
            response = f"مبروك تاج ووردل لكلمة امس 👑 :\n{mentions_str}"
            await message.channel.send(response)
        else:
            print("لم يتم العثور على منشنز في سطر التاج.")

client.run(TOKEN)