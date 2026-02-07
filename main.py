import discord
import re
import os
import asyncio
from datetime import datetime, timedelta
import pytz

# --- الإعدادات (نفس بياناتك بالضبط) ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1466614946233057291 
APP_ID = 1211781489931452447          
MY_ID = 831989224101773372 

GIRL_ROLE_ID = 1413283305167654914 
MONKEY_BOY_ROLE_ID = 1442629105127526481   
MONKEY_GIRL_ROLE_ID = 1461160132359753895   
ROLE_TO_ADD_EXTRA = 1426382504427917374  
ROLE_TO_REMOVE = 774892842736549918 

OUTPUT_CHANNEL_ID = 779692039352221698 
KSA = pytz.timezone('Asia/Riyadh')
# -----------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'--- البوت شغال وجاهز! ---')
    print(f'الإخراج موجه للقناة ID: {OUTPUT_CHANNEL_ID}')

@client.event
async def on_message(message):
    if message.author == client.user: return

    # تحديد قناة الرد (روم 2)
    output_channel = client.get_channel(OUTPUT_CHANNEL_ID)
    if not output_channel:
        output_channel = message.channel

    # --- كوماند !استعادة ---
    if message.content.startswith('!استعادة'):
        if message.author.id != MY_ID: return
        guild = message.guild
        r_m_b, r_m_g, r_add_ex, r_taken = guild.get_role(MONKEY_BOY_ROLE_ID), guild.get_role(MONKEY_GIRL_ROLE_ID), guild.get_role(ROLE_TO_ADD_EXTRA), guild.get_role(ROLE_TO_REMOVE)
        for member in message.mentions:
            try:
                if r_m_b: await member.remove_roles(r_m_b)
                if r_m_g: await member.remove_roles(r_m_g)
                if r_add_ex: await member.remove_roles(r_add_ex)
                if r_taken: await member.add_roles(r_taken)
            except: continue
        await message.channel.send("تم تنظيف الرولات وإعادة الوضع للطبيعي ✅")
        return

    # --- نظام ووردل التلقائي مع شرط الساعة 12 ---
    if message.author.id == APP_ID and "Your group is on a" in message.content:
        
        # فحص الوقت الحالي في السعودية
        now_ksa = datetime.now(KSA)
        
        # إذا وصلت الرسالة قبل الساعة 12 صباحاً (من الساعة 9 مساءً فما فوق)
        if now_ksa.hour >= 21:
            tomorrow = now_ksa + timedelta(days=1)
            midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            wait_seconds = (midnight - now_ksa).total_seconds()
            
            print(f"🕒 رسالة ووردل وصلت مبكراً ({now_ksa.strftime('%H:%M')}). الانتظار: {int(wait_seconds)} ثانية...")
            await asyncio.sleep(wait_seconds)
            print("🔔 حانت الساعة 12 صباحاً، جاري معالجة النتائج...")

        # تنفيذ المنطق الخاص بك بعد الانتظار
        guild = message.guild
        winner_role, m_boy, m_girl = guild.get_role(WINNER_ROLE_ID), guild.get_role(MONKEY_BOY_ROLE_ID), guild.get_role(MONKEY_GIRL_ROLE_ID)
        
        # تصفير الرولات من الجميع
        roles_to_clear = [winner_role, m_boy, m_girl]
        for r in roles_to_clear:
            if r:
                for member in r.members:
                    try: await member.remove_roles(r)
                    except: continue

        lines = message.content.split('\n')
        cheaters_mentions, legit_winners = [], []

        for line in lines:
            match = re.search(r'(\d)/6', line)
            if match:
                attempts, user_ids = int(match.group(1)), re.findall(r'<@!?(\d+)>', line)
                
                if attempts == 1:
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member:
                                if any(r.id == GIRL_ROLE_ID for r in member.roles):
                                    if m_girl: await member.add_roles(m_girl)
                                else:
                                    if m_boy: await member.add_roles(m_boy)
                                r_ex, r_de = guild.get_role(ROLE_TO_ADD_EXTRA), guild.get_role(ROLE_TO_REMOVE)
                                if r_ex: await member.add_roles(r_ex)
                                if r_de: await member.remove_roles(r_de)
                                cheaters_mentions.append(f"<@{u_id}>")
                        except: continue
                    continue 

                if not legit_winners:
                    for u_id in user_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member and winner_role:
                                await member.add_roles(winner_role)
                                legit_winners.append(f"<@{u_id}>")
                        except: continue
                    if legit_winners: break

        # إرسال الرسائل في روم 2
        if legit_winners:
            await output_channel.send(f"مبروك تاج ووردل لكلمة امس 👑 :\n{' '.join(legit_winners)}")        
        if cheaters_mentions:
            await output_channel.send(f"نتائج التحقيق أثبتت مخالفتك لقوانين اللعب النظيف ونتيجةً لذلك تم تحويلك الى قرد/ة لمدة 24 ساعة 🐒 :\n{' '.join(cheaters_mentions)}")

client.run(TOKEN)