import discord
from discord.ext import commands
from keep_alive import keep_alive
import asyncio
from collections import defaultdict
from datetime import timedelta

# === INTENTS EINSTELLEN ===
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.webhooks = True
intents.members = True
intents.guild_messages = True

# === BOT-TOKEN ===
BOT_TOKEN = 'DEIN_BOT_TOKEN_HIER'  # ⚠ Ersetze durch deinen echten Token

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN fehlt! Bitte direkt im Code eintragen.")

# === ZENTRALE WHITELIST ===
WHITELIST = ['843180408152784936', '662596869221908480', '1388295197691216030']

# === LINK-VERSUCH-SPEICHER ===
link_versuche = defaultdict(int)

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
                if executor_id not in WHITELIST:
                    await webhook.delete(reason='Nicht autorisierter Webhook-Ersteller')
                    print(f'🛑 Webhook von {executor_id} gelöscht (nicht in WHITELIST).')
                else:
                    print(f'✅ Webhook von {executor_id} ist erlaubt.')
    except Exception as e:
        print(f'⚠ Fehler beim Überprüfen der Webhooks: {e}')

# === KANAL/ROLLEN-ERSTELLUNG & LÖSCHUNG ÜBERWACHEN ===
@bot.event
async def on_guild_channel_create(channel):
    await check_guild_modification(channel.guild, discord.AuditLogAction.channel_create)

@bot.event
async def on_guild_channel_delete(channel):
    await check_guild_modification(channel.guild, discord.AuditLogAction.channel_delete)

@bot.event
async def on_guild_role_create(role):
    await check_guild_modification(role.guild, discord.AuditLogAction.role_create)

@bot.event
async def on_guild_role_delete(role):
    await check_guild_modification(role.guild, discord.AuditLogAction.role_delete)

async def check_guild_modification(guild, action):
    try:
        async for entry in guild.audit_logs(limit=1, action=action):
            user = entry.user
            if str(user.id) not in WHITELIST:
                await guild.kick(user, reason=f'🔨 Nicht autorisierte Aktion: {action.name}')
                print(f'🛑 {user} wurde gekickt wegen {action.name}')
    except Exception as e:
        print(f'⚠ Fehler beim Kick-Vorgang: {e}')

# === NACHRICHTENÜBERWACHUNG ===
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    author_id = str(message.author.id)
    invite_keywords = ['discord.gg/', 'discord.com/invite/']

    if any(keyword in message.content.lower() for keyword in invite_keywords):
        if author_id not in WHITELIST:
            link_versuche[author_id] += 1
            try:
                await message.delete()
                print(f'🛑 Einladung von {author_id} gelöscht. Versuch {link_versuche[author_id]}/3')
            except Exception as e:
                print(f'⚠ Fehler beim Löschen der Einladung: {e}')

            if link_versuche[author_id] >= 3:
                try:
                    timeout_duration = timedelta(hours=1)
                    await message.author.timeout(timeout_duration, reason='🚫 Spam von Einladungslinks')
                    print(f'⏱️ {author_id} wurde für 1h getimeoutet wegen Linkspam.')
                    link_versuche[author_id] = 0  # zurücksetzen
                except Exception as e:
                    print(f'⚠ Fehler beim Timeout: {e}')

    await bot.process_commands(message)

# === KEEP-ALIVE STARTEN (z. B. für Replit) ===
keep_alive()

# === BOT STARTEN ===
bot.run(BOT_TOKEN)
