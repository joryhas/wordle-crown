import discord
import re
import os

# --- الإعدادات ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1466614946233057291 
APP_ID = 1211781489931452447          
MY_ID = 831989224101773372 

GIRL_ROLE_ID = 1413283305167654914 
MONKEY_BOY_ROLE_ID = 1442629105127526481   
MONKEY_GIRL_ROLE_ID = 1461160132359753895   
ROLE_TO_ADD_EXTRA = 1426382504427917374  
ROLE_TO_REMOVE = 774892842736549918 
# -----------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'--- البوت شغال وجاهز! ---')

@client.event
async def on_message(message):
    if message.author == client.user: return

    # استخراج النص سواء كان رسالة عادية أو داخل Embed
    content = message.content
    if not content and message.embeds:
        # إذا كانت الرسالة Embed، نأخذ النص من الوصف (Description) أو العنوان
        content = message.embeds[0].description or ""
        if not content: content = message.embeds[0].title or ""

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

    # --- نظام ووردل التلقائي ---
    if message.author.id == APP_ID and "Your group is on a" in content:
        guild = message.guild
        winner_role, m_boy, m_girl = guild.get_role(WINNER_ROLE_ID), guild.get_role(MONKEY_BOY_ROLE_ID), guild.get_role(MONKEY_GIRL_ROLE_ID)
        
        # تصفير الرولات
        for r in [winner_role, m_boy, m_girl]:
            if r:
                for member in r.members:
                    try: await member.remove_roles(r)
                    except: continue

        lines = content.split('\n')
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
        
        if legit_winners:
            await message.channel.send(f"مبروك تاج ووردل لكلمة امس 👑 :\n{' '.join(legit_winners)}")
        if cheaters_mentions:
            await message.channel.send(f"نتائج التحقيق أثبتت مخالفتك لقوانين اللعب النظيف ونتيجةً لذلك تم تحويلك الى قرد/ة لمدة 24 ساعة 🐒 :\n{' '.join(cheaters_mentions)}")


client.run(TOKEN)