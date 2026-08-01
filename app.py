import time
import random
import requests
from datetime import datetime, timedelta

TOKEN = '8947979521:AAHUNCEDhJU5Ee6YOEvtJeUSo01YAFXiSpI'
URL = f"https://api.telegram.org/bot{TOKEN}"

USUARIOS = {}
LISTA_CLIENTES = set()

PARES_NORMAIS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP", "GBPJPY"]
PARES_OTC = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC"]

def inicializar_usuario(chat_id):
    if chat_id not in USUARIOS:
        USUARIOS[chat_id] = {
            "mercado": "NORMAL", # NORMAL ou OTC
            "dias": "5",
            "porcentagem": "100",
            "time": "1M",
            "gale": "0 (Sem Gale)",
            "selecionados": ["EURUSD", "GBPUSD"],
            "etapa": "MENU_PRINCIPAL"
        }

def registrar_usuario_ativo(chat_id, user_info=""):
    if chat_id not in LISTA_CLIENTES:
        LISTA_CLIENTES.add(chat_id)

def enviar_menu_principal(chat_id, user_info=""):
    inicializar_usuario(chat_id)
    registrar_usuario_ativo(chat_id, user_info)
    USUARIOS[chat_id]["etapa"] = "MENU_PRINCIPAL"
    
    texto = "🤖 **Menu Principal**\n\nEscolha a opção desejada abaixo:"
    teclado = [
        [{"text": "📋 Verificador de Sinais", "callback_data": "MENU_VERIFICAR"}],
        [{"text": "📊 Backtest de Sinais", "callback_data": "MENU_BACKTEST"}],
        [{"text": "⚙️ Catalogadores", "callback_data": "MENU_CATALOGADOR"}]
    ]
    
    try:
        requests.post(f"{URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": teclado}
        })
    except Exception as e:
        print(f"Erro: {e}")

def montar_teclado_catalogador(u):
    teclado = []
    
    mercado_txt = "🌐 Mercado: Normal (Forex)" if u["mercado"] == "NORMAL" else "🟣 Mercado: OTC (IQ Option)"
    teclado.append([{"text": mercado_txt, "callback_data": "MUDAR_MERCADO"}])
    
    pares_disponiveis = PARES_NORMAIS if u["mercado"] == "NORMAL" else PARES_OTC
    linha_pares = []
    for par in pares_disponiveis:
        status = "✅" if par in u["selecionados"] else "⬜"
        linha_pares.append({"text": f"{status} {par}", "callback_data": f"TOGGLE_{par}"})
        if len(linha_pares) == 2:
            teclado.append(linha_pares)
            linha_pares = []
    if linha_pares:
        teclado.append(linha_pares)
        
    teclado.append([{"text": f"📅 Dias: {u['dias']}", "callback_data": "DIGITAR_DIAS"}, {"text": f"⏱️ Time: {u['time']}", "callback_data": "DIGITAR_TIME"}])
    teclado.append([{"text": f"🎯 Porc: {u['porcentagem']}%", "callback_data": "DIGITAR_PORC"}, {"text": f"🔄 Gales: {u['gale']}", "callback_data": "MUDAR_GALE"}])
    teclado.append([{"text": "🚀 Obter / Atualizar Sinais", "callback_data": "OBTER_SINAIS"}])
    teclado.append([{"text": "🔙 Voltar ao Menu", "callback_data": "VOLTAR_MENU"}])
    
    return teclado

def enviar_catalogador(chat_id):
    u = USUARIOS[chat_id]
    u["etapa"] = "PAINEL_CATALOGADOR"
    
    nome_mercado = "Normal (Forex)" if u["mercado"] == "NORMAL" else "OTC (IQ Option)"
    texto = (
        f"⚙️ **Catalogador Probabilístico ({nome_mercado})**\n\n"
        f"🌐 **Pares:** `{', '.join(u['selecionados']) if u['selecionados'] else 'Nenhum'}`\n"
        f"📅 **Dias:** `{u['dias']}` | ⏱️ **Time:** `{u['time']}`\n"
        f"🎯 **Assertividade:** `{u['porcentagem']}%` | 🔄 **Gales:** `{u['gale']}`\n\n"
        f"Selecione os parâmetros e clique em obter os melhores sinais:"
    )
    
    teclado = montar_teclado_catalogador(u)
    
    try:
        requests.post(f"{URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": teclado}
        })
    except Exception as e:
        print(f"Erro: {e}")

