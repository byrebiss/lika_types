import os
import json
import httpx
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8645404074:AAG14-fw8XZ884GmnqW9vKHXS4-OTVV_OKo")
WEB_APP_URL = "https://byrebiss.github.io/lika_types/"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBW1-dVdTttIIDlcdtw3tw9bHpHqjipfVA")

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
