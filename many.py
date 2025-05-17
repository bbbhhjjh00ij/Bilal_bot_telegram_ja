import os
import json
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# بيانات البوت
TOKEN = "7453518539:AAGaUdf10iCqauTXGJfGDxOHel_xzv3T4CI"
ADMIN_ID = 7971415230

# تحميل المستخدمين من ملف JSON
def load_users():
    try:
        with open("users.json", "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

# حفظ المستخدمين إلى ملف JSON
def save_users():
    with open("users.json", "w") as f:
        json.dump(list(users_db), f)

# قاعدة بيانات المستخدمين
users_db = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        users_db.add(user.id)
        save_users()

        welcome_text = (
            "🌟 *Welcome to ID Extractor Bot!* 🤖\n\n"
            "This bot helps you get your Telegram information easily.\n"
            "• Get your Telegram ID\n"
            "• View your account details\n"
            "• Copy your ID with one click\n\n"
            "Your information will appear in the next message.\n"
            "Note: Information message will be deleted after 1 hour."
        )

        await update.message.reply_text(welcome_text, parse_mode='Markdown')

        info_text = (
            "👤 *Your Information:*\n\n"
            f"*Name:* {user.first_name}\n"
            f"*Username:* @{user.username if user.username else 'None'}\n"
            f"*ID:* `{user.id}`\n\n"
            "⏳ _This message will delete in 1 hour_"
        )

        info_message = await update.message.reply_text(info_text, parse_mode='Markdown')

        if user.id != ADMIN_ID:
            admin_text = (
                "📱 *New User Alert!*\n\n"
                f"*Name:* {user.first_name}\n"
                f"*Username:* @{user.username if user.username else 'None'}\n"
                f"*ID:* `{user.id}`\n"
                f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode='Markdown')

        await asyncio.sleep(3600)
        try:
            await info_message.delete()
        except Exception as e:
            logger.error(f"Error deleting info message: {e}")
    except Exception as e:
        logger.error(f"Error in start: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    stats_text = (
        "📊 *Bot Statistics*\n\n"
        f"*Total Users:* {len(users_db)}\n"
        f"*Last Updated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def bilal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ *Please provide a message to broadcast.*",
            parse_mode='Markdown'
        )
        return

    message = ' '.join(context.args)
    success = 0
    failed = 0

    status_msg = await update.message.reply_text(
        "🚀 *Broadcasting message...*",
        parse_mode='Markdown'
    )

    for user_id in users_db:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Error sending message to user {user_id}: {e}")

    report = (
        "📬 *Broadcast Complete*\n\n"
        f"✅ *Successful:* {success}\n"
        f"❌ *Failed:* {failed}\n"
        f"📊 *Total:* {success + failed}"
    )

    await status_msg.edit_text(report, parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("bilal", bilal))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
        
