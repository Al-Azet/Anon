import logging
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from telegram.ext.webhook import WebhookRequestHandler
from http.server import BaseHTTPRequestHandler
import json

# Gunakan variabel lingkungan
TOKEN = os.environ.get("BOT_TOKEN", "7612315280:AAGUX3iCRGp20rkGbrYhhdiYbLkafrkDndU")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Struktur data
anonymous_queue = []
active_chats = {}
message_links = {}

def save_message_link(sender_id, sender_msg_id, partner_id, partner_msg_id):
    message_links.setdefault(sender_id, {})[sender_msg_id] = partner_msg_id
    message_links.setdefault(partner_id, {})[partner_msg_id] = sender_msg_id

def get_reply_to_msg_id(user_id, reply_to_message):
    if reply_to_message:
        local_id = reply_to_message.message_id
        return message_links.get(user_id, {}).get(local_id)
    return None

# Handler fungsi2 bot kamu (start, anonchat, dll) sama seperti sebelumnya.
# (Untuk ringkas, bagian ini bisa kamu copas langsung dari kode awal kamu.)

# Webhook handler
class VercelWebhookHandler(BaseHTTPRequestHandler):
    async def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(length)
        update = Update.de_json(json.loads(body), context.bot)
        await app.process_update(update)

# Bot setup
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("anonchat", anon_chat_start))
app.add_handler(CommandHandler("endchat", anon_chat_end))
app.add_handler(CommandHandler("next", anon_chat_next))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.Sticker(), handle_sticker))

async def handler(request):
    try:
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return {"statusCode": 200}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}
