import asyncio
import requests
import random
import os
from datetime import datetime
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === НАЛАШТУВАННЯ ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

EMILIA_CHAT_ID = None
WAITING_MOOD = False
BAD_MOOD_CHAT = False
RANDOM_CHAT = False
ADMIN_ID = 1290247650
USERS_DB = {}
app_ref = None

# === ПРИВІТАННЯ ===
def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Доброго ранку"
    elif 12 <= hour < 19:
        return "Привіт"
    else:
        return "Доброго вечора"

# === 100+ КОМПЛІМЕНТІВ ===
COMPLIMENTS = [
    "Ти неймовірна і особлива ✨", "Твоя посмішка освітлює весь світ 🌟",
    "Ти найкраща і найяскравіша 🌸", "Твоя доброта надихає всіх навколо 💛",
    "Ти справжнє диво цього світу 🌺", "Твої очі сяють як зірки ⭐",
    "Ти така розумна і талановита 🧠", "Твоя енергія заряджає всіх навколо ⚡",
    "Ти робиш світ кращим просто існуючи 🌍", "Твоя краса — це не лише зовнішність 💎",
    "Ти сильна і впевнена 💪", "Твій сміх — найкраща музика 🎵",
    "Ти унікальна в кожній своїй рисі 🦋", "Твоя теплота зігріває серця 🔥",
    "Ти надихаєш просто своєю присутністю 🌈", "Твоя усмішка варта мільйона зірок 💫",
    "Ти чарівна і неповторна 🌙", "Твоя душа прекрасна як ранкова зоря 🌅",
    "Ти справжня перлина 🐚", "Твій характер — це справжній скарб 💝",
    "Ти така творча і натхненна 🎨", "Твоя інтуїція завжди вражає 🔮",
    "Ти граціозна і елегантна 👑", "Твоя щирість — найцінніша якість 💌",
    "Ти наповнюєш кімнату світлом 💡", "Твоя сміливість вражає 🦁",
    "Ти така мила і ніжна 🌷", "Твій стиль неповторний 👗",
    "Ти розумієш серцем те що інші не бачать 👁️", "Твоя присутність — це подарунок 🎁",
    "Ти неймовірно цікава людина 📚", "Твоя впевненість надихає 🚀",
    "Ти справжня зірка 🌟", "Твоя ніжність зворушує до сліз 🥹",
    "Ти така особлива — таких більше немає 💯", "Твоя мудрість вражає 🦉",
    "Ти повна сюрпризів і це чудово 🎊", "Твоя жіночність неперевершена 🌹",
    "Ти вмієш бачити красу в дрібницях 🔍", "Твоя доброта повертається сторицею 🌀",
    "Твоя посмішка — найкращі ліки 😊", "Ти повна життя і натхнення 🌊",
    "Твоя уважність до деталей вражає 🎯", "Ти вмієш робити звичайне особливим ✨",
    "Твоя відкритість приваблює людей 🤗", "Ти така щира і справжня 💚",
    "Твоя харизма неймовірна 🔆", "Ти вмієш слухати і це рідкість 👂",
    "Твоя позитивність заряджає 🌞", "Ти як сонячний промінь у похмурий день ☀️",
    "Твоя усмішка — найкраща прикраса 💐", "Ти вмієш знаходити радість у малому 🎈",
    "Твоя природність підкуповує 🍃", "Ти така жива і справжня 🌻",
    "Твоя інтелігентність приваблює 🎓", "Ти вмієш надихати словом 🗣️",
    "Твоя турботливість зігріває 🫂", "Ти як квітка що розцвітає щодня 🌼",
    "Твоя наполегливість вражає 🏆", "Ти вмієш перетворювати мрії на реальність 🌠",
    "Твоя чуттєвість — це дар 🎶", "Ти така яскрава особистість 🎆",
    "Твоя елегантність незрівнянна 🕊️", "Ти вмієш дарувати тепло 🕯️",
    "Твоя легкість у спілкуванні чарує 🦚", "Ти робиш кожен день кращим 📆",
    "Твоя душевність — найбільший скарб 💎", "Ти вмієш любити всім серцем ❤️",
    "Твоя усмішка варта цілого всесвіту 🌌", "Ти така натхненна і яскрава 🎇",
    "Твоя лагідність зачаровує 🌬️", "Ти вмієш бути справжньою 🌿",
    "Твоя краса розквітає з кожним днем 🌸", "Ти як музика — завжди в серці 🎼",
    "Твоя вірність безцінна 🔑", "Ти вмієш бути сонцем для інших ☀️",
    "Твоя грація неперевершена 🩰", "Ти така душевна і щира людина 🫀",
    "Твоя усмішка робить серце теплішим 💓", "Ти вмієш бачити хороше в усьому 🌈",
    "Твоя ніжність — це твоя сила 🌷", "Ти така захоплива і цікава 🎭",
    "Твоя радість заразна 😄", "Ти вмієш перетворювати будні на свято 🎉",
    "Твоя інтуїція — справжній дар 🔮", "Ти така жвава і енергійна 🌪️",
    "Твоя відданість вражає 🤝", "Ти вмієш надихати своїм прикладом 🌟",
    "Твоя чарівність не має меж ✨", "Ти така особлива кожного дня 💫",
    "Твоя теплота — це твій найбільший скарб 🧡", "Ти вмієш освітлювати темряву 🕯️",
    "Твоя краса всередині і зовні 🪞", "Ти така дивовижна людина 🦋",
    "Твоя присутність змінює атмосферу 🌤️", "Ти вмієш любити щиро і глибоко ❤️‍🔥",
]

