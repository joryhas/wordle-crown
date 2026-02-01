import discord
import re
import os

# --- الإعدادات ---
TOKEN = os.getenv('DISCORD_TOKEN')
WINNER_ROLE_ID = 1467466259787546823
APP_ID = 831989224101773372  # ID تطبيق ووردل
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
        if not winner_role: return

        # 1. سحب الرول من الجميع
        for member in winner_role.members:
            try: await member.remove_roles(winner_role)
            except: continue

        # 2. البحث عن أول "أفضل نتيجة" بشرط ألا تكون 1/6
        winners_mentions = []
        lines = message.content.split('\n')
        
        for line in lines:
            # نبحث عن نمط "رقم/6" في السطر (مثل 1/6 أو 2/6)
            match = re.search(r'(\d)/6', line)
            if match:
                attempts = int(match.group(1))
                
                # إذا كانت المحاولة 1/6، نتجاهل السطر ونكمل للي بعده
                if attempts == 1:
                    continue
                
                # أول سطر يقابلنا بعد الـ 1/6 هو الفائز (سواء كان 2/6 أو 3/6 إلخ)
                user_ids = re.findall(r'<@!?(\d+)>', line)
                for u_id in user_ids:
                    try:
                        member = await guild.fetch_member(int(u_id))
                        if member:
                            await member.add_roles(winner_role)
                            winners_mentions.append(f"<@{u_id}>")
                    except: continue
                
                # بمجرد ما لقينا أول "فائزين شرعيين"، نوقف البحث
                if winners_mentions:
                    break

        # 3. إرسال التهنئة
        if winners_mentions:
            mentions_str = " ".join(winners_mentions)
            response = f"مبروك تاج ووردل (المحاولات الشرعية) 👑 :\n{mentions_str}"
            await message.channel.send(response)

client.run(TOKEN)