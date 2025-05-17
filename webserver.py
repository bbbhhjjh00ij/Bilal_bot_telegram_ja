from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
import asyncio
import logging
import os

# تهيئة اللوجينج
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# متغيرات بيئية (يمكنك ضبطها في Render أو .env)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")

# انشاء تطبيق FastAPI
app = FastAPI()

# انشاء بوت تيليجرام بتوكن
bot = Bot(token=BOT_TOKEN)

# انشاء التطبيق من مكتبة python-telegram-bot
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# مثال أمر /start بوت تيليجرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبا! هذا بوت تيليجرام احترافي باستخدام FastAPI.")

telegram_app.add_handler(CommandHandler("start", start))

# تشغيل بوت في الخلفية (دون حجب سيرفر FastAPI)
@app.on_event("startup")
async def on_startup():
    logger.info("Starting Telegram bot...")
    # تشغيل بوت التيليجرام في حدث غير متزامن
    asyncio.create_task(telegram_app.run_polling())

# نقطة استقبال Webhook (اختياري - إذا تستخدم Webhook)
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = Update.de_json(await request.json(), bot)
    await telegram_app.update_queue.put(update)
    return JSONResponse(content={"status": "ok"})

# صفحة رئيسية بسيطة
@app.get("/")
async def home():
    return {"message": "Telegram Bot Running with FastAPI!"}
    