# === 100+ ПОРАД ===
DAILY_TIPS = [
    "💧 Випий склянку води одразу після пробудження",
    "🚶 Пройди 10 хвилин пішки після їжі",
    "📵 Перші 30 хвилин після пробудження не бери телефон",
    "🧘 Зроби 5 глибоких вдихів коли відчуваєш стрес",
    "📖 Читай хоча б 10 сторінок книги щодня",
    "🌿 Додай зелень до кожного прийому їжі",
    "😴 Лягай спати до 23:00",
    "🎯 Запиши три цілі на сьогодні вранці",
    "🧴 Не забувай про SPF кожного дня",
    "💃 Потанцюй 5 хвилин під улюблену пісню",
    "🫖 Замість кави вранці спробуй зелений чай",
    "📝 Веди щоденник вдячності — 3 речі щодня",
    "🌬️ Провітрюй кімнату щоранку 5 хвилин",
    "🧠 Вчи одне нове слово іноземної мови щодня",
    "🤸 Розтягуйся 5 хвилин перед сном",
    "🫂 Обіймай близьких частіше",
    "🎨 Виділи 15 хвилин на творчість щодня",
    "🌅 Подивись на захід або схід сонця",
    "💊 Перевір чи вживаєш достатньо вітаміну D",
    "🧹 Прибери один маленький безлад",
    "📞 Зателефонуй комусь близькому без приводу",
    "🍎 З'їж фрукт замість солодкого на перекус",
    "👁️ Кожну годину давай очам відпочинок від екрану",
    "🌙 Склади список справ на завтра ввечері",
    "🎵 Слухай музику яка надихає під час роботи",
    "💰 Відклади невелику суму заощаджень сьогодні",
    "🧊 Вмийся холодною водою вранці",
    "🌱 Полий рослини або зупинись біля зелені",
    "😊 Посміхнись першій людині яку зустрінеш",
    "✍️ Напиши листа собі майбутній",
    "🏃 Зроби 20 присідань прямо зараз",
    "🎧 Послухай подкаст поки їдеш кудись",
    "🛁 Прийми ванну з сіллю після важкого дня",
    "🌊 Вийди на природу хоча б на 20 хвилин",
    "💻 Очисти робочий стіл телефону або комп'ютера",
    "🥗 Приготуй щось нове і корисне",
    "📸 Сфотографуй щось красиве сьогодні",
    "🎁 Зроби комусь приємний сюрприз",
    "🧡 Скажи комусь щось добре сьогодні",
    "💤 Спробуй лягти на 30 хвилин раніше",
    "🌺 Купи собі квітку просто так",
    "📚 Перечитай улюблену цитату яка надихає",
    "🎯 Зроби одну справу яку відкладала",
    "🫧 Пий воду з лимоном",
    "🌟 Згадай три своїх досягнення цього тижня",
    "💝 Зроби щось добре для себе сьогодні",
    "🎶 Співай вголос — знімає напругу",
    "🧁 Побалуй себе улюбленими ласощами",
    "🌍 Дізнайся щось нове про світ сьогодні",
    "🎬 Подивись надихаючий фільм увечері",
]

