import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.webhooks = True
intents.members = True

# === KONFIGURATION via Umgebungsvariablen ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Whitelist als kommaseparierte Strings in Umgebungsvariable
WHITELIST_WEBHOOK = os.environ.get('843180408152784936','662596869221908480').split(',')
WHITELIST_INVITES = os.environ.get('843180408152784936','662596869221908480').split(',')

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot ist online als {bot.user.name} ({bot.user.id})')

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
                    print(f'🛑 Webhook von {executor_id} gelöscht (nicht in Whitelist).')
                else:
                    print(f'✅ Erlaubter Webhook von {executor_id}')
    except Exception as e:
        print(f'⚠ Fehler beim Webhook-Check: {e}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    invite_keywords = ['discord.gg/', 'discord.com/invite/']
    if any(keyword in message.content.lower() for keyword in invite_keywords):
        author_id = str(message.author.id)
        if author_id not in WHITELIST_INVITES:
            try:
                await message.delete()
                print(f'🛑 Einladung von {author_id} gelöscht (nicht in Whitelist).')
            except Exception as e:
                print(f'⚠ Fehler beim Löschen der Einladung: {e}')
    
    await bot.process_commands(message)

# Starte den Webserver für Keep-Alive
keep_alive()

bot.run(BOT_TOKEN)