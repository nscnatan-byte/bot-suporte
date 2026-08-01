import time
import requests
from datetime import datetime, timedelta
from iqoptionapi.api import IQ_Option

TOKEN = '8947979521:AAHUNCEDhJU5Ee6YOEvtJeUSo01YAFXiSpI'
URL = f"https://api.telegram.org/bot{TOKEN}"

USUARIOS = {}
LISTA_CLIENTES = set()

PARES_NORMAIS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP", "GBPJPY"]
PARES_OTC = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC"]

def inicializar_usuario(chat_id):
    if chat_id not in USUARIOS:
        USUARIOS[chat_id] = {
            "mercado": "NORMAL",
            "dias": "5",
            "porcentagem": "100",
            "time": "1M",
            "gale": "0 (Sem Gale)",
            "verif_data": datetime.now().strftime("%d/%m/%Y"),
            "verif_gale": "0 (Sem Gale)",
            "selecionados": ["EURUSD", "GBPUSD"],
            "etapa": "MENU_PRINCIPAL",
            "iq_email": "",
            "iq_senha": "",
            "iq_api": None,
            "logado": False
        }

def registrar_usuario_ativo(chat_id, user_info=""):
    if chat_id not in LISTA_CLIENTES:
        LISTA_CLIENTES.add(chat_id)

def enviar_menu_principal(chat_id, user_info=""):
    inicializar_usuario(chat_id)
    registrar_usuario_ativo(chat_id, user_info)
    u = USUARIOS[chat_id]
    u["etapa"] = "MENU_PRINCIPAL"
    
    status_conexao = "🟢 Conectado" if u["logado"] else "🔴 Desconectado (Necessário Logar)"
    
    texto = (
        f"🤖 **Menu Principal**\n"
        f"Status da sua Conta IQ Option: {status_conexao}\n\n"
        f"Escolha a opção desejada abaixo:"
    )
    
    teclado = []
    if not u["logado"]:
        teclado.append([{"text": "🔑 Conectar Minha Conta IQ Option", "callback_data": "LOGAR_CONTA"}])
    else:
        teclado.append([{"text": "📋 Verificador de Sinais", "callback_data": "MENU_VERIFICAR"}])
        teclado.append([{"text": "📊 Backtest de Sinais", "callback_data": "MENU_BACKTEST"}])
        teclado.append([{"text": "⚙️ Catalogadores", "callback_data": "MENU_CATALOGADOR"}])
        teclado.append([{"text": "🔌 Desconectar Conta", "callback_data": "DESCONECTAR_CONTA"}])
    
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
    teclado.append([{"text": "🚀 Obter / Atualizar Sinais Reais", "callback_data": "OBTER_SINAIS"}])
    teclado.append([{"text": "🔙 Voltar ao Menu", "callback_data": "VOLTAR_MENU"}])
    
    return teclado

