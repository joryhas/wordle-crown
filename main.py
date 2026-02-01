import discord
import re
import os

# --- الإعدادات ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1467466259787546823
APP_ID = 831989224101773372  # استبدل هذا بـ ID تطبيق ووردل
# -----------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'---')
    print(f'البوت شغال وجاهز!')
    print(f'مراقبة التطبيق ID: {APP_ID}')
    print(f'---')

@client.event
async def on_message(message):
    # التأكد أن الرسالة من تطبيق ووردل حصراً
    if message.author.id != APP_ID:
        return

    # التأكد من وجود نص النتائج
    if "Your group is on a" in message.content:
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)
        if not winner_role:
            print("خطأ: لم يتم العثور على الرول.")
            return

        # 1. سحب الرول من الجميع (تصفير)
        for member in winner_role.members:
            try:
                await member.remove_roles(winner_role)
            except:
                continue

        # 2. تحليل الأسطر وتجاهل 1/6
        winners_mentions = []
        lines = message.content.split('\n')
        
        for line in lines:
            # البحث عن نمط المحاولات (رقم من 1 إلى 6)
            match = re.search(r'(\d)/6', line)
            if match:
                attempts = int(match.group(1))
                
                # إذا جابها من أول مرة (غشاش أو محظوظ بزيادة)، نتخطى السطر
                if attempts == 1:
                    continue
                
                # أول سطر شرعي نقابله (2 أو أكثر) نعتبر أصحابه هم الفائزين
                user_ids = re.findall(r'<@!?(\d+)>', line)
                for u_id in user_ids:
                    try:
                        # fetch_member يضمن الحصول على البيانات حتى لو العضو أوفلاين
                        member = await guild.fetch_member(int(u_id))
                        if member:
                            await member.add_roles(winner_role)
                            winners_mentions.append(f"<@{u_id}>")
                    except:
                        continue
                
                # بمجرد العثور على أول فائزين (الأفضل بعد 1/6)، نتوقف عن قراءة باقي الأسطر
                if winners_mentions:
                    break

        # 3. إرسال رسالة التهنئة بالصيغة المطلوبة
        if winners_mentions:
            mentions_str = " ".join(winners_mentions)
            response = f"مبروك تاج ووردل لكلمة امس 👑 :\n{mentions_str}"
            await message.channel.send(response)

client.run(TOKEN)