# === МОТИВАЦІЯ ===
MOTIVATION = [
    "🌟 Ти здатна на більше ніж думаєш!",
    "💪 Кожен маленький крок — це перемога!",
    "🌈 Після дощу завжди буде веселка!",
    "🔥 Твоя сила всередині тебе!",
    "✨ Ти вже робиш все правильно!",
    "🚀 Великі справи починаються з малого!",
    "💎 Ти коштовна — не забувай про це!",
    "🌸 Будь ніжна до себе — ти заслуговуєш!",
    "🦋 Зміни — це завжди на краще!",
    "🌅 Кожен день — новий шанс!",
    "💫 Вір у себе — і все вийде!",
    "🎯 Ти ближче до мети ніж думаєш!",
    "🌻 Ти розквітаєш з кожним днем!",
    "❤️ Ти гідна найкращого!",
    "🏆 Ти переможець у своєму житті!",
    "🌊 Пливи — ти вмієш!",
    "🎨 Твоє життя — твій шедевр!",
    "🌙 Навіть у темряві ти сяєш!",
    "💐 Ти варта найкращого!",
    "🎵 Твоє серце знає правильний ритм!",
]

# === ПЛАНИ НА ТИЖДЕНЬ ===
WEEK_ACTIVITIES = {
    "Понеділок": ["медитація 10 хвилин", "прогулянка на свіжому повітрі", "читання книги", "приготування корисної страви", "планування тижня"],
    "Вівторок": ["йога або розтяжка", "дзвінок близькій людині", "вивчення нового рецепту", "перегляд надихаючого фільму", "малювання або творчість"],
    "Середа": ["водний детокс — 2л води", "прибирання одного куточка", "написання у щоденнику", "новий маршрут прогулянки", "приємна ванна"],
    "Четвер": ["фізична активність 30 хв", "приготування улюбленої страви", "читання мотивуючої статті", "розмова з подругою", "догляд за собою"],
    "П'ятниця": ["підсумок тижня", "маленька нагорода собі", "перегляд улюбленого серіалу", "приємна прогулянка", "планування вихідних"],
    "Субота": ["ранковий ритуал без поспіху", "похід у кафе або парк", "творчий проєкт", "зустріч з близькими", "релакс і відпочинок"],
    "Неділя": ["повільний ранок", "підготовка до нового тижня", "улюблена музика", "вдячність за тиждень", "рання нічна рутина"],
}

# === ПИТАННЯ ДЛЯ РАНДОМНОГО CHECK-IN ===
CHECK_IN_QUESTIONS = [
    "Привіт! 🌸 Як ти сьогодні?",
    "Гей, Емілія! 💛 Як справи?",
    "Привіт! ✨ Що робиш зараз?",
    "Як твій день проходить? 🌼",
    "Гей! 🦋 Як ти себе почуваєш?",
    "Привіт! 💌 Розкажи як ти?",
    "Як настрій сьогодні? 🌈",
    "Гей, сонечко! ☀️ Як справи?",
    "Привіт! 🌺 Що нового?",
    "Як ти там? 💝 Думаю про тебе!",
    "Привіт! 🎀 Як проходить день?",
    "Гей! 🌟 Що цікавого сьогодні?",
    "Привіт, зірочко! ⭐ Як ти?",
    "Як самопочуття? 🌷 Розкажи!",
    "Гей! 💫 Що робиш гарного?",
]

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

