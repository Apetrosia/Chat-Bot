import telebot
import requests
import jsons
import os
from dotenv import load_dotenv 
from Class_ModelResponse import ModelResponse
 
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

user_context = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я единорог Тоня, первая пони-программист в Эквестрии!\n"
        "Доступные команды:\n"
        "/start - вывод доступных команд\n"
        "/model - название используемой языковой модели\n"
        "/clear - очистка контекста\n"
        "Напиши мне что-нибудь для начала диалога:)"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['model'])
def send_model_name(message):
    response = requests.get('http://localhost:1234/v1/models')
    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')

@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id
    if user_id in user_context:
        user_context.pop(user_id)
        bot.reply_to(message, "Контекст успешно очищен.")
    else:
        bot.reply_to(message, "Контекст уже пуст.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_query = message.text

    if user_id not in user_context:
        user_context[user_id] = []
    user_context[user_id].append({"role": "user", "content": user_query})

    request = {
        "messages": user_context[user_id]
    }

    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        json=request
    )

    if response.status_code == 200:
        model_response: ModelResponse = jsons.loads(response.text, ModelResponse)
        bot_reply = model_response.choices[0].message.content

        user_context[user_id].append({"role": "assistant", "content": bot_reply})
        
        bot.reply_to(message, bot_reply)
    else:
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.')

if __name__ == '__main__':
    bot.polling(none_stop=True)