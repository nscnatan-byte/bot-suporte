import time
import requests

TOKEN = '8947979521:AAHUNCEDhJU5Ee6YOEvtJeUSo01YAFXiSpI'
URL = f"https://api.telegram.org/bot{TOKEN}"

# Dicionário para controlar o estado de cada usuário
USUARIOS = {}

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
            
            if chat_id not in USUARIOS:
                USUARIOS[chat_id] = {
                    "etapa": None, 
                    "email": "", 
                    "senha": "", 
                    "banca": 0.0, 
                    "meta_diaria": 0.0
                }
                
            usuario = USUARIOS[chat_id]
            
            # 1. Quando der /start -> vai direto pedir o e-mail
            if texto == "/start" or usuario["etapa"] is None:
                usuario["etapa"] = "AGUARDANDO_EMAIL"
                enviar_mensagem(chat_id, "🤖 **Robô de Operações IQ Option**\n\n1️⃣ Digite o seu **e-mail** da IQ Option:")
            
            # 2. Recebeu o e-mail -> pede a senha
            elif usuario["etapa"] == "AGUARDANDO_EMAIL":
                usuario["email"] = texto
                usuario["etapa"] = "AGUARDANDO_SENHA"
                enviar_mensagem(chat_id, "🔑 Digite a sua **senha** da IQ Option:")
            
            # 3. Recebeu a senha -> mostra "aguardando conectando" e simula a conexão
            elif usuario["etapa"] == "AGUARDANDO_SENHA":
                usuario["senha"] = texto
                enviar_mensagem(chat_id, "⏳ **Aguardando conectar...** Conectando à IQ Option...")
                
                # Simula o processo de conexão (aqui depois colocaremos a API real se precisar)
                time.sleep(2)
                
                # 4. Conectado com sucesso -> Pede o valor da banca inicial
                usuario["etapa"] = "AGUARDANDO_BANCA"
                enviar_mensagem(chat_id, "✅ **Conectado com sucesso!**\n\n💰 Digite o valor da sua **banca inicial** (Ex: 1000):")
            
            # 5. Recebeu a banca -> Pede a meta de ganho diário
            elif usuario["etapa"] == "AGUARDANDO_BANCA":
                try:
                    valor_banca = float(texto.replace(",", "."))
                    usuario["banca"] = valor_banca
                    usuario["etapa"] = "AGUARDANDO_META"
                    enviar_mensagem(chat_id, "🎯 Quanto você quer **ganhar por dia** (Meta diária em $ ou %)? (Ex: 50 ou digite 2%):")
                except ValueError:
                    enviar_mensagem(chat_id, "❌ Valor inválido. Digite apenas números para a banca (ex: 500):")
            
            # 6. Recebeu a meta -> Mostra o painel final configurado
            elif usuario["etapa"] == "AGUARDANDO_META":
                meta = texto
                usuario["etapa"] = "CONCLUIDO"
                enviar_mensagem(chat_id, 
                    f"🚀 **Configuração Concluída com Sucesso!**\n\n"
                    f"📧 E-mail: `{usuario['email']}`\n"
                    f"💰 Banca Inicial: `${usuario['banca']:.2f}`\n"
                    f"🎯 Meta Diária: `{meta}`\n\n"
                    f"O robô está pronto. Para reiniciar a configuração a qualquer momento, digite `/start`."
                )
            else:
                if texto == "/start":
                    usuario["etapa"] = "AGUARDANDO_EMAIL"
                    enviar_mensagem(chat_id, "🤖 **Reiniciando...**\n\n1️⃣ Digite o seu **e-mail** da IQ Option:")
                else:
                    enviar_mensagem(chat_id, "Para reiniciar o fluxo de configuração, digite `/start`.")
                    
    except Exception as e:
        print(f"Erro no loop: {e}")
        
    return offset

if __name__ == "__main__":
    print("Robô configurado no fluxo correto e iniciado na nuvem...")
    ultimo_offset = 0
    while True:
        ultimo_offset = processar_mensagens(ultimo_offset)
        time.sleep(1)