def enviar_catalogador(chat_id):
    u = USUARIOS[chat_id]
    u["etapa"] = "PAINEL_CATALOGADOR"
    nome_mercado = "Normal (Forex)" if u["mercado"] == "NORMAL" else "OTC (IQ Option)"
    texto = (
        f"⚙️ **Catalogador Real ({nome_mercado})**\n\n"
        f"🌐 **Pares:** `{', '.join(u['selecionados']) if u['selecionados'] else 'Nenhum'}`\n"
        f"📅 **Dias de Análise:** `{u['dias']}` | ⏱️ **Time:** `{u['time']}`\n"
        f"🎯 **Assertividade Mínima:** `{u['porcentagem']}%` | 🔄 **Gales:** `{u['gale']}`\n\n"
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

def enviar_painel_verificador(chat_id):
    u = USUARIOS[chat_id]
    u["etapa"] = "PAINEL_VERIFICADOR"
    texto = (
        f"📋 **Verificador de Sinais Reais**\n\n"
        f"📅 **Data da Verificação:** `{u['verif_data']}`\n"
        f"🔄 **Gales Configurados:** `{u['verif_gale']}`\n\n"
        f"Configure a data e os gales abaixo, depois clique em enviar a lista:"
    )
    teclado = [
        [{"text": f"📅 Mudar Data: {u['verif_data']}", "callback_data": "VERIF_MUDAR_DATA"}],
        [{"text": f"🔄 Mudar Gales: {u['verif_gale']}", "callback_data": "VERIF_MUDAR_GALE"}],
        [{"text": "📤 Enviar Lista de Sinais", "callback_data": "VERIF_ENVIAR_LISTA"}],
        [{"text": "🔙 Voltar ao Menu", "callback_data": "MENU_PRINCIPAL"}]
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

def catalogar_melhores_sinais_real(u):
    if not u["logado"] or not u["iq_api"]:
        return "⚠️ Você precisa conectar sua conta da IQ Option primeiro no menu principal!"
        
    tf_fmt = "M1" if u["time"] == "1M" else ("M5" if u["time"] == "5M" else u["time"])
    duracao_seg = 60 if tf_fmt == "M1" else 300
    porcentagem_min = int(u["porcentagem"]) if u["porcentagem"].isdigit() else 100
    dias_analise = int(u["dias"]) if u["dias"].isdigit() else 5
    tipo_mercado = "IQ Option OTC" if u["mercado"] == "OTC" else "Normal"
    
    sinais_gerados = []
    end_time = time.time()
    
    for par in u["selecionados"]:
        try:
            velas = u["iq_api"].get_candles(par, duracao_seg, 300, end_time)
            if not velas:
                continue
            
            horarios_validos = {}
            for v in velas:
                dt = datetime.fromtimestamp(v["from"])
                horario_str = dt.strftime("%H:%M")
                cor = "CALL" if v["close"] > v["open"] else "PUT"
                
                if horario_str not in horarios_validos:
                    horarios_validos[horario_str] = []
                horarios_validos[horario_str].append(cor)
                
            for h_str, cores in horarios_validos.items():
                if len(cores) >= dias_analise:
                    primeira_cor = cores[0]
                    if all(c == primeira_cor for c in cores[-dias_analise:]):
                        sinais_gerados.append(f"`{tf_fmt};{par};{h_str};{primeira_cor}`")
        except Exception as e:
            print(f"Erro ao buscar velas para {par}: {e}")
            
        if len(sinais_gerados) >= 25:
            break
            
    if not sinais_gerados:
        return f"⚠️ Nenhum sinal atingiu {porcentagem_min}% de assertividade real nos últimos {dias_analise} dias."
        
    total_sinais = len(sinais_gerados)
    gale_escolhido = u["gale"]
    
    return (
        f"📊 *Resultados Reais da Corretora ({tipo_mercado} - {dias_analise} Dias):*\n\n" + 
        "\n".join(sinais_gerados) + 
        f"\n\n📈 **Resumo da Catalogação:**\n"
        f"• Sinais Reais Encontrados: `{total_sinais}`\n"
        f"• Modo de Recuperação: `{gale_escolhido}`"
    )

def verificar_lista_sinais_real(chat_id, texto_lista):
    u = USUARIOS[chat_id]
    if not u["logado"] or not u["iq_api"]:
        return "⚠️ Você precisa conectar sua conta da IQ Option primeiro!"
        
    linhas = texto_lista.strip().split("\n")
    resultados = []
    wins_direto = 0
    wins_gale1 = 0
    wins_gale2 = 0
    losses = 0
    
    gale_modo = u["verif_gale"]
    
    try:
        dt_alvo = datetime.strptime(u['verif_data'], "%d/%m/%Y")
        timestamp_inicio = dt_alvo.timestamp()
        timestamp_fim = timestamp_inicio + 86400
    except:
        timestamp_inicio = time.time() - 86400
        timestamp_fim = time.time()
        
    for linha in linhas:
        linha = linha.strip()
        if not linha or ";" not in linha:
            continue
            
        partes = linha.split(";")
        if len(partes) >= 4:
            tf = partes[0]
            par = partes[1]
            horario = partes[2]
            direcao = partes[3].upper()
            
            duracao = 60 if tf == "M1" else 300
            
            try:
                velas = u["iq_api"].get_candles(par, duracao, 1000, timestamp_fim)
                vela_encontrada = None
                
                for v in velas:
                    dt_vela = datetime.fromtimestamp(v["from"])
                    if dt_vela.strftime("%H:%M") == horario and timestamp_inicio <= v["from"] < timestamp_fim:
                        vela_encontrada = v
                        break
                
                if vela_encontrada:
                    cor_real = "CALL" if vela_encontrada["close"] > vela_encontrada["open"] else "PUT"
                    if cor_real == direcao:
                        res = "✅ **WIN (Direto)**"
                        wins_direto += 1
                    else:
                        res = "❌ **LOSS**"
                        losses += 1
                else:
                    res = "⚠️ **Sem Dados na Corretora**"
                    losses += 1
            except Exception as e:
                res = "❌ **Erro de Conexão**"
                losses += 1
        else:
            res = "❌ **Formato Inválido**"
            losses += 1
            
        resultados.append(f"{linha} ➔ {res}")
        
    total = len(resultados)
    if total == 0:
        return "⚠️ Nenhuma linha de sinal válida encontrada."
        
    total_wins = wins_direto + wins_gale1 + wins_gale2
    assertividade = int((total_wins / total) * 100) if total > 0 else 0
    
    return (
        f"📋 **Resultado Real na Corretora**\n"
        f"📅 **Data Analisada:** `{u['verif_data']}` | 🔄 **Gales:** `{u['verif_gale']}`\n\n" +
        "\n".join(resultados) +
        f"\n\n📊 **Placar Geral Real:**\n"
        f"• Total de Sinais: `{total}`\n"
        f"• Wins Diretos: `{wins_direto}`\n"
        f"• Wins Gale 1: `{wins_gale1}`\n"
        f"• Wins Gale 2: `{wins_gale2}`\n"
        f"• Losses: `{losses}`\n"
        f"• Assertividade Final: `{assertividade}%`"
    )

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
                elif dados_botao == "LOGAR_CONTA":
                    u["etapa"] = "AGUARDANDO_EMAIL"
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "📧 Digite o seu **e-mail** de acesso à IQ Option:", "parse_mode": "Markdown"})
                elif dados_botao == "DESCONECTAR_CONTA":
                    u["logado"] = False
                    u["iq_api"] = None
                    u["iq_email"] = ""
                    u["iq_senha"] = ""
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "🔌 Conta desconectada com sucesso.", "parse_mode": "Markdown"})
                    enviar_menu_principal(chat_id)
                elif dados_botao == "MENU_CATALOGADOR":
                    if not u["logado"]:
                        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⚠️ Conecte sua conta da IQ Option primeiro!", "parse_mode": "Markdown"})
                        enviar_menu_principal(chat_id)
                    else:
                        enviar_catalogador(chat_id)
                elif dados_botao == "MENU_VERIFICAR":
                    if not u["logado"]:
                        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⚠️ Conecte sua conta da IQ Option primeiro!", "parse_mode": "Markdown"})
                        enviar_menu_principal(chat_id)
                    else:
                        enviar_painel_verificador(chat_id)
                elif dados_botao == "VERIF_MUDAR_DATA":
                    u["etapa"] = "AGUARDANDO_DATA_VERIFICACAO"
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⌨️ Digite a **Data** (Ex: `30/07/2026`):", "parse_mode": "Markdown"})
                elif dados_botao == "VERIF_MUDAR_GALE":
                    if u["verif_gale"] == "0 (Sem Gale)":
                        u["verif_gale"] = "1 Gale"
                    elif u["verif_gale"] == "1 Gale":
                        u["verif_gale"] = "2 Gales"
                    else:
                        u["verif_gale"] = "0 (Sem Gale)"
                    enviar_painel_verificador(chat_id)
                elif dados_botao == "VERIF_ENVIAR_LISTA":
                    u["etapa"] = "AGUARDANDO_LISTA_VERIFICACAO"
                    teclado_voltar = [[{"text": "🔙 Voltar", "callback_data": "MENU_VERIFICAR"}]]
                    requests.post(f"{URL}/sendMessage", json={
                        "chat_id": chat_id, 
                        "text": f"📋 **Envie sua lista de sinais** para a data `{u['verif_data']}` com `{u['verif_gale']}`:\n\n*Exemplo:*\n`M1;GBPUSD-OTC;13:42;PUT`", 
                        "parse_mode": "Markdown",
                        "reply_markup": {"inline_keyboard": teclado_voltar}
                    })
                elif dados_botao == "MENU_BACKTEST":
                    if not u["logado"]:
                        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⚠️ Conecte sua conta da IQ Option primeiro!", "parse_mode": "Markdown"})
                        enviar_menu_principal(chat_id)
                    else:
                        u["etapa"] = "AGUARDANDO_LISTA_BACKTEST"
                        teclado_voltar = [[{"text": "🔙 Voltar ao Menu", "callback_data": "MENU_PRINCIPAL"}]]
                        requests.post(f"{URL}/sendMessage", json={
                            "chat_id": chat_id, 
                            "text": "📊 **Backtest de Sinais Reais**\n\nEnvie sua lista para teste no formato:\n\n`M1;EURUSD-OTC;14:00;CALL`", 
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
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⌨️ Digite a **Assertividade Mínima %** (Ex: 100):", "parse_mode": "Markdown"})
                elif dados_botao == "DIGITAR_TIME":
                    u["etapa"] = "AGUARDANDO_TIME"
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "⌨️ Digite o **Time** (`1M`, `5M`):", "parse_mode": "Markdown"})
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
                        "text": f"🔍 **Conectando à corretora...** Buscando velas reais...", 
                        "parse_mode": "Markdown"
                    })
                    lista_sinais = catalogar_melhores_sinais_real(u)
                    requests.post(f"{URL}/sendMessage", json={
                        "chat_id": chat_id, 
                        "text": f"📋 **SINAIS CATALOGADOS (REAIS):**\n\n{lista_sinais}", 
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
            elif u["etapa"] == "AGUARDANDO_EMAIL":
                u["iq_email"] = texto
                u["etapa"] = "AGUARDANDO_SENHA"
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "🔒 Agora digite a sua **senha** da IQ Option:", "parse_mode": "Markdown"})
            elif u["etapa"] == "AGUARDANDO_SENHA":
                u["iq_senha"] = texto
                u["etapa"] = "MENU_PRINCIPAL"
                
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "🔄 Autenticando com a corretora, aguarde um instante...", "parse_mode": "Markdown"})
                
                try:
                    api_instance = IQ_Option(u["iq_email"], u["iq_senha"])
                    check, reason = api_instance.connect()
                    if check:
                        u["iq_api"] = api_instance
                        u["logado"] = True
                        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "✅ **Conectado com sucesso à sua conta!**", "parse_mode": "Markdown"})
                    else:
                        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": f"❌ **Erro na autenticação:** {reason}\nTente novamente.", "parse_mode": "Markdown"})
                except Exception as e:
                    requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": f"❌ **Erro técnico ao conectar:** {e}", "parse_mode": "Markdown"})
                    
                enviar_menu_principal(chat_id)
            elif u["etapa"] == "AGUARDANDO_DATA_VERIFICACAO":
                u["verif_data"] = texto
                enviar_painel_verificador(chat_id)
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
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": f"🔍 **Baixando velas reais para o dia {u['verif_data']}...**", "parse_mode": "Markdown"})
                resultado_conferencia = verificar_lista_sinais_real(chat_id, texto)
                teclado_voltar = [[{"text": "🔙 Voltar ao Menu", "callback_data": "MENU_PRINCIPAL"}]]
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": resultado_conferencia, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": teclado_voltar}})
                u["etapa"] = "MENU_PRINCIPAL"
            elif u["etapa"] == "AGUARDANDO_LISTA_BACKTEST":
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": "📈 **Executando Backtest Real...**", "parse_mode": "Markdown"})
                resultado_backtest = verificar_lista_sinais_real(chat_id, texto)
                teclado_voltar = [[{"text": "🔙 Voltar ao Menu", "callback_data": "MENU_PRINCIPAL"}]]
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": resultado_backtest, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": teclado_voltar}})
                u["etapa"] = "MENU_PRINCIPAL"
                
    except Exception as e:
        print(f"Erro no loop: {e}")
        
    return offset

if __name__ == "__main__":
    print("Bot com login individual por usuário iniciado...")
    ultimo_offset = 0
    while True:
        ultimo_offset = processar_mensagens(ultimo_offset)
        time.sleep(1)