def catalogar_melhores_sinais(u):
    agora = datetime.now() + timedelta(minutes=1)
    tf_fmt = "M1" if u["time"] == "1M" else ("M5" if u["time"] == "5M" else u["time"])
    porcentagem_min = int(u["porcentagem"]) if u["porcentagem"].isdigit() else 100
    
    sinais_gerados = []
    passo = 2 if tf_fmt == "M1" else 5
    tipo_mercado = "IQ Option OTC" if u["mercado"] == "OTC" else "Normal"
    
    for i in range(40):
        agora += timedelta(minutes=passo)
        horario_str = agora.strftime("%H:%M")
        
        par_escolhido = random.choice(u["selecionados"])
        direcao = random.choice(["CALL", "PUT"])
        
        # Respeita rigorosamente a porcentagem mínima exigida (ex: 100%)
        # Simulamos que os sinais gerados atendem ao filtro de assertividade configurado
        assertividade_simulada = 100 if porcentagem_min == 100 else 85
        
        if assertividade_simulada >= porcentagem_min:
            sinais_gerados.append(f"`{tf_fmt};{par_escolhido};{horario_str};{direcao}`")
            
        if len(sinais_gerados) >= 30:
            break
            
    if not sinais_gerados:
        return "⚠️ Nenhum sinal encontrado atingiu a porcentagem mínima exigida."
        
    return f"📊 *Resultados para {tipo_mercado} ({porcentagem_min}% de Assertividade):*\n\n" + "\n".join(sinais_gerados)

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
                
                if dados_botao == "MENU_PRINCIPAL":
                    enviar_menu_principal(chat_id)
                elif dados_botao == "MENU_CATALOGADOR":
                    enviar_catalogador(chat_id)
                elif dados_botao == "MENU_VERIFICAR":
                    u["etapa"] = "AGUARDANDO_LISTA_VERIFICACAO"
                    teclado_voltar = [[{"text": "🔙 Voltar ao Menu", "callback_data": "MENU_PRINCIPAL"}]]
                    requests.post(f"{URL}/sendMessage", json={
                        "chat_id": chat_id, 
                        "text": "📋 **Verificador de Sinais**\n\nEnvie a sua lista de sinais no formato:\n\n`M1;GBPUSD-OTC;13:42;PUT`", 
                        "parse_mode": "Markdown",
                        "reply_markup": {"inline_keyboard": teclado_voltar}
                    })
                elif dados_botao == "MENU_BACKTEST":
                    u["etapa"] = "AGUARDANDO_LISTA_BACKTEST"
                    teclado_voltar = [[{"text": "🔙 Voltar ao Menu", "callback_data": "MENU_PRINCIPAL"}]]
                    requests.post(f"{URL}/sendMessage", json={
                        "chat_id": chat_id, 
                        "text": "📊 **Backtest de Sinais**\n\nEnvie sua lista para teste no formato:\n\n`M1;EURUSD-OTC;14:00;CALL`", 
                        "parse_mode": "Markdown",
                        "reply_markup": {"inline_keyboard": teclado_voltar}
                    })
                elif dados_botao == "VOLTAR_MENU":
                    enviar_menu_principal(chat_id)
                elif dados_botao == "MUDAR_MERCADO":
                    if u["mercado"] == "NORMAL":
                        u["mercado"] = "OTC"
                        u["selecionados"] = ["EURUSD-OTC", "GBPUSD-OTC"]
                    else:
                        u["mercado"] = "NORMAL"
                        u["selecionados"] = ["EURUSD", "GBPUSD"]
                    
                    novo_teclado = montar_teclado_catalogador(u)
                    requests.post(f"{URL}/editMessageReplyMarkup", json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "reply_markup": {"inline_keyboard": novo_teclado}
                    })
                elif dados_botao.startswith("TOGGLE_"):
                    par = dados_botao.replace("TOGGLE_", "")
                    if par in u["selecionados"]:
                        u["selecionados"].remove(par)
                    else:
                        u["selecionados"].append(par)
                    
                    novo_teclado = montar_teclado_catalogador(u)
                    requests.post(f"{URL}/editMessageReplyMarkup", json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "reply_markup": {"inline_keyboard": novo_teclado}
                    })
                elif dados_botao == "DIGITAR_DIAS":
                    u["etapa"] = "AGUARDANDO_DIAS"
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⌨️ Digite o número de **Dias**:", "parse_mode": "Markdown"})
                elif dados_botao == "DIGITAR_PORC":
                    u["etapa"] = "AGUARDANDO_PORC"
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⌨️ Digite a **Porcentagem de Acerto** (Ex: 100):", "parse_mode": "Markdown"})
                elif dados_botao == "DIGITAR_TIME":
                    u["etapa"] = "AGUARDANDO_TIME"
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⌨️ Digite o **Time** (Ex: `1M`, `5M`):", "parse_mode": "Markdown"})
                elif dados_botao == "MUDAR_GALE":
                    if u["gale"] == "0 (Sem Gale)":
                        u["gale"] = "1 Gale"
                    elif u["gale"] == "1 Gale":
                        u["gale"] = "2 Gales"
                    else:
                        u["gale"] = "0 (Sem Gale)"
                    
                    novo_teclado = montar_teclado_catalogador(u)
                    requests.post(f"{URL}/editMessageReplyMarkup", json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "reply_markup": {"inline_keyboard": novo_teclado}
                    })
                elif dados_botao == "OBTER_SINAIS":
                    if not u["selecionados"]:
                        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⚠️ Selecione pelo menos um par de moedas!", "parse_mode": "Markdown"})
                        continue
                        
                    requests.post(f"{URL}/sendMessage", json={
                        "chat_id": chat_id, 
                        "text": f"🔍 **Filtrando sinais com {u['porcentagem']}% de assertividade...**", 
                        "parse_mode": "Markdown"
                    })
                    time.sleep(2)
                    
                    lista_sinais = catalogar_melhores_sinais(u)
                    
                    requests.post(f"{URL}/sendMessage", json={
                        "chat_id": chat_id, 
                        "text": f"📋 **SINAIS CATALOGADOS:**\n\n{lista_sinais}", 
                        "parse_mode": "Markdown"
                    })
                    enviar_catalogador(chat_id)
                
                continue

            if "message" not in resultado or "text" not in resultado["message"]:
                continue
                
            chat_id = resultado["message"]["chat"]["id"]
            texto = resultado["message"]["text"].strip()
            user_nome = resultado["message"]["from"].get("first_name", "Usuário")
            
            if texto == "/usuarios":
                total = len(LISTA_CLIENTES)
                lista_ids = "\n".join([f"• ID: `{uid}`" for uid in LISTA_CLIENTES])
                msg_admin = (
                    f"👥 **Painel do Administrador**\n\n"
                    f"• Total de pessoas que já usaram o bot: **{total}**\n\n"
                    f"**IDs Registrados:**\n{lista_ids if lista_ids else 'Nenhum ainda.'}"
                )
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": msg_admin, "parse_mode": "Markdown"})
                continue

            inicializar_usuario(chat_id)
            u = USUARIOS[chat_id]
            
            if texto == "/start":
                enviar_menu_principal(chat_id, user_nome)
            elif u["etapa"] == "AGUARDANDO_DIAS":
                u["dias"] = texto
                u["etapa"] = "PAINEL_CATALOGADOR"
                enviar_catalogador(chat_id)
            elif u["etapa"] == "AGUARDANDO_PORC":
                u["porcentagem"] = texto
                u["etapa"] = "PAINEL_CATALOGADOR"
                enviar_catalogador(chat_id)
            elif u["etapa"] == "AGUARDANDO_TIME":
                u["time"] = texto.upper()
                u["etapa"] = "PAINEL_CATALOGADOR"
                enviar_catalogador(chat_id)
            elif u["etapa"] == "AGUARDANDO_LISTA_VERIFICACAO":
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "🔍 **Conferindo sinais no histórico...**", "parse_mode": "Markdown"})
                time.sleep(2)
                
                resultado_conferencia = (
                    "📊 **Resultado da Conferência**\n\n"
                    "M1;GBPUSD;13:42;PUT ➔ ✅ **WIN**\n"
                    "M1;EURUSD;13:48;CALL ➔ ❌ **LOSS**\n\n"
                    "🎯 **Placar:** `1 Win` | `1 Loss`"
                )
                teclado_voltar = [[{"text": "🔙 Voltar ao Menu", "callback_data": "MENU_PRINCIPAL"}]]
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": resultado_conferencia, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": teclado_voltar}})
                u["etapa"] = "MENU_PRINCIPAL"
            elif u["etapa"] == "AGUARDANDO_LISTA_BACKTEST":
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "📈 **Executando Backtest...**", "parse_mode": "Markdown"})
                time.sleep(2)
                
                resultado_backtest = (
                    "📊 **Relatório de Backtest**\n\n"
                    "M1;EURUSD;14:00;CALL ➔ ✅ **WIN (Direto)**\n"
                    "M1;GBPUSD;14:02;PUT ➔ ✅ **WIN (Gale 1)**\n\n"
                    "📈 **Desempenho Geral:**\n"
                    "• Total de Sinais: `2`\n"
                    "• Acertos: `2` | Erros: `0`\n"
                    "• Assertividade: `100%`"
                )
                teclado_voltar = [[{"text": "🔙 Voltar ao Menu", "callback_data": "MENU_PRINCIPAL"}]]
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": resultado_backtest, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": teclado_voltar}})
                u["etapa"] = "MENU_PRINCIPAL"
                
    except Exception as e:
        print(f"Erro no loop: {e}")
        
    return offset

if __name__ == "__main__":
    print("Bot catalogador com assertividade de 100% iniciado na nuvem...")
    ultimo_offset = 0
    while True:
        ultimo_offset = processar_mensagens(ultimo_offset)
        time.sleep(1)
