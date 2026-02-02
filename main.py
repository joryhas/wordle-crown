import discord
import re
import os

# --- الإعدادات ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1467641677199184227 # رول التاج
APP_ID = 831989224101773372          # ID تطبيق ووردل

# --- إعدادات العقوبة ---
MONKEY_ROLE_ID = 1467641757385883841  # ID رول القرد 🐒
ROLE_TO_REMOVE_1 = 1434608888145248257 # ID الرول الأول اللي تبي تسحبه
ROLE_TO_REMOVE_2 = 1461747562808606884 # ID الرول الثاني اللي تبي تسحبه
# -----------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author.id != APP_ID:
        return

    if "Your group is on a" in message.content:
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)
        monkey_role = guild.get_role(MONKEY_ROLE_ID)
        
        # مصفوفات لتخزين المنشنز
        cheaters_mentions = []
        legit_winners_mentions = []

        # 1. تصفير رول التاج من الجميع أولاً
        for member in winner_role.members:
            try: await member.remove_roles(winner_role)
            except: continue

        lines = message.content.split('\n')
        
        for line in lines:
            match = re.search(r'(\d)/6', line)
            if match:
                attempts = int(match.group(1))
                user_ids = re.findall(r'<@!?(\d+)>', line)
                
                # --- حالة الغش (1/6) ---
                if attempts == 1:
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member:
                                # سحب الرولين وإضافة رول القرد
                                roles_to_del = [guild.get_role(ROLE_TO_REMOVE_1), guild.get_role(ROLE_TO_REMOVE_2)]
                                for r in roles_to_del:
                                    if r: await member.remove_roles(r)
                                
                                if monkey_role: await member.add_roles(monkey_role)
                                cheaters_mentions.append(f"<@{u_id}>")
                        except: continue
                    continue # كمل للأدوار اللي بعدها عشان نلقى الفائز الشرعي

                # --- حالة الفوز الشرعي (أول سطر بعد الـ 1/6) ---
                if not legit_winners_mentions: # لضمان أخذ أول سطر متاح فقط
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member:
                                await member.add_roles(winner_role)
                                legit_winners_mentions.append(f"<@{u_id}>")
                        except: continue
                    if legit_winners_mentions:
                        # لقينا الفائزين الشرعيين، ما نحتاج نمر على باقي الأسطر
                        pass 

        # --- إرسال الرسائل ---
        
     

        # 2. رسالة التاج (للفائزين الشرعيين)
        if legit_winners_mentions:
            winners_str = " ".join(legit_winners_mentions)
            await message.channel.send(f"مبروك تاج ووردل لكلمة امس 👑 :\n{winners_str}")
            
               # 1. رسالة العقوبة (إذا فيه غشاشين)
        if cheaters_mentions:
            cheaters_str = " ".join(cheaters_mentions)
            penalty_msg = f"نتائج التحقيق أثبتت مخالفتك لقوانين اللعب النظيف ونتيجةً لذلك تم تحويلك الى قرد لمدة 24 ساعة 🐒 :\n{cheaters_str}"
            await message.channel.send(penalty_msg)

client.run(TOKEN)