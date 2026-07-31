import os
import time
import requests

TOKEN = '8947979521:AAHUNCEDhJU5Ee6YOEvtJeUSo01YAFXiSpI'
URL = f"https://api.telegram.org/bot{TOKEN}"

# Variáveis globais para controlar a banca e o estado da conversa
DADOS = {
    "etapa": None,
    "email": "",
    "banca": 0.0,
    "meta": 0.0
}

def enviar_mensagem(chat_id, texto):
    try:
        requests.post(f"{URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "Markdown"
        })
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def processar_mensagens(offset):
    try:
        resposta = requests.get(f"{URL}/getUpdates", params={"offset": offset, "timeout": 30})
        dados = resposta.json()
        
        if not dados.get("ok"):
            return offset
            
        for resultado in dados.get("result", []):
            offset = resultado["update_id"] + 1
            
            if "message" not in resultado or "text" not in resultado["message"]:
                continue
                
            chat_id = resultado["message"]["chat"]["id"]
            texto = resultado["message"]["text"].strip()
            
            global DADOS
            
            # Comando /start
            if texto == "/start":
                DADOS["etapa"] = None
                enviar_mensagem(chat_id, 
                    "🤖 **Robô de Operações Ativo!**\n\n"
                    "Comandos disponíveis:\n"
                    "🔹 /conectar - Fazer login na IQ Option\n"
                    "🔹 /banca - Definir o valor da banca\n"
                    "🔹 /status - Ver o progresso e a meta de 2%"
                )
            
            # Comando /conectar
            elif texto == "/conectar":
                DADOS["etapa"] = "AGUARDANDO_EMAIL"
                enviar_mensagem(chat_id, "📧 Por favor, digite o seu **e-mail** da IQ Option:")
            
            # Comando /banca
            elif texto == "/banca":
                DADOS["etapa"] = "AGUARDANDO_BANCA"
                enviar_mensagem(chat_id, "💰 Qual é o valor da sua **banca inicial**? (Ex: 1000)")
            
            # Comando /status
            elif texto == "/status":
                enviar_mensagem(chat_id, 
                    f"📊 **Status Atual**\n"
                    f"Banca: ${DADOS['banca']:.2f}\n"
                    f"Meta de 2%: ${DADOS['meta']:.2f}"
                )
            
            # Fluxos de conversas guiadas
            elif DADOS["etapa"] == "AGUARDANDO_EMAIL":
                DADOS["email"] = texto
                DADOS["etapa"] = "AGUARDANDO_SENHA"
                enviar_mensagem(chat_id, "🔑 Agora, digite a sua **senha** da IQ Option:")
            
            elif DADOS["etapa"] == "AGUARDANDO_SENHA":
                senha = texto
                email = DADOS["email"]
                DADOS["etapa"] = None
                enviar_mensagem(chat_id, f"✅ Credenciais recebidas para `{email}`! Módulo de conexão pronto.")
            
            elif DADOS["etapa"] == "AGUARDANDO_BANCA":
                try:
                    valor = float(texto.replace(",", "."))
                    DADOS["banca"] = valor
                    DADOS["meta"] = valor * 0.02
                    DADOS["etapa"] = None
                    enviar_mensagem(chat_id, 
                        f"✅ **Banca configurada com sucesso!**\n"
                        f"💰 Inicial: ${valor:.2f}\n"
                        f"🎯 Meta de 2%: ${DADOS['meta']:.2f}"
                    )
                except ValueError:
                    enviar_mensagem(chat_id, "❌ Valor inválido. Digite apenas números (ex: 500).")
            else:
                if not texto.startswith("/"):
                    enviar_mensagem(chat_id, "❓ Comando não reconhecido. Use /start para ver as opções.")
                    
    except Exception as e:
        print(f"Erro no loop: {e}")
        
    return offset

if __name__ == "__main__":
    print("Robô iniciado com sucesso na nuvem...")
    ultimo_offset = 0
    while True:
        ultimo_offset = processar_mensagens(ultimo_offset)
        time.sleep(1)
