import discord
import re
import os

# --- الإعدادات ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1466614946233057291
# حط هنا الـ Application ID الخاص ببرنامج ووردل (تلقاه في بروفايل الـ App)
APP_ID = 1211781489931452447  
# -----------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'---')
    print(f'البوت شغال وجاهز لمراقبة تطبيق ووردل!')
    print(f'اسم البوت: {client.user.name}')
    print(f'---')

@client.event
async def on_message(message):
    # 1. التحقق من أن مرسل الرسالة هو الـ App المطلوب
    # في ديسكورد، الـ App ID هو نفسه الـ author.id في أغلب الحالات
    if message.author.id != APP_ID:
        return

    # 2. التحقق من محتوى الرسالة (تأكد أن النص مطابق لما يرسله الـ App)
    if "Your group is on a" in message.content:
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)

        if not winner_role:
            print("خطأ: رول التاج غير موجود، تأكد من الـ ID.")
            return

        # 3. سحب الرول من الفائزين السابقين
        for member in winner_role.members:
            try:
                await member.remove_roles(winner_role)
            except:
                continue

        # 4. البحث عن سطر التاج 👑 واستخراج الفائزين
        winners_mentions = []
        lines = message.content.split('\n')
        
        for line in lines:
            if "👑" in line:
                # استخراج الـ IDs من المنشنز الموجودة في السطر
                user_ids = re.findall(r'<@!?(\d+)>', line)
                for u_id in user_ids:
                    # fetch_member أفضل من get_member في السيرفرات الكبيرة لضمان إيجاد العضو
                    try:
                        member = await guild.fetch_member(int(u_id))
                        if member:
                            await member.add_roles(winner_role)
                            winners_mentions.append(f"<@{u_id}>")
                    except:
                        continue
                break

        # 5. إرسال رسالة التهنئة
        if winners_mentions:
            mentions_str = " ".join(winners_mentions)
            response = f"مبروك تاج ووردل لكلمة امس 👑 :\n{mentions_str}"
            await message.channel.send(response)

client.run(TOKEN)