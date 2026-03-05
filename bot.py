import os
import json
import httpx
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8645404074:AAG14-fw8XZ884GmnqW9vKHXS4-OTVV_OKo")
WEB_APP_URL = "https://byrebiss.github.io/lika_types/"
YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY", "AQVNwDUOaifWuOQ5vVKMXD6Vp9QfgBbPNYfo7qyn")
YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID", "b1gi4t1d30shgf82bcpi")

ARCHETYPE_DESCRIPTIONS = {
    "innocent":  "Невинный — светлый, оптимистичный, верит в доброту мира",
    "orphan":    "Сирота — реалист, ценит своих людей, умеет выживать",
    "warrior":   "Воин — целеустремлённый, борется за результат",
    "caregiver": "Опекун — заботливый, ставит других выше себя",
    "seeker":    "Искатель — свободолюбивый, тянется к новому",
    "destroyer": "Разрушитель — смелый, не боится перемен и разрушения старого",
    "lover":     "Влюблённая — живёт чувствами, стремится к глубокой связи",
    "creator":   "Творец — создаёт своё, творчество это потребность",
    "ruler":     "Правитель — берёт ответственность, умеет организовывать",
    "magician":  "Маг — видит скрытые связи, верит в силу намерения",
    "sage":      "Мудрец — ищет истину, думает прежде чем действовать",
    "jester":    "Шут — находит лёгкость и юмор даже в серьёзном",
}

TOPICS = {
    "style":    ("👗 Стиль и образ",      "Опиши стиль одежды, цвета, образ и эстетику для архетипа {name}. Конкретно и практично."),
    "strengths":("💪 Сильные стороны",    "Опиши сильные стороны и таланты архетипа {name}. Что даётся легко, в чём природная сила."),
    "weaknesses":("⚠️ Слабые стороны",   "Опиши слабые стороны и типичные ловушки архетипа {name}. Честно и мягко."),
    "voice":    ("🗣 Тон оф войс",         "Опиши стиль общения, речь, тон голоса и манеру подачи себя для архетипа {name}."),
    "habits":   ("✨ Ритуалы и привычки", "Опиши полезные ритуалы, привычки и практики которые усиливают архетип {name}."),
    "career":   ("💼 Карьера и призвание","Опиши подходящие сферы деятельности, карьерные пути и призвание для архетипа {name}."),
}


async def ask_yandex(prompt: str) -> str:
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 1500
        },
        "messages": [
            {"role": "user", "text": prompt}
        ]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json=payload)
        data = response.json()
        print(f"YandexGPT response: {data}")
        return data["result"]["alternatives"][0]["message"]["text"]


