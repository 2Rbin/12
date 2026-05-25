import asyncio
import requests
import random
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, ReplyKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === НАЛАШТУВАННЯ ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

EMILIA_CHAT_ID = None
WAITING_MOOD = False

# === GEMINI ЗАПИТ ===
def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=data)
    result = response.json()
    if "candidates" not in result:
        return None
    return result["candidates"][0]["content"]["parts"][0]["text"]

# === ПОГОДА ===
def get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Kyiv&appid={WEATHER_API_KEY}&units=metric&lang=ua"
        r = requests.get(url).json()
        if "main" not in r:
            return "🌦 Погода тимчасово недоступна"
        temp = round(r["main"]["temp"])
        desc = r["weather"][0]["description"]
        feels = round(r["main"]["feels_like"])
        return f"🌦 Погода в Києві: {temp}°C, {desc}, відчувається як {feels}°C"
    except:
        return "🌦 Погода тимчасово недоступна"
# === РАНКОВЕ ПОВІДОМЛЕННЯ ===
def generate_morning_message():
    import random
    themes = [
        "зроби акцент на її красі та посмішці",
        "зроби акцент на її розумі та талантах",
        "зроби акцент на її доброті та теплоті",
        "зроби акцент на тому як вона надихає інших",
        "зроби акцент на її силі та впевненості",
        "зроби акцент на її унікальності та особливості",
        "зроби акцент на її позитивній енергії",
    ]
    theme = random.choice(themes)
    prompt = (
        f"Ти ніжний бот для дівчини на ім'я Емілія. {theme}. "
        "Напиши їй ранкове повідомлення українською мовою. "
        "Воно має містити: комплімент, побажання гарного дня, "
        "одну корисну пораду та позитивне передбачення на день. "
        "Тон — теплий, щирий. Використовуй емодзі. Максимум 150 слів. "
        "Кожного разу пиши абсолютно інше повідомлення!"
    )
    result = ask_gemini(prompt)
    if not result:
        fallbacks = [
            "🌸 Емілія, доброго ранку! Твоя посмішка освітлює весь день 💛",
            "🌺 Доброго ранку, Емілія! Ти неймовірна і особлива ✨",
            "🌷 Привіт, Емілія! Сьогодні буде чудовий день 💫",
            "🌼 Доброго ранку! Ти найкраща і найяскравіша 🌟",
        ]
        return random.choice(fallbacks)
    return result

# === ВЕЧІРНЄ ПОВІДОМЛЕННЯ ===
def generate_evening_message():
    prompt = (
        "Ти ніжний бот для дівчини на ім'я Емілія. "
        "Напиши їй вечірнє повідомлення українською мовою. "
        "Воно має містити: побажання на ніч, підсумок що день був гарним, "
        "маленький комплімент і побажання солодких снів. "
        "Тон — теплий, спокійний. Використовуй емодзі. Максимум 100 слів."
    )
    result = ask_gemini(prompt)
    if not result:
        return "🌙 Емілія, на добраніч! Ти сьогодні була чудовою 💫 Солодких снів!"
    return result

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global EMILIA_CHAT_ID
    EMILIA_CHAT_ID = update.effective_chat.id
    await update.message.reply_text(
        "Привіт, Емілія! 🌸\n"
        "Я твій особистий бот 💌\n"
        "Щоранку о 09:00 я буду надсилати тобі щось особливе ✨"
    )
    await app_ref.bot.set_my_commands([
        ("start", "🌸 Запустити бота"),
        ("message", "💌 Отримати повідомлення зараз"),
        ("porada", "💡 Отримати пораду"),
("nastrii", "🎵 Підбадьорення під настрій"),
("tyzhden", "📅 План на тиждень"),
    ])

# === /message ===
async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Генерую для тебе повідомлення... ✨")
    text = generate_morning_message()
    weather = get_weather()
    await update.message.reply_text(f"{text}\n\n{weather}")
    with open("sticker.webm", "rb") as sticker:
        await update.message.reply_sticker(sticker)

# === /порада ===
async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Думаю над порадою для тебе... 💡")
    prompt = (
        "Дай одну корисну, цікаву та практичну пораду для дівчини на ім'я Емілія. "
        "Тема може бути будь-яка: здоров'я, краса, стосунки, розвиток, мотивація. "
        "Українською мовою. Тон теплий. Використовуй емодзі. Максимум 100 слів."
    )
    result = ask_gemini(prompt)
    await update.message.reply_text(result or "💡 Порада дня: вір у себе, ти все зможеш!")

# === /настрій ===
async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global WAITING_MOOD
    WAITING_MOOD = True
    keyboard = [["😊 Чудово", "😐 Нормально", "😔 Сумно", "😤 Злюся"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Який у тебе зараз настрій? 🎵", reply_markup=markup)

# === /тиждень ===
async def week_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Генерую план на тиждень... 📅")
    prompt = (
        "Створи мотиваційний план на тиждень для дівчини на ім'я Емілія. "
        "Для кожного дня тижня (пн-нд) напиши одне завдання або активність. "
        "Теми: саморозвиток, здоров'я, краса, відпочинок, творчість. "
        "Українською мовою. Використовуй емодзі. Максимум 200 слів."
    )
    result = ask_gemini(prompt)
    await update.message.reply_text(result or "📅 Плануй тиждень з посмішкою! 😊")

# === ОБРОБКА ПОВІДОМЛЕНЬ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global WAITING_MOOD
    text = update.message.text
    if WAITING_MOOD:
        WAITING_MOOD = False
        prompt = (
            f"Дівчина на ім'я Емілія написала що її настрій: '{text}'. "
            "Напиши їй підбадьорливе повідомлення українською мовою під цей настрій. "
            "Тон теплий і щирий. Використовуй емодзі. Максимум 100 слів."
        )
        result = ask_gemini(prompt)
        await update.message.reply_text(result or "🌸 Ти справжня! Все буде добре!")

# === ЩОДЕННІ ПОВІДОМЛЕННЯ ===
async def daily_morning(app):
    if EMILIA_CHAT_ID:
        text = generate_morning_message()
        weather = get_weather()
        await app.bot.send_message(chat_id=EMILIA_CHAT_ID, text=f"{text}\n\n{weather}")

async def daily_evening(app):
    if EMILIA_CHAT_ID:
        text = generate_evening_message()
        await app.bot.send_message(chat_id=EMILIA_CHAT_ID, text=text)

# === ЗАПУСК ===
app_ref = None

async def main():
    global app_ref
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_ref = app

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("message", send_now))
    app.add_handler(CommandHandler("porada", advice))
    app.add_handler(CommandHandler("nastrii", mood))
    app.add_handler(CommandHandler("tyzhden", week_plan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
    scheduler.add_job(daily_morning, "cron", hour=9, minute=0, args=[app])
    scheduler.add_job(daily_evening, "cron", hour=21, minute=0, args=[app])
    scheduler.start()

    print("Бот Емілії запущено ✅")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
