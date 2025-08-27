import os
import logging
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "Bot is alive!"


def run():
    app.run(host='0.0.0.0', port=8080)


# اجرای Flask در یک Thread جدا
Thread(target=run).start()


# ---------------- تابع ترکیب ----------------
def combine_excels(file_list, output_file):
    dfs = []
    for f in file_list:
        dfs.append(pd.read_excel(f))
    combined = pd.concat(dfs, ignore_index=True)
    combined.to_excel(output_file, index=False)


# ---------------- تنظیمات ----------------
TOKEN = "8374560512:AAE-iBr8W6D1rQ-lZaNZaKuNjzb7KNuk31s"  # توکن رباتتو اینجا بذار
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ---------------- لاگ ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------- شروع ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 اکسل", callback_data="excel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! یکی از گزینه‌ها رو انتخاب کن:",
                                    reply_markup=reply_markup)


# ---------------- هندلر دکمه ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "excel":
        context.user_data["files"] = []  # لیست فایل‌های کاربر
        await query.message.reply_text(
            "📂 فایل‌های اکسل خودت رو یکی‌یکی بفرست.\nوقتی تموم شد روی دکمه زیر بزن:",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ ترکیب کن", callback_data="done")]]))

    elif query.data == "done":
        await done(update, context)


# ---------------- دریافت فایل ----------------
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = os.path.join(UPLOAD_DIR, update.message.document.file_name)
    await file.download_to_drive(file_path)

    # ذخیره اسم فایل برای همین کاربر
    if "files" not in context.user_data:
        context.user_data["files"] = []
    context.user_data["files"].append(file_path)

    await update.message.reply_text(
        f"✅ فایل {update.message.document.file_name} ذخیره شد.")


# ---------------- وقتی کاربر تموم کرد ----------------
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = context.user_data.get("files", [])
    if not files:
        await update.callback_query.message.reply_text(
            "❌ هیچ فایلی نفرستادی! اول فایل‌هات رو آپلود کن.")
        return

    await update.callback_query.message.reply_text("⏳ در حال ترکیب فایل‌ها...")

    try:
        output_file = "combined.xlsx"
        combine_excels(files, output_file)

        # فرستادن فایل خروجی
        await update.callback_query.message.reply_document(
            document=open(output_file, "rb"))
    except Exception as e:
        logger.error(e)
        await update.callback_query.message.reply_text("⚠️ مشکلی پیش اومد!")
    finally:
        # پاک کردن فایل‌های آپلودی برای تمیز موندن
        for f in files:
            if os.path.exists(f):
                os.remove(f)
        context.user_data["files"] = []


# ---------------- اجرای ربات ----------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("ربات روشن شد...")
    app.run_polling()


if __name__ == "__main__":
    main()
