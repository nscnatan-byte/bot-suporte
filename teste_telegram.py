import requests

TOKEN = "8977968510:AAH5gCJ8UeS6-DbfwN-AlTFxqbHDUQXxUjc"

CHAT_ID = "-1002260588784"

MESSAGE_THREAD_ID = 19

mensagem = "TESTE NO TOPICO CERTO 🚀"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

dados = {
    "chat_id": CHAT_ID,
    "message_thread_id": MESSAGE_THREAD_ID,
    "text": mensagem
}

requests.post(url, data=dados)

print("MENSAGEM ENVIADA")