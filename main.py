from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from config import TELEGRAM_BOT_TOKEN
from bot_logic import handle_message
from sessions import get_session, init_session
from photos import handle_photo  

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_session(update.effective_user.id)
    session = get_session(update.effective_user.id)
    first_reply = session["history"][-1].content
    await update.message.reply_text(first_reply)

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    response = await handle_message(user_id, text)
    await update.message.reply_text(response)

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    # В случае, если пользователь отправляет фото вместо текста
    if session["stage"] == "reading":
        await handle_photo(update, context)  
    else:
        await update.message.reply_text("❌ Пожалуйста, отправьте показания в текстовом виде.")
        
def main():
    request = HTTPXRequest()

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))
    app.add_handler(MessageHandler(filters.PHOTO, photo)) 
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
