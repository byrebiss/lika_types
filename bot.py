import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8645404074:AAG14-fw8XZ884GmnqW9vKHXS4-OTVV_OKo")
WEB_APP_URL = "https://byrebiss.github.io/lika_types/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            "✨ Узнать свой архетип",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    ]]
    await update.message.reply_text(
        "Привет! 🌸\n\nНажми кнопку ниже, чтобы пройти тест на определение архетипа.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", app=start))
app.run_polling()
