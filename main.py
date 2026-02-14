import discord
import re
import os

# --- الإعدادات الثابتة ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1466614946233057291 
APP_ID = 1211781489931452447          
MY_ID = 831989224101773372 

GIRL_ROLE_ID = 1413283305167654914 
MONKEY_BOY_ROLE_ID = 1442629105127526481   
MONKEY_GIRL_ROLE_ID = 1461160132359753895   
ROLE_TO_ADD_EXTRA = 1426382504427917374  
ROLE_TO_REMOVE = 774892842736549918 

# --- قناة الإخراج (Output Channel) ---
OUTPUT_CHANNEL_ID = 779692039352221698 
# -----------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'--- البوت متصل الآن وجاهز للإرسال في الروم المحددة ---')

@client.event
async def on_message(message):
    if message.author == client.user: return

    # جلب قناة الإخراج المحددة
    output_channel = client.get_channel(OUTPUT_CHANNEL_ID)
    if not output_channel:
        output_channel = message.channel # خطة بديلة إذا لم يجد القناة

    # --- كوماند !تاج (يدوي) ---
    if message.content.startswith('!تاج'):
        if message.author.id != MY_ID: return
        if not message.mentions: return
        
        guild = message.guild
        winner_role = guild.get_role(WINNER_ROLE_ID)
        if winner_role:
            for member in winner_role.members:
                try: await member.remove_roles(winner_role)
                except: continue
            
            mentions_list = []
            for member in message.mentions:
                try:
                    await member.add_roles(winner_role)
                    mentions_list.append(member.mention)
                except: continue
            
            if mentions_list:
                await output_channel.send(f"تم منح التاج يدوياً بواسطة الإدارة 👑 :\n{' '.join(mentions_list)}")
        return

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
        await output_channel.send("تم حذف الرولات الغير مطلوبة وارجاع الرولات المأخوذة ✅")
        return

    # --- نظام ووردل التلقائي ---
    if message.author.id == APP_ID and "Your group is on a" in message.content:
        guild = message.guild
        winner_role, m_boy, m_girl = guild.get_role(WINNER_ROLE_ID), guild.get_role(MONKEY_BOY_ROLE_ID), guild.get_role(MONKEY_GIRL_ROLE_ID)
        
        # تصفير كل شيء
        for r in [winner_role, m_boy, m_girl]:
            if r:
                for m in r.members:
                    try: await m.remove_roles(r)
                    except: continue

        lines = message.content.split('\n')
        cheaters, legit = [], []

        for line in lines:
            match = re.search(r'(\d)/6', line)
            if match:
                attempts, u_ids = int(match.group(1)), re.findall(r'<@!?(\d+)>', line)
                if attempts == 1:
                    for u_id in u_ids:
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
                                cheaters.append(f"<@{u_id}>")
                        except: continue
                    continue 

                if not legit:
                    for u_id in u_ids:
                        try:
                            member = await guild.fetch_member(int(u_id))
                            if member and winner_role:
                                await member.add_roles(winner_role)
                                legit.append(f"<@{u_id}>")
                        except: continue
                    if legit: break

        if cheaters:
            await output_channel.send(f"نتائج التحقيق أثبتت مخالفتك لقوانين اللعب النظيف ونتيجةً لذلك تم تحويلك الى قرد/ة لمدة 24 ساعة 🐒 :\n{' '.join(cheaters)}")
        if legit:
            await output_channel.send(f"مبروك تاج ووردل لكلمة امس 👑 :\n{' '.join(legit)}")

client.run(TOKEN)