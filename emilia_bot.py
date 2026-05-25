import asyncio
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === НАЛАШТУВАННЯ ===
TELEGRAM_TOKEN = "8834903933:AAEZzduAbyXKYU_tL0OPWPigaiQpYr5GJIg"
GEMINI_API_KEY = "AIzaSyDrhVdeDAHTDBXldb-GN1WdBj0P8MVOrS4"

EMILIA_CHAT_ID = None

# === ГЕНЕРАЦІЯ ПОВІДОМЛЕННЯ ===
def generate_morning_message():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    data = {
        "contents": [{
            "parts": [{
                "text": (
                    "Ти ніжний бот для дівчини на ім'я Емілія. "
                    "Напиши їй ранкове повідомлення українською мовою. "
                    "Воно має містити: комплімент, побажання гарного дня, "
                    "одну корисну пораду та позитивне передбачення на день. "
                    "Тон — теплий, щирий. Використовуй емодзі. Максимум 150 слів."
                )
            }]
        }]
    }
    response = requests.post(url, json=data)
    result = response.json()
    if "candidates" not in result:
        return "🌸 Емілія, доброго ранку! Сьогодні ти особлива і неповторна 💛 Гарного дня!"
    return result["candidates"][0]["content"]["parts"][0]["text"]

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global EMILIA_CHAT_ID
    EMILIA_CHAT_ID = update.effective_chat.id
    await update.message.reply_text(
        "Привіт, Емілія! 🌸\n"
        "Я твій особистий бот 💌\n"
        "Щоранку о 09:00 я буду надсилати тобі щось особливе ✨\n"
        "Але в мене є ліміт(\n"
        "Так шо не наглій)\n"
    )

# === /message ===
async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Генерую для тебе повідомлення... ✨")
    text = generate_morning_message()
    await update.message.reply_text(text)
    with open("sticker.webm", "rb") as sticker:
        await update.message.reply_sticker(sticker)

# === ЩОДЕННЕ ПОВІДОМЛЕННЯ ===
async def daily_message(app):
    if EMILIA_CHAT_ID:
        text = generate_morning_message()
        await app.bot.send_message(chat_id=EMILIA_CHAT_ID, text=text)

# === ЗАПУСК ===
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("message", send_now))

    # Кнопки меню
    await app.bot.set_my_commands([
        ("start", "🌸 Запустити бота"),
        ("message", "💌 Отримати повідомлення зараз"),
    ])

    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
    scheduler.add_job(daily_message, "cron", hour=9, minute=0, args=[app])
    scheduler.start()

    print("Бот Емілії запущено ✅")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())