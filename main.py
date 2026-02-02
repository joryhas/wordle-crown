import discord
import re
import os

# --- الإعدادات ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1467641677199184227 # رول التاج
APP_ID = 831989224101773372          # ID تطبيق ووردل

# --- إعدادات العقوبة (تعديل الإضافة والحذف) ---
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
    print(f'البوت شغال وجاهز بنظام العقوبات الجديد!')
    print(f'---')

@client.event
async def on_message(message):
    if message.author.id != APP_ID:
        return

    if "Your group is on a" in message.content:
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)
        
        cheaters_mentions = []
        legit_winners_mentions = []

        # 1. تصفير رول التاج من الجميع
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
                                # إضافة رولين
                                roles_to_add = [guild.get_role(ROLE_TO_ADD_1), guild.get_role(ROLE_TO_ADD_2)]
                                for r in roles_to_add:
                                    if r: await member.add_roles(r)
                                
                                # حذف رول واحد
                                r_to_del = guild.get_role(ROLE_TO_REMOVE)
                                if r_to_del: await member.remove_roles(r_to_del)
                                
                                cheaters_mentions.append(f"<@{u_id}>")
                        except: continue
                    continue 

                # --- حالة الفوز الشرعي ---
                if not legit_winners_mentions:
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member:
                                await member.add_roles(winner_role)
                                legit_winners_mentions.append(f"<@{u_id}>")
                        except: continue
                    if legit_winners_mentions:
                        pass 

        # --- إرسال الرسائل ---
         if legit_winners_mentions:
            winners_str = " ".join(legit_winners_mentions)
            await message.channel.send(f"مبروك تاج ووردل لكلمة امس 👑 :\n{winners_str}")
            
        if cheaters_mentions:
            cheaters_str = " ".join(cheaters_mentions)
            penalty_msg = f"نتائج التحقيق أثبتت مخالفتك لقوانين اللعب النظيف ونتيجةً لذلك تم تحويلك الى قرد لمدة 24 ساعة 🐒 :\n{cheaters_str}"
            await message.channel.send(penalty_msg)

       

client.run(TOKEN)