# === ГЕНЕРАЦІЯ ПОВІДОМЛЕННЯ ===
def generate_message():
    greeting = get_greeting()
    themes = [
        "зроби акцент на її красі та посмішці",
        "зроби акцент на її розумі та талантах",
        "зроби акцент на її доброті та теплоті",
        "зроби акцент на тому як вона надихає інших",
        "зроби акцент на її силі та впевненості",
        "зроби акцент на її унікальності",
        "зроби акцент на її позитивній енергії",
        "зроби акцент на її творчості",
        "зроби акцент на її мудрості",
        "зроби акцент на її харизмі",
    ]
    theme = random.choice(themes)
    prompt = (
        f"Ти ніжний бот для дівчини на ім'я Емілія. {theme}. "
        f"Напиши їй повідомлення яке починається з '{greeting}, Емілія!' українською. "
        "Воно має містити: комплімент, побажання гарного дня, пораду та передбачення. "
        "Тон — теплий, щирий. Емодзі. Максимум 150 слів. Щоразу абсолютно інше!"
    )
    result = ask_gemini(prompt)
    if not result:
        return f"🌸 {greeting}, Емілія! {random.choice(COMPLIMENTS)}"
    return result

# === ВЕЧІРНЄ ПОВІДОМЛЕННЯ ===
def generate_evening_message():
    prompt = (
        "Ти ніжний бот для дівчини на ім'я Емілія. "
        "Напиши вечірнє повідомлення українською: побажання на ніч, "
        "підсумок що день був гарним, комплімент і побажання солодких снів. "
        "Тон спокійний і теплий. Емодзі. Максимум 100 слів."
    )
    result = ask_gemini(prompt)
    return result or "🌙 На добраніч, Емілія! Ти сьогодні була чудовою 💫 Солодких снів!"

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global EMILIA_CHAT_ID
    EMILIA_CHAT_ID = update.effective_chat.id
    USERS_DB[update.effective_chat.id] = update.effective_user.username or update.effective_user.first_name
    await update.message.reply_text(
        "Привіт, Емілія! 🌸\n"
        "Я твій особистий бот 💌\n"
        "Щоранку — особливе повідомлення ✨\n"
        "Щовечора — побажання на ніч 🌙\n"
        "І інколи буду просто писати щоб дізнатись як ти 💛"
    )

# === /message ===
async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = generate_message()
    weather = get_weather()
    await update.message.reply_text(f"{text}\n\n{weather}")
    with open("sticker.webm", "rb") as sticker:
        await update.message.reply_sticker(sticker)

# === /pogoda ===
async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_weather())

# === /porada ===
async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tip = random.choice(DAILY_TIPS)
    prompt = (
        f"Розкажи детальніше про цю пораду для дівчини Емілія: '{tip}'. "
        "Поясни чому це корисно і як зробити. Українською. Емодзі. Максимум 100 слів."
    )
    result = ask_gemini(prompt)
    await update.message.reply_text(result or tip)

