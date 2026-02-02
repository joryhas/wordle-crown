import discord
import re
import os

# --- الإعدادات ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1467641677199184227 
APP_ID = 831989224101773372          
MY_ID = 831989224101773372  # الـ ID حقك للاستعادة

# --- إعدادات العقوبة ---
ROLE_TO_ADD_1 = 1467641757385883841  # رول القرد 🐒
ROLE_TO_ADD_2 = 1461747562808606884  # رول إضافي
ROLE_TO_REMOVE = 1434608888145248257 # الرول المأخوذ
# -----------------

ROLE_TO_ADD_3 = 1467641757385883841  # رول القرد 🐒
ROLE_TO_ADD_4 = 1434608888145248257  # رول إضافي
ROLE_TO_REMOVE1 =1461747562808606884  # الرول المأخوذ

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'--- البوت شغال وجاهز لتنظيف السيرفر من القرود! ---')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # --- كوماند !استعادة ---
    if message.content.startswith('!استعادة'):
        if message.author.id != MY_ID: return
        if not message.mentions:
            await message.channel.send("الرجاء منشن الأشخاص المطلوب استعادة رولاتهم.")
            return
        guild = message.guild
        r_a1, r_a2, r_t = guild.get_role(ROLE_TO_ADD_3), guild.get_role(ROLE_TO_ADD_4), guild.get_role(ROLE_TO_REMOVE1)
        for member in message.mentions:
            try:
                if r_a1: await member.remove_roles(r_a1)
                if r_a2: await member.remove_roles(r_a2)
                if r_t: await member.add_roles(r_t)
            except: continue
        await message.channel.send("تم حذف الرولات الغير مطلوبة وارجاع الرولات المأخوذة")
        return

    # --- نظام ووردل التلقائي ---
    if message.author.id == APP_ID and "Your group is on a" in message.content:
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)
        monkey_role = guild.get_role(ROLE_TO_ADD_1) # رول القرد
        
        cheaters_mentions = []
        legit_winners_mentions = []

        # 1. تصفير رول التاج من الجميع
        if winner_role:
            for member in winner_role.members:
                try: await member.remove_roles(winner_role)
                except: continue

        # 2. تصفير رول القرد من الجميع (الشرط الجديد اللي طلبته)
        if monkey_role:
            for member in monkey_role.members:
                try: await member.remove_roles(monkey_role)
                except: continue

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
                                r_a1 = guild.get_role(ROLE_TO_ADD_1) # القرد
                                r_a2 = guild.get_role(ROLE_TO_ADD_2)
                                if r_a1: await member.add_roles(r_a1)
                                if r_a2: await member.add_roles(r_a2)
                                r_del = guild.get_role(ROLE_TO_REMOVE)
                                if r_del: await member.remove_roles(r_del)
                                cheaters_mentions.append(f"<@{u_id}>")
                        except: continue
                    continue 

                # حالة الفوز الشرعي
                if not legit_winners_mentions:
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member:
                                if winner_role: await member.add_roles(winner_role)
                                legit_winners_mentions.append(f"<@{u_id}>")
                        except: continue
                    if legit_winners_mentions: break

        # إرسال الرسائل
        if legit_winners_mentions:
            winners_str = " ".join(legit_winners_mentions)
            await message.channel.send(f"مبروك تاج ووردل لكلمة امس 👑 :\n{winners_str}")
            
        if cheaters_mentions:
            cheaters_str = " ".join(cheaters_mentions)
            await message.channel.send(f"نتائج التحقيق أثبتت مخالفتك لقوانين اللعب النظيف ونتيجةً لذلك تم تحويلك الى قرد لمدة 24 ساعة 🐒 :\n{cheaters_str}")



client.run(TOKEN)