import os
from dotenv import load_dotenv
import telebot

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
SENHA_CORRETA = os.getenv('SENHA_CORRETA')
ARQUIVO_APROVADOS = os.getenv('ARQUIVO_APROVADOS')
bot = telebot.TeleBot(BOT_TOKEN)

def carregar_ids_aprovados():
    try:
        with open(ARQUIVO_APROVADOS, 'r') as f:
            return set(line.strip() for line in f if line.strip().isdigit())
    except FileNotFoundError:
        return set()

def salvar_id_aprovado(chat_id):
    with open(ARQUIVO_APROVADOS, 'a') as f:
        f.write(f"{chat_id}\n")

ids_aprovados = carregar_ids_aprovados()

def conversar(message):
    bot.reply_to(message, message.text)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Olá, por favor envie a senha para liberar acesso ao bot")

@bot.message_handler(func=lambda message: True) 
def verificar_senha(message):
    chat_id = format(message.chat.id)

    print ("aprovados:", ids_aprovados)
    print (chat_id)

    if chat_id in ids_aprovados:
        conversar(message)
    else:
        if message.text.strip() == SENHA_CORRETA:
            salvar_id_aprovado(chat_id)
            carregar_ids_aprovados()
            bot.reply_to(message, "Senha correta! Acesso liberado.")
        else:
            bot.reply_to(message, "Você ainda não tem acesso. Por favor, envie a senha")


bot.infinity_polling()