# === /nastrii ===
async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global WAITING_MOOD
    WAITING_MOOD = True
    keyboard = [["😊 Чудово", "😐 Нормально"], ["😔 Сумно", "😤 Злюся"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Який у тебе зараз настрій? 🎵", reply_markup=markup)

# === /tyzhden ===
async def week_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Генерую план на тиждень... 📅")
    plan = "📅 Твій план на тиждень, Емілія:\n\n"
    for day, activities in WEEK_ACTIVITIES.items():
        activity = random.choice(activities)
        plan += f"{day}: {activity}\n"
    prompt = (
        f"Ось план на тиждень для дівчини Емілія:\n{plan}\n"
        "Додай коротку мотиваційну фразу в кінці. Українською. Емодзі."
    )
    result = ask_gemini(prompt)
    await update.message.reply_text(result or plan)

# === /users ===
async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID:
        await update.message.reply_text("⛔ Немає доступу")
        return
    if not USERS_DB:
        await update.message.reply_text("Поки ніхто не використовував бота")
        return
    text = "👥 Користувачі бота:\n\n"
    for uid, name in USERS_DB.items():
        text += f"• {name} (ID: {uid})\n"
    await update.message.reply_text(text)

# === ОБРОБКА ПОВІДОМЛЕНЬ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global WAITING_MOOD, BAD_MOOD_CHAT, RANDOM_CHAT
    text = update.message.text

    # Рандомна розмова (check-in)
    if RANDOM_CHAT:
        RANDOM_CHAT = False
        prompt = (
            f"Ти ніжний бот для дівчини Емілія. Вона відповіла на питання як справи: '{text}'. "
            "Відреагуй щиро як подруга: якщо добре — порадій, якщо погано — підтримай. "
            "Продовж розмову одним теплим реченням. Українською. Емодзі. Максимум 80 слів."
        )
        result = ask_gemini(prompt)
        await update.message.reply_text(result or f"🌸 Дякую що поділилась! {random.choice(MOTIVATION)}")
        return

    # Вибір настрою
    if WAITING_MOOD:
        WAITING_MOOD = False
        bad_moods = ["😔 Сумно", "😤 Злюся"]
        if text in bad_moods:
            BAD_MOOD_CHAT = True
            prompt = (
                f"Дівчина на ім'я Емілія написала що їй '{text}'. "
                "Почни з нею теплу розмову: спочатку визнай її почуття, "
                "потім запитай що сталось. Будь як найкраща подруга. "
                "Українською. Емодзі. Максимум 100 слів."
            )
            result = ask_gemini(prompt)
            await update.message.reply_text(
                result or "💙 Розкажи мені що сталось — я тут для тебе...",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            BAD_MOOD_CHAT = False
            prompt = (
                f"Дівчина на ім'я Емілія написала що її настрій: '{text}'. "
                "Напиши підбадьорливе повідомлення під цей настрій. "
                "Українською. Теплий тон. Емодзі. Максимум 100 слів."
            )
            result = ask_gemini(prompt)
            await update.message.reply_text(
                result or f"🌸 Чудово! {random.choice(MOTIVATION)}",
                reply_markup=ReplyKeyboardRemove()
            )
        return

    # Розмова при поганому настрої
    if BAD_MOOD_CHAT:
        prompt = (
            f"Ти підтримуєш дівчину Емілія у розмові. Вона написала: '{text}'. "
            "Відповідай як найкраща подруга: слухай, підтримуй, давай пораду. "
            "Якщо ситуація вирішена — скажи щось тепле на завершення. "
            "Українською. Емодзі. Максимум 150 слів."
        )
        result = ask_gemini(prompt)
        await update.message.reply_text(result or "💙 Я тут поруч, не хвилюйся!")
        return

# === ЩОДЕННІ ПОВІДОМЛЕННЯ ===
async def daily_morning(app):
    if EMILIA_CHAT_ID:
        text = generate_message()
        weather = get_weather()
        await app.bot.send_message(chat_id=EMILIA_CHAT_ID, text=f"{text}\n\n{weather}")

async def daily_evening(app):
    if EMILIA_CHAT_ID:
        text = generate_evening_message()
        await app.bot.send_message(chat_id=EMILIA_CHAT_ID, text=text)

# === РАНДОМНИЙ CHECK-IN ===
async def random_check_in(app):
    global RANDOM_CHAT
    if EMILIA_CHAT_ID:
        RANDOM_CHAT = True
        await app.bot.send_message(
            chat_id=EMILIA_CHAT_ID,
            text=random.choice(CHECK_IN_QUESTIONS)
        )

# === ЗАПУСК ===
async def main():
    global app_ref
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_ref = app

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("message", send_now))
    app.add_handler(CommandHandler("pogoda", weather_cmd))
    app.add_handler(CommandHandler("porada", advice))
    app.add_handler(CommandHandler("nastrii", mood))
    app.add_handler(CommandHandler("tyzhden", week_plan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("users", users_cmd))

    await app.bot.set_my_commands([
        ("start", "🌸 Запустити бота"),
        ("message", "💌 Отримати повідомлення"),
        ("pogoda", "🌦 Погода в Києві"),
        ("porada", "💡 Порада дня"),
        ("nastrii", "🎵 Підбадьорення під настрій"),
        ("tyzhden", "📅 План на тиждень"),
    ])

    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
    scheduler.add_job(daily_morning, "cron", hour=9, minute=0, args=[app])
    scheduler.add_job(daily_evening, "cron", hour=21, minute=0, args=[app])

    # Рандомний check-in 3 рази на день між 10 і 21
    hours = random.sample(range(10, 21), 3)
    for hour in hours:
        scheduler.add_job(
            random_check_in, "cron",
            hour=hour,
            minute=random.randint(0, 59),
            args=[app]
        )

    scheduler.start()

   print("Бот Емілії запущено ✅")
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
        await app.updater.stop()
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
