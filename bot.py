import os
import sys

# تثبيت المكتبات المطلوبة
def install_packages():
    try:
        import telegram
    except ImportError:
        os.system('pip install python-telegram-bot')

install_packages()

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# المتغيرات الأساسية
TOKEN = "7453518539:AAGaUdf10iCqauTXGJfGDxOHel_xzv3T4CI"
ADMIN_ID = 7971415230

# قائمة المستخدمين
users_db = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        users_db.add(user.id)  # إضافة المستخدم إلى قاعدة البيانات
        
        # رسالة الترحيب
        welcome_text = (
            "🌟 *Welcome to ID Extractor Bot!* 🤖\n\n"
            "This bot helps you get your Telegram information easily.\n"
            "• Get your Telegram ID\n"
            "• View your account details\n"
            "• Copy your ID with one click\n\n"
            "Your information will appear in the next message.\n"
            "Note: Information message will be deleted after 1 hour."
        )
        
        # إرسال رسالة الترحيب
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown'
        )
        
        # رسالة المعلومات
        info_text = (
            "👤 *Your Information:*\n\n"
            f"*Name:* {user.first_name}\n"
            f"*Username:* @{user.username if user.username else 'None'}\n"
            f"*ID:* `{user.id}`\n\n"
            "⏳ _This message will delete in 1 hour_"
        )
        
        # إرسال رسالة المعلومات
        info_message = await update.message.reply_text(
            info_text,
            parse_mode='Markdown'
        )
        
        # إرسال إشعار للمشرف إذا لم يكن هو نفس المستخدم
        if user.id != ADMIN_ID:
            admin_text = (
                "📱 *New User Alert!*\n\n"
                f"*Name:* {user.first_name}\n"
                f"*Username:* @{user.username if user.username else 'None'}\n"
                f"*ID:* `{user.id}`\n"
                f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text,
                parse_mode='Markdown'
            )
        
        # حذف رسالة المعلومات بعد ساعة
        await asyncio.sleep(3600)
        try:
            await info_message.delete()
        except Exception as e:
            logger.error(f"Error deleting info message: {e}")
            
    except Exception as e:
        logger.error(f"Error in start: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return  # إذا لم يكن هو المشرف لا يعرض الإحصائيات
        
        stats_text = (
            "📊 *Bot Statistics*\n\n"
            f"*Total Users:* {len(users_db)}\n"  # عدد المستخدمين الفعليين
            f"*Last Updated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await update.message.reply_text(
            stats_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in stats: {e}")

async def bilal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
        
        # إرسال الرسالة لجميع المستخدمين
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
        
        # تقرير نتائج البث
        report = (
            "📬 *Broadcast Complete*\n\n"
            f"✅ *Successful:* {success}\n"
            f"❌ *Failed:* {failed}\n"
            f"📊 *Total:* {success + failed}"
        )
        
        await status_msg.edit_text(
            report,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in bilal: {e}")

def main():
    try:
        # إنشاء التطبيق
        print("Starting bot...")
        app = Application.builder().token(TOKEN).build()
        
        # إضافة الأوامر
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("stats", stats))
        app.add_handler(CommandHandler("bilal", bilal))
        
        # تشغيل البوت
        print("Bot is running...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
