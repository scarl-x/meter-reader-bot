from yandex_cloud_ml_sdk import YCloudML
from langchain_core.messages import AIMessage, HumanMessage
from config import YANDEX_FOLDER_ID, YANDEX_IAM_TOKEN
from sessions import get_session
from api import validate_account, validate_serial, submit_reading

sdk = YCloudML(folder_id=YANDEX_FOLDER_ID, auth=YANDEX_IAM_TOKEN)
model = sdk.models.completions("yandexgpt", model_version="rc").langchain()

async def handle_message(user_id, message_text):
    session = get_session(user_id)

    # === Этап 1: ввод лицевого счёта ===
    if session["stage"] == "account":
        if message_text.strip().isdigit():
            account = message_text.strip()
            if await validate_account(account):
                session["accountNumber"] = account
                session["stage"] = "serial"
                session["history"].append(HumanMessage(content=message_text))
                response = model.invoke(session["history"])
                session["history"].append(AIMessage(content=response.content))
                return response.content
            else:
                return "❌ Лицевой счёт не найден. Пожалуйста, введите другой."
        else:
            session["history"].append(HumanMessage(content=message_text))
            response = model.invoke(session["history"])
            session["history"].append(AIMessage(content=response.content))
            return response.content

    # === Этап 2: серийный номер ===
    elif session["stage"] == "serial":
        serial = message_text.strip()
        if await validate_serial(serial):
            session["serialNumber"] = serial
            session["stage"] = "reading"
            session["history"].append(HumanMessage(content=message_text))
            response = model.invoke(session["history"])
            session["history"].append(AIMessage(content=response.content))
            return response.content
        else:
            return "❌ Серийный номер не найден. Введите правильный номер."

    # === Этап 3: показания ===
    elif session["stage"] == "reading":
        try:
            reading = int(message_text.strip())
            if reading <= 0:
                raise ValueError
            session["newReading"] = reading
            session["history"].append(HumanMessage(content=message_text))

            success = await submit_reading(session["serialNumber"], session["newReading"])
            if success:
                session["stage"] = "done"
                return "✅ Показания успешно переданы! Спасибо!"
            else:
                return "⚠️ Не удалось отправить показания. Повторите позже."
        except ValueError:
            return "⚠️ Введите корректное целое число — показание счётчика."

    # === Завершено ===
    else:
        return "Вы уже передали показания. Начните заново, если нужно снова."
