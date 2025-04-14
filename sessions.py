from langchain_core.messages import AIMessage, HumanMessage

user_sessions = {}

def init_session(user_id):
    user_sessions[user_id] = {
        "stage": "account",
        "accountNumber": None,
        "serialNumber": None,
        "newReading": None,
        "history": [
            HumanMessage(content="Привет"),
            AIMessage(content="Привет! Я умный помощник, готов помочь тебе дать показания счетчика! Напиши здесь лицевой счёт, я проверю его наличие и мы будем двигаться дальше!")
        ]
    }

def get_session(user_id):
    if user_id not in user_sessions:
        init_session(user_id)
    return user_sessions[user_id]
