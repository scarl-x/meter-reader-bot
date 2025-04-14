from telegram import Update
from telegram.ext import ContextTypes
import aiohttp
from config import PHOTO_API_KEY
from sessions import get_session
from api import submit_reading

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)

    if session["stage"] != "reading":
        await update.message.reply_text("📸 Вы можете отправить фото только на этапе ввода показаний.")
        return

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    photo_bytes = await file.download_as_bytearray()

    async with aiohttp.ClientSession() as http_session:
        data = aiohttp.FormData()
        data.add_field('image', photo_bytes, filename='photo.jpg', content_type='image/jpeg')
        data.add_field('counter_type', 'water')

        headers = {
            "Api-Key": PHOTO_API_KEY
        }

        async with http_session.post("https://api.cv-blueberry.yavlenie.pro/v1/recognize", headers=headers, data=data) as resp:
            if resp.status == 200:
                result = await resp.json()

                try:
                    reading = int(result["value"])  # предполагаем, что API возвращает поле 'value'
                    if reading <= 0:
                        raise ValueError

                    session["newReading"] = reading
                    success = await submit_reading(session["serialNumber"], reading)

                    if success:
                        session["stage"] = "done"
                        await update.message.reply_text(f"✅ Показания {reading} успешно переданы! Спасибо!")
                    else:
                        await update.message.reply_text("⚠️ Не удалось отправить показания. Повторите позже.")
                except Exception:
                    await update.message.reply_text(f"⚠️ Не удалось распознать корректные показания: {result}")
            else:
                await update.message.reply_text(f"❌ Ошибка распознавания. Код: {resp.status}")
