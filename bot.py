import os
from dotenv import load_dotenv
import telebot

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
SENHA_CORRETA = os.getenv('SENHA_CORRETA')
ARQUIVO_APROVADOS = os.getenv('ARQUIVO_APROVADOS')
bot = telebot.TeleBot(BOT_TOKEN)
PASTA_PDFS = "pdfs"
os.makedirs(PASTA_PDFS, exist_ok=True)

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

@bot.message_handler(content_types=['document'])
def receber_documento(message):
    chat_id = format(message.chat.id)

    if chat_id in ids_aprovados:
        documento = message.document
        file_name = documento.file_name

        if file_name.lower().endswith('.pdf'):
            bot.reply_to(message, f"Iniciando download de '{file_name}'. Isso pode demorar alguns segundos")
            file_info = bot.get_file(documento.file_id)
            file_path = file_info.file_path

            downloaded_file = bot.download_file(file_path)
            caminho_local = os.path.join(PASTA_PDFS, file_name)
            with open(caminho_local, 'wb') as f:
                f.write(downloaded_file)

            bot.reply_to(message, f"PDF '{file_name}' salvo com sucesso!")
    else:
        bot.reply_to(message, "Envie a senha para ganhar acesso ao bot")


def conversar(message):
    bot.reply_to(message, "bobo")

@bot.message_handler(commands=['files','show'])
def show_dir(message):
    nomes_arquivos = [f for f in os.listdir(PASTA_PDFS) if os.path.isfile(os.path.join(PASTA_PDFS, f))]
    if nomes_arquivos:
        string_resultado = '\n\n'.join(nomes_arquivos)
        bot.reply_to(message, f"Aqui está a lista de arquivos presentes na biblioteca do bot:\n{string_resultado}")
    else:
        bot.reply_to(message, "A biblioteca do bot está vazia ;-;")
    


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Olá, sou um bot para armazenar seus arquivos.")
    chat_id = format(message.chat.id)

    if chat_id not in ids_aprovados:
        bot.reply_to(message, "Por favor, envie a senha para ganhar acesso ao bot")


@bot.message_handler(func=lambda message: True) 
def verificar_senha(message):
    chat_id = format(message.chat.id)

    if chat_id in ids_aprovados:
        conversar(message)
    else:
        if message.text.strip() == SENHA_CORRETA:
            salvar_id_aprovado(chat_id)
            ids_aprovados.add(chat_id)
            bot.reply_to(message, "Senha correta! Acesso liberado.")
        else:
            bot.reply_to(message, "Você ainda não tem acesso. Por favor, envie a senha")


bot.infinity_polling()