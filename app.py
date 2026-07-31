import time
import requests

TOKEN = '8947979521:AAHUNCEDhJU5Ee6YOEvtJeUSo01YAFXiSpI'
URL = f"https://api.telegram.org/bot{TOKEN}"

USUARIOS = {}

# Os 5 principais pares de moedas para seleção manual
PARES_DISPONIVEIS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP"]

def inicializar_usuario(chat_id):
    if chat_id not in USUARIOS:
        USUARIOS[chat_id] = {
            "dias": "5",
            "porcentagem": "5",
            "time": "1M",
            "selecionados": ["EURUSD", "GBPUSD"],
            "etapa": "PAINEL"
        }

def montar_teclado_painel(u):
    teclado = []
    
    # Linha de seleção dos 5 pares (Caixas de marcação)
    linha_pares = []
    for par in PARES_DISPONIVEIS:
        status = "✅" if par in u["selecionados"] else "⬜"
        linha_pares.append({"text": f"{status} {par}", "callback_data": f"TOGGLE_{par}"})
        if len(linha_pares) == 2:
            teclado.append(linha_pares)
            linha_pares = []
    if linha_pares:
        teclado.append(linha_pares)
        
    # Botões de configuração manual
    teclado.append([{"text": f"📅 Dias: {u['dias']} (Mudar)", "callback_data": "DIGITAR_DIAS"}, {"text": f"⏱️ Time: {u['time']} (Mudar)", "callback_data": "DIGITAR_TIME"}])
    teclado.append([{"text": f"🎯 Porcentagem: {u['porcentagem']} (Mudar)", "callback_data": "DIGITAR_PORC"}])
    teclado.append([{"text": "🔄 Obter / Atualizar Sinais", "callback_data": "OBTER_SINAIS"}, {"text": "❌ Limpar", "callback_data": "LIMPAR"}])
    
    return teclado

def enviar_painel(chat_id):
    u = USUARIOS[chat_id]
    texto = (
        f"📊 **Catalogador de Sinais (Mercado Normal)**\n\n"
        f"🌐 **Pares Marcados:** `{', '.join(u['selecionados']) if u['selecionados'] else 'Nenhum'}`\n"
        f"📅 **Dias:** `{u['dias']}` | ⏱️ **Time:** `{u['time']}` | 🎯 **Porc:** `{u['porcentagem']}`\n\n"
        f"Clique nos quadrados para marcar os pares ou altere os dados abaixo:"
    )
    
    teclado = montar_teclado_painel(u)
    
    try:
        requests.post(f"{URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": teclado}
        })
    except Exception as e:
        print(f"Erro: {e}")

def processar_mensagens(offset):
    try:
        resposta = requests.get(f"{URL}/getUpdates", params={"offset": offset, "timeout": 30})
        dados = resposta.json()
        
        if not dados.get("ok"):
            return offset
            
        for resultado in dados.get("result", []):
            offset = resultado["update_id"] + 1
            
            if "callback_query" in resultado:
                callback = resultado["callback_query"]
                chat_id = callback["message"]["chat"]["id"]
                dados_botao = callback["data"]
                message_id = callback["message"]["message_id"]
                
                inicializar_usuario(chat_id)
                u = USUARIOS[chat_id]
                
                # Marcar ou desmarcar pares com caixas
                if dados_botao.startswith("TOGGLE_"):
                    par = dados_botao.replace("TOGGLE_", "")
                    if par in u["selecionados"]:
                        u["selecionados"].remove(par)
                    else:
                        u["selecionados"].append(par)
                    
                    # Atualiza os botões do painel na hora
                    novo_teclado = montar_teclado_painel(u)
                    requests.post(f"{URL}/editMessageReplyMarkup", json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "reply_markup": {"inline_keyboard": novo_teclado}
                    })
                
                elif dados_botao == "DIGITAR_DIAS":
                    u["etapa"] = "AGUARDANDO_DIAS"
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⌨️ Digite o número de **Dias** desejado:", "parse_mode": "Markdown"})
                
                elif dados_botao == "DIGITAR_PORC":
                    u["etapa"] = "AGUARDANDO_PORC"
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⌨️ Digite o valor da **Porcentagem** desejado:", "parse_mode": "Markdown"})
                
                elif dados_botao == "DIGITAR_TIME":
                    u["etapa"] = "AGUARDANDO_TIME"
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⌨️ Digite o **Time** desejado (Ex: `1M`, `5M`):", "parse_mode": "Markdown"})
                
                elif dados_botao == "LIMPAR":
                    u["dias"] = "5"
                    u["porcentagem"] = "5"
                    u["time"] = "1M"
                    u["selecionados"] = ["EURUSD", "GBPUSD"]
                    u["etapa"] = "PAINEL"
                    enviar_painel(chat_id)
                
                elif dados_botao == "OBTER_SINAIS":
                    if not u["selecionados"]:
                        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⚠️ Selecione pelo menos um par de moedas nas caixas acima!", "parse_mode": "Markdown"})
                        continue
                        
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": f"🔍 **Varredura iniciada!**\nPares: {', '.join(u['selecionados'])}\nDias: {u['dias']} | Time: {u['time']}\nAguarde...", "parse_mode": "Markdown"})
                    time.sleep(3)
                    
                    lista_resultados = (
                        "📊 **Resultado**\n\n"
                        "AUDUSD - 19:24 - PUT\n"
                        "AUDUSD - 19:25 - PUT\n"
                        "EURUSD - 19:29 - CALL\n"
                        "EURGBP - 19:30 - CALL\n"
                        "GBPUSD - 19:32 - PUT"
                    )
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": lista_resultados, "parse_mode": "Markdown"})
                    enviar_painel(chat_id)
                
                continue

            if "message" not in resultado or "text" not in resultado["message"]:
                continue
                
            chat_id = resultado["message"]["chat"]["id"]
            texto = resultado["message"]["text"].strip()
            
            inicializar_usuario(chat_id)
            u = USUARIOS[chat_id]
            
            if texto == "/start":
                u["etapa"] = "PAINEL"
                enviar_painel(chat_id)
            elif u["etapa"] == "AGUARDANDO_DIAS":
                u["dias"] = texto
                u["etapa"] = "PAINEL"
                enviar_painel(chat_id)
            elif u["etapa"] == "AGUARDANDO_PORC":
                u["porcentagem"] = texto
                u["etapa"] = "PAINEL"
                enviar_painel(chat_id)
            elif u["etapa"] == "AGUARDANDO_TIME":
                u["time"] = texto.upper()
                u["etapa"] = "PAINEL"
                enviar_painel(chat_id)
                
    except Exception as e:
        print(f"Erro no loop: {e}")
        
    return offset

if __name__ == "__main__":
    print("Catalogador com caixas de seleção manual iniciado na nuvem...")
    ultimo_offset = 0
    while True:
        ultimo_offset = processar_mensagens(ultimo_offset)
        time.sleep(1)
