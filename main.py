import discord
import re
import os

# --- الإعدادات ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1466614946233057291  
APP_ID = 831989224101773372          
MY_ID = 831989224101773372   

# --- رولات الجنس ---
GIRL_ROLE_ID = 1413283305167654914 # <--- حط هنا ID رول البنات

# --- إعدادات العقوبة ---
MONKEY_BOY_ROLE_ID = 1442629105127526481  # رول قرد 🐒
MONKEY_GIRL_ROLE_ID = 1461160132359753895  # <--- حط هنا ID رول قردة 🐒
ROLE_TO_ADD_EXTRA = 1426382504427917374   # الرول الإضافي (اللي يضاف للكل)
ROLE_TO_REMOVE = 774892842736549918      # الرول المأخوذ
# -----------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'--- البوت شغال بنظام القرد والقردة! ---')

@client.event
async def on_message(message):
    if message.author == client.user: return

    # --- كوماند !استعادة ---
    if message.content.startswith('!استعادة'):
        if message.author.id != MY_ID: return
        guild = message.guild
        r_m_b = guild.get_role(MONKEY_BOY_ROLE_ID)
        r_m_g = guild.get_role(MONKEY_GIRL_ROLE_ID)
        r_add_ex = guild.get_role(ROLE_TO_ADD_EXTRA)
        r_taken = guild.get_role(ROLE_TO_REMOVE)
        
        for member in message.mentions:
            try:
                if r_m_b: await member.remove_roles(r_m_b)
                if r_m_g: await member.remove_roles(r_m_g)
                if r_add_ex: await member.remove_roles(r_add_ex)
                if r_taken: await member.add_roles(r_taken)
            except: continue
        await message.channel.send("تم تنظيف الرولات وإعادة الوضع للطبيعي ✅")
        return

    # --- نظام ووردل التلقائي ---
    if message.author.id == APP_ID and "Your group is on a" in message.content:
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)
        m_boy_role = guild.get_role(MONKEY_BOY_ROLE_ID)
        m_girl_role = guild.get_role(MONKEY_GIRL_ROLE_ID)
        
        # 1. تصفير التيجان والقرود والبنوات من السيرفر
        roles_to_clear = [winner_role, m_boy_role, m_girl_role]
        for r in roles_to_clear:
            if r:
                for member in r.members:
                    try: await member.remove_roles(r)
                    except: continue

        lines = message.content.split('\n')
        cheaters_mentions = []
        legit_winners_mentions = []

        for line in lines:
            match = re.search(r'(\d)/6', line)
            if match:
                attempts = int(match.group(1))
                user_ids = re.findall(r'<@!?(\d+)>', line)
                
                if attempts == 1: # الغشاشين
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member:
                                # شيك هل هي بنت؟
                                if any(r.id == GIRL_ROLE_ID for r in member.roles):
                                    if m_girl_role: await member.add_roles(m_girl_role)
                                else:
                                    if m_boy_role: await member.add_roles(m_boy_role)
                                
                                # الرول الإضافي والحذف (للجنسين)
                                r_extra = guild.get_role(ROLE_TO_ADD_EXTRA)
                                r_del = guild.get_role(ROLE_TO_REMOVE)
                                if r_extra: await member.add_roles(r_extra)
                                if r_del: await member.remove_roles(r_del)
                                
                                cheaters_mentions.append(f"<@{u_id}>")
                        except: continue
                    continue 

                if not legit_winners_mentions: # الفائز الشرعي
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member and winner_role:
                                await member.add_roles(winner_role)
                                legit_winners_mentions.append(f"<@{u_id}>")
                        except: continue
                    if legit_winners_mentions: break

        # إرسال الرسائل

        if legit_winners_mentions:
            await message.channel.send(f"مبروك تاج ووردل لكلمة امس 👑 :\n{' '.join(legit_winners_mentions)}")
            
        if cheaters_mentions:
            await message.channel.send(f"نتائج التحقيق أثبتت مخالفتك لقوانين اللعب النظيف ونتيجةً لذلك تم تحويلك الى قرد/ة لمدة 24 ساعة 🐒 :\n{' '.join(cheaters_mentions)}")            

client.run(TOKEN)