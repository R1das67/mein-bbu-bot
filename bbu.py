import discord
from discord.ext import commands
from keep_alive import keep_alive

# === INTENTS EINSTELLEN ===
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.webhooks = True
intents.members = True

# === BOT-TOKEN DIREKT IM CODE (wenn du willst) ===
BOT_TOKEN = 'DEIN_BOT_TOKEN_HIER'  # ⚠ Setze hier deinen echten Token ein!

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN fehlt! Bitte direkt im Code eintragen.")

# === WHITELISTS DIREKT IM CODE ===
WHITELIST_WEBHOOK = [
    '843180408152784936',
    '662596869221908480',
    '1388295197691216030'
]

WHITELIST_INVITES = [
    '843180408152784936',
    '662596869221908480',
    '1388295197691216030'
]

# === BOT INITIALISIEREN ===
bot = commands.Bot(command_prefix='!', intents=intents)

# === BOT BEREIT ===
@bot.event
async def on_ready():
    print(f'✅ Bot ist online als {bot.user.name} ({bot.user.id})')

# === WEBHOOK-ÜBERWACHUNG ===
@bot.event
async def on_webhooks_update(channel):
    try:
        webhooks = await channel.guild.webhooks()
        audit_logs = channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.webhook_create)

        async for entry in audit_logs:
            webhook = next((w for w in webhooks if w.id == entry.target.id), None)
            if webhook:
                executor_id = str(entry.user.id)
                if executor_id not in WHITELIST_WEBHOOK:
                    await webhook.delete(reason='Nicht autorisierter Webhook-Ersteller')
                    print(f'🛑 Webhook von {executor_id} gelöscht (nicht in WHITELIST_WEBHOOK).')
                else:
                    print(f'✅ Webhook von {executor_id} ist erlaubt.')
    except Exception as e:
        print(f'⚠ Fehler beim Überprüfen der Webhooks: {e}')

# === NACHRICHTENÜBERWACHUNG ===
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Eigene Nachrichten ignorieren

    invite_keywords = ['discord.gg/', 'discord.com/invite/']
    if any(keyword in message.content.lower() for keyword in invite_keywords):
        author_id = str(message.author.id)
        if author_id not in WHITELIST_INVITES:
            try:
                await message.delete()
                print(f'🛑 Einladung von {author_id} gelöscht (nicht in WHITELIST_INVITES).')
            except Exception as e:
                print(f'⚠ Fehler beim Löschen der Einladung: {e}')

    await bot.process_commands(message)

# === KEEP-ALIVE SERVER STARTEN (z. B. für Replit) ===
keep_alive()

# === BOT STARTEN ===
bot.run(BOT_TOKEN)