def topics_keyboard():
    buttons = []
    for key, (label, _) in TOPICS.items():
        buttons.append([InlineKeyboardButton(label, callback_data=f"topic:{key}")])
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        KeyboardButton(
            "✨ Узнать свой архетип",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    ]]
    await update.message.reply_text(
        "Привет! 🌸\n\nНажми кнопку ниже, чтобы пройти тест на определение архетипа.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.message.web_app_data.data)

    main_arch = data.get("archetype", "")
    main_name = data.get("name", "")
    main_icon = data.get("icon", "")
    supporting = ARCHETYPE_DESCRIPTIONS.get(data.get("supporting", ""), "")
    shadow = ARCHETYPE_DESCRIPTIONS.get(data.get("shadow", ""), "")
    anti = ARCHETYPE_DESCRIPTIONS.get(data.get("anti", ""), "")
    main_desc = ARCHETYPE_DESCRIPTIONS.get(main_arch, "")

    # Сохраняем архетип пользователя для кнопок
    context.user_data["archetype"] = main_arch
    context.user_data["archetype_name"] = main_name
    context.user_data["archetype_icon"] = main_icon

    await update.message.reply_text(f"Твой архетип — {main_name} {main_icon}\n\nСоставляю твой разбор...")

    prompt = f"""Ты — Анжелика, мягкий и глубокий психолог-архетиполог. Пишешь тепло, лично, без клише.

Пользователь прошёл тест. Его результаты:
- Главный архетип: {main_name} ({main_desc})
- Поддерживающий: {supporting}
- Теневой: {shadow}
- Антиархетип: {anti}

Напиши персональный разбор в 4-5 абзацах:
1. Кто такой {main_name} — его суть и сила
2. Как поддерживающий архетип дополняет главный
3. Что такое теневой архетип и как он проявляется в жизни
4. Антиархетип — от чего человек бежит или что отрицает
5. Короткое напутствие

Пиши на "ты", тепло и конкретно. Без заголовков и списков — сплошной текст."""

    try:
        reply = await ask_yandex(prompt)
        await update.message.reply_text(reply)
        await update.message.reply_text(
            "Что хочешь изучить подробнее?",
            reply_markup=topics_keyboard()
        )
    except Exception as e:
        await update.message.reply_text("Что-то пошло не так при генерации разбора. Попробуй ещё раз.")
        print(f"YandexGPT error: {e}")


async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topic_key = query.data.split(":")[1]
    arch_name = context.user_data.get("archetype_name", "")
    arch_icon = context.user_data.get("archetype_icon", "")

    if not arch_name:
        await query.message.reply_text("Сначала пройди тест, чтобы узнать свой архетип.")
        return

    _, prompt_template = TOPICS[topic_key]
    prompt = f"""Ты — Анжелика, архетиполог. Пишешь тепло, конкретно, без клише. На "ты".

{prompt_template.format(name=arch_name)}

Напиши 3-4 абзаца. Без заголовков и списков — сплошной текст."""

    await query.message.reply_text(f"Готовлю для тебя...")

    try:
        reply = await ask_yandex(prompt)
        await query.message.reply_text(reply)
        await query.message.reply_text(
            "Что ещё хочешь изучить?",
            reply_markup=topics_keyboard()
        )
    except Exception as e:
        await query.message.reply_text("Что-то пошло не так. Попробуй ещё раз.")
        print(f"YandexGPT error: {e}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    app.add_handler(CallbackQueryHandler(handle_topic, pattern="^topic:"))
    app.run_polling()


BOT_TOKEN = os.environ.get("BOT_TOKEN", "8645404074:AAG14-fw8XZ884GmnqW9vKHXS4-OTVV_OKo")
WEB_APP_URL = "https://byrebiss.github.io/lika_types/"
YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY", "AQVNwDUOaifWuOQ5vVKMXD6Vp9QfgBbPNYfo7qyn")
YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID", "b1gi4t1d30shgf82bcpi")

ARCHETYPE_DESCRIPTIONS = {
    "innocent":  "Невинный — светлый, оптимистичный, верит в доброту мира",
    "orphan":    "Сирота — реалист, ценит своих людей, умеет выживать",
    "warrior":   "Воин — целеустремлённый, борется за результат",
    "caregiver": "Опекун — заботливый, ставит других выше себя",
    "seeker":    "Искатель — свободолюбивый, тянется к новому",
    "destroyer": "Разрушитель — смелый, не боится перемен и разрушения старого",
    "lover":     "Влюблённая — живёт чувствами, стремится к глубокой связи",
    "creator":   "Творец — создаёт своё, творчество это потребность",
    "ruler":     "Правитель — берёт ответственность, умеет организовывать",
    "magician":  "Маг — видит скрытые связи, верит в силу намерения",
    "sage":      "Мудрец — ищет истину, думает прежде чем действовать",
    "jester":    "Шут — находит лёгкость и юмор даже в серьёзном",
}


async def ask_yandex(prompt: str) -> str:
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 1500
        },
        "messages": [
            {"role": "user", "text": prompt}
        ]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json=payload)
        data = response.json()
        print(f"YandexGPT response: {data}")
        return data["result"]["alternatives"][0]["message"]["text"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        KeyboardButton(
            "✨ Узнать свой архетип",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    ]]
    await update.message.reply_text(
        "Привет! 🌸\n\nНажми кнопку ниже, чтобы пройти тест на определение архетипа.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.message.web_app_data.data)

    main_arch = data.get("archetype", "")
    main_name = data.get("name", "")
    main_icon = data.get("icon", "")
    supporting = ARCHETYPE_DESCRIPTIONS.get(data.get("supporting", ""), "")
    shadow = ARCHETYPE_DESCRIPTIONS.get(data.get("shadow", ""), "")
    anti = ARCHETYPE_DESCRIPTIONS.get(data.get("anti", ""), "")
    main_desc = ARCHETYPE_DESCRIPTIONS.get(main_arch, "")

    await update.message.reply_text(f"Твой архетип — {main_name} {main_icon}\n\nСоставляю твой разбор...")

    prompt = f"""Ты — Анжелика, мягкий и глубокий психолог-архетиполог. Пишешь тепло, лично, без клише.

Пользователь прошёл тест. Его результаты:
- Главный архетип: {main_name} ({main_desc})
- Поддерживающий: {supporting}
- Теневой: {shadow}
- Антиархетип: {anti}

Напиши персональный разбор в 4-5 абзацах:
1. Кто такой {main_name} — его суть и сила
2. Как поддерживающий архетип дополняет главный
3. Что такое теневой архетип и как он проявляется в жизни
4. Антиархетип — от чего человек бежит или что отрицает
5. Короткое напутствие

Пиши на "ты", тепло и конкретно. Без заголовков и списков — сплошной текст."""

    try:
        reply = await ask_yandex(prompt)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Что-то пошло не так при генерации разбора. Попробуй ещё раз.")
        print(f"YandexGPT error: {e}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    app.run_polling()


ARCHETYPE_DESCRIPTIONS = {
    "innocent":  "Невинный — светлый, оптимистичный, верит в доброту мира",
    "orphan":    "Сирота — реалист, ценит своих людей, умеет выживать",
    "warrior":   "Воин — целеустремлённый, борется за результат",
    "caregiver": "Опекун — заботливый, ставит других выше себя",
    "seeker":    "Искатель — свободолюбивый, тянется к новому",
    "destroyer": "Разрушитель — смелый, не боится перемен и разрушения старого",
    "lover":     "Влюблённая — живёт чувствами, стремится к глубокой связи",
    "creator":   "Творец — создаёт своё, творчество это потребность",
    "ruler":     "Правитель — берёт ответственность, умеет организовывать",
    "magician":  "Маг — видит скрытые связи, верит в силу намерения",
    "sage":      "Мудрец — ищет истину, думает прежде чем действовать",
    "jester":    "Шут — находит лёгкость и юмор даже в серьёзном",
}


async def ask_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload)
        data = response.json()
        print(f"Gemini response: {data}")
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        KeyboardButton(
            "✨ Узнать свой архетип",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    ]]
    await update.message.reply_text(
        "Привет! 🌸\n\nНажми кнопку ниже, чтобы пройти тест на определение архетипа.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.message.web_app_data.data)

    main_arch = data.get("archetype", "")
    main_name = data.get("name", "")
    main_icon = data.get("icon", "")
    supporting = ARCHETYPE_DESCRIPTIONS.get(data.get("supporting", ""), "")
    shadow = ARCHETYPE_DESCRIPTIONS.get(data.get("shadow", ""), "")
    anti = ARCHETYPE_DESCRIPTIONS.get(data.get("anti", ""), "")
    main_desc = ARCHETYPE_DESCRIPTIONS.get(main_arch, "")

    # Сообщаем пользователю что считаем результат
    await update.message.reply_text(f"Твой архетип — {main_name} {main_icon}\n\nСоставляю твой разбор...")

    prompt = f"""Ты — Анжелика, мягкий и глубокий психолог-архетиполог. Пишешь тепло, лично, без клише.

Пользователь прошёл тест. Его результаты:
- Главный архетип: {main_name} ({main_desc})
- Поддерживающий: {supporting}
- Теневой: {shadow}
- Антиархетип: {anti}

Напиши персональный разбор в 4-5 абзацах:
1. Кто такой {main_name} — его суть и сила
2. Как поддерживающий архетип дополняет главный
3. Что такое теневой архетип и как он проявляется в жизни
4. Антиархетип — от чего человек бежит или что отрицает
5. Короткое напутствие

Пиши на "ты", тепло и конкретно. Без заголовков и списков — сплошной текст."""

    try:
        reply = await ask_gemini(prompt)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Что-то пошло не так при генерации разбора. Попробуй ещё раз.")
        print(f"Gemini error: {e}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    app.run_polling()
