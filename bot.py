import telebot
from combine_excel import combine_files
import os

TOKEN = "8374560512:AAE-iBr8W6D1rQ-lZaNZaKuNjzb7KNuk31s"  # ← اینجا توکن رباتتو بذار
bot = telebot.TeleBot(TOKEN)

UPLOAD_DIR = "temp"

# ساخت پوشه temp اگر وجود نداشت
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# دریافت فایل Excel
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_path = os.path.join(UPLOAD_DIR, message.document.file_name)
    with open(file_path, "wb") as f:
        f.write(downloaded_file)

    bot.reply_to(message, f"فایل دریافت شد: {message.document.file_name}\nمنتظر ترکیب فایل‌ها باشید...")

    # ترکیب همه فایل‌های موجود در temp
    files = [os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR)]
    combined_path = combine_files(files)

    if combined_path:
        with open(combined_path, "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.reply_to(message, "⚠️ هیچ داده‌ای برای ترکیب وجود نداشت.")


bot.infinity_polling()
