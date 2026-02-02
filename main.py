import discord
import re
import os

# --- الإعدادات (نفس بياناتك) ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1467641677199184227 # رول التاج
APP_ID = 831989224101773372          # ID تطبيق ووردل

# --- إعدادات العقوبة ---
ROLE_TO_ADD_1 = 1467641757385883841  # ID رول القرد 🐒 (سيتم إضافته)
ROLE_TO_ADD_2 = 1461747562808606884  # ID رول إضافي للعقوبة (سيتم إضافته)
ROLE_TO_REMOVE = 1434608888145248257 # ID الرول الذي سيتم حذفه من الغشاش
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
    print(f'مراقبة تطبيق ووردل ID: {APP_ID}')
    print(f'---')

@client.event
async def on_message(message):
    # 1. التحقق من المرسل (التأكد أنه تطبيق ووردل)
    if message.author.id != APP_ID:
        return

    # 2. التحقق من محتوى الرسالة
    if "Your group is on a" in message.content:
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)
        
        cheaters_mentions = []
        legit_winners_mentions = []

        # سحب رول التاج من الجميع قبل التحديث
        if winner_role:
            for member in winner_role.members:
                try:
                    await member.remove_roles(winner_role)
                except:
                    continue

        lines = message.content.split('\n')
        
        for line in lines:
            match = re.search(r'(\d)/6', line)
            if match:
                attempts = int(match.group(1))
                user_ids = re.findall(r'<@!?(\d+)>', line)
                
                # حالة الغش (1/6)
                if attempts == 1:
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member:
                                # إضافة الرولين المحددين
                                r_add1 = guild.get_role(ROLE_TO_ADD_1)
                                r_add2 = guild.get_role(ROLE_TO_ADD_2)
                                if r_add1: await member.add_roles(r_add1)
                                if r_add2: await member.add_roles(r_add2)
                                
                                # حذف الرول المحدد
                                r_del = guild.get_role(ROLE_TO_REMOVE)
                                if r_del: await member.remove_roles(r_del)
                                
                                cheaters_mentions.append(f"<@{u_id}>")
                        except:
                            continue
                    continue 

                # حالة الفوز الشرعي (أول سطر بعد الـ 1/6)
                if not legit_winners_mentions:
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member:
                                if winner_role: await member.add_roles(winner_role)
                                legit_winners_mentions.append(f"<@{u_id}>")
                        except:
                            continue
                    if legit_winners_mentions:
                        # نتوقف عن قراءة الأسطر التالية لأننا وجدنا أصحاب أقل محاولات شرعية
                        pass

        # 3. إرسال الرسائل في القناة
        # رسالة التاج 👑
        if legit_winners_mentions:
            winners_str = " ".join(legit_winners_mentions)
            response = f"مبروك تاج ووردل لكلمة امس 👑 :\n{winners_str}"
            await message.channel.send(response)
        # رسالة الغشاشين 🐒
        if cheaters_mentions:
            cheaters_str = " ".join(cheaters_mentions)
            penalty_msg = f"نتائج التحقيق أثبتت مخالفتك لقوانين اللعب النظيف ونتيجةً لذلك تم تحويلك الى قرد لمدة 24 ساعة 🐒 :\n{cheaters_str}"
            await message.channel.send(penalty_msg)

        

client.run(TOKEN)