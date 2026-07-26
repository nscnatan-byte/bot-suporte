import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

def run_fake_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive!")
        def log_message(self, format, *args):
            return

    server = HTTPServer(("0.0.0.0", 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

import easyocr
import json
import os
import glob
from datetime import datetime

# =========================================
# TOKEN
# =========================================

TOKEN = "8977968510:AAH5gCJ8UeS6-DbfwN-AlTFxqbHDUQXxUjc"

# =========================================
# IDS
# =========================================

ATIVADOR_ID = 929855491
DONO_ID = 674527541

# =========================================
# LINK BOT
# =========================================

BOT_PRIVADO = "https://t.me/suporte_xbotbot"

# =========================================
# DADOS E PERSISTÊNCIA (PARA NÃO PERDER AO REINICIAR)
# =========================================

ARQUIVO_ESTADO = "dados_clientes.json"

def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        try:
            with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados.get("clientes", {}), dados.get("status_cliente", {})
        except Exception as e:
            print(f"Erro ao carregar estado: {e}")
    return {}, {}

def salvar_estado():
    try:
        dados = {
            "clientes": clientes,
            "status_cliente": status_cliente
        }
        with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar estado: {e}")

clientes, status_cliente = carregar_estado()
# Converte as chaves de string para int, já que o json converte chaves de dicionário para string
clientes = {int(k): v for k, v in clientes.items()}
status_cliente = {int(k): v for k, v in status_cliente.items()}

recibos_usados = set()
arquivos_processados = set()  # Guarda o nome dos arquivos para evitar reprocessamento

# =========================================
# TABELA FIXA DE DESCONTO USDT (EM REAIS)
# =========================================
TABELA_DESCONTO_USDT = {
    "4": 10.00,
    "7.60": 19.00,
    "10.80": 27.00,
    "13.60": 34.00,
    "16": 40.00,
    "18": 45.00,
    "32.40": 81.00
}

# =========================================
# OCR (INICIALIZAÇÃO)
# =========================================

leitor = easyocr.Reader(['pt'], gpu=False)

# =========================================
# SISTEMA ANTI-FRAUDE: MAPEAMENTO OTIMIZADO
# =========================================

def carregar_historico_comprovantes_salvos():
    """
    Apenas indexa os nomes dos arquivos existentes.
    Evita passar o EasyOCR em tudo ao iniciar, fazendo o bot ligar INSTANTANEAMENTE.
    """
    print("⏳ Indexando imagens antigas na pasta de segurança...")
    imagens_salvas = glob.glob("comprovante_*.jpg")
    
    for imagem in imagens_salvas:
        arquivos_processados.add(imagem)
            
    print(f"✅ Varredura concluída! {len(arquivos_processados)} arquivos antigos indexados. Bot pronto!")

# Executa a varredura instantânea ao ligar o bot
carregar_historico_comprovantes_salvos()

# =========================================
# MENU
# =========================================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    teclado = [[
        InlineKeyboardButton(
            "💳 PROSEGUIR COM PAGAMENTO",
            callback_data="pagamento"
        )
    ]]

    reply_markup = InlineKeyboardMarkup(teclado)

    await update.message.reply_text(

        "🔥 BEM VINDO 🔥\n\n"
        "Clique abaixo para continuar.",

        reply_markup=reply_markup
    )

# =========================================
# TESTE
# =========================================

async def teste(update: Update, context: ContextTypes.DEFAULT_TYPE):

    usuario_id = update.effective_chat.id

    if usuario_id not in clientes:

        clientes[usuario_id] = {

            "valor": "0",
            "plano": "TESTE",
            "tipo": "pix"

        }

    status_cliente[usuario_id] = "aguardando_email"
    salvar_estado()

    teclado = [[
        InlineKeyboardButton(
            "📧 ENVIAR EMAIL",
            callback_data="email"
        )
    ]]

    reply_markup = InlineKeyboardMarkup(teclado)

    await update.message.reply_text(

        "✅ PAGAMENTO LIBERADO.\n\n"
        "📧 Agora envie seu email.",

        reply_markup=reply_markup
    )

# =========================================
# FINANCEIRO
# =========================================

async def comando_financeiro(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if (
        update.effective_chat.id != DONO_ID
        and update.effective_chat.id != ATIVADOR_ID
    ):
        return

    import financeiro
    await update.message.reply_text(
        financeiro.painel()
    )

async def comando_clientes(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if (
        update.effective_chat.id != ATIVADOR_ID
        and update.effective_chat.id != DONO_ID
    ):
        return

    import financeiro
    await update.message.reply_text(
        financeiro.listar_clientes()
    )

async def comando_pagar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != DONO_ID:
        return

    try:

        valor = context.args[0]

        import financeiro
        financeiro.pagar_ativador(valor)

        total = financeiro.total_faturado()

        clientes_total = len(financeiro.clientes)

        await update.message.reply_text(

            "💰 FINANCEIRO XBOT 💰\n\n"

            f"👥 CLIENTES ATIVOS: {clientes_total}\n\n"

            f"💸 VALOR TOTAL:\n"
            f"R${total:.2f}"

        )

    except:

        await update.message.reply_text(
            "❌ Use:\n/pagar 100"
        )

# =========================================
# RETIRAR SALDO
# =========================================

async def comando_retira(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != DONO_ID:
        return

    try:

        valor = float(context.args[0])

        import financeiro
        financeiro.clientes.append({

            "usuario_id": 0,
            "email": "retirada@gmail.com",
            "plano": "RETIRADA",
            "valor": 0,
            "historico": -valor,
            "tipo": "manual"

        })

        financeiro.salvar()

        total = financeiro.total_faturado()

        clientes_total = len(financeiro.clientes)

        await update.message.reply_text(

            "💸 RETIRADA REALIZADA\n\n"

            f"👥 CLIENTES ATIVOS: {clientes_total}\n\n"

            f"💸 VALOR TOTAL:\n"
            f"R${total:.2f}"

        )

    except:

        await update.message.reply_text(
            "❌ Use:\n/retira 10"
        )


# =========================================
# RESETAR FINANCEIRO
# =========================================

async def comando_resetar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != DONO_ID:
        return

    clientes.clear()
    status_cliente.clear()
    salvar_estado()

    import financeiro
    if financeiro.clientes:
        try:
            data_atual = datetime.now().strftime("%d-%m-%Y_%H-%M")
            nome_backup = f"historico_financeiro_{data_atual}.json"
            
            with open(nome_backup, "w", encoding="utf-8") as f:
                json.dump(financeiro.clientes, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Aviso ao salvar backup: {e}")

    financeiro.clientes.clear()

    if hasattr(financeiro, 'salvar'):
        financeiro.salvar()

    await update.message.reply_text(
        "✅ **FINANCEIRO RESETADO COM SUCESSO!**\n\n"
        "👥 Clientes Ativos voltou para: **0**\n"
        "💰 Valor Total voltou para: **R$0.00**\n\n"
    )

# =========================================
# ADICIONAR SALDO POSITIVO (ACERTO / PAGAMENTO)
# =========================================

async def comando_addsaldo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != DONO_ID:
        return

    try:
        # Força o valor a ser estritamente POSITIVO
        valor = abs(float(context.args[0].replace(",", ".")))

        import financeiro
        financeiro.adicionar_valor(
            email="adicao_manual@gmail.com",
            plano="ADICAO MANUAL",
            valor=valor
        )

        total = financeiro.total_faturado()
        clientes_total = len([c for c in financeiro.clientes if c.get("usuario_id", 0) != 0])

        await update.message.reply_text(

            "✅ SALDO POSITIVO ADICIONADO\n\n"

            f"💰 Valor Adicionado: R${valor:.2f}\n\n"

            f"👥 CLIENTES ATIVOS: {clientes_total}\n\n"

            f"💸 TOTAL DO CAIXA:\n"
            f"R${total:.2f}"

        )

    except Exception as e:
        print(f"Erro em addsaldo: {e}")
        await update.message.reply_text(

            "❌ Use corretamente:\n/addsaldo 10"

        )


# =========================================
# LANÇAR DÍVIDA (SALDO NEGATIVO)
# =========================================

async def comando_divida(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != DONO_ID:
        return

    try:
        # Pega o valor e converte obrigatoriamente para NEGATIVO
        valor = -abs(float(context.args[0].replace(",", ".")))

        import financeiro
        financeiro.adicionar_valor(
            email="divida_manual@gmail.com",
            plano="DIVIDA MANUAL",
            valor=valor
        )

        total = financeiro.total_faturado()
        clientes_total = len([c for c in financeiro.clientes if c.get("usuario_id", 0) != 0])

        await update.message.reply_text(

            "⚠️ DÍVIDA LANÇADA (NEGATIVO)\n\n"

            f"💰 Valor da Dívida: R${valor:.2f}\n\n"

            f"👥 CLIENTES ATIVOS: {clientes_total}\n\n"

            f"💸 TOTAL DO CAIXA:\n"
            f"R${total:.2f}"

        )

    except Exception as e:
        print(f"Erro em divida: {e}")
        await update.message.reply_text(

            "❌ Use corretamente:\n/divida 10"

        )


# =========================================
# GRUPO
# =========================================

async def grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensagem = str(update.message.text).lower()

    palavras = [

        "passes",
        "tabela",
        "licença",
        "preço",
        "aluguel",
        "meis",
        "pass",
        "planos",
        "pass",
        "plano",
        "mensalidade",
        "pagamento"

    ]

    if any(p in mensagem for p in palavras):

        teclado = [[
            InlineKeyboardButton(
                "💳 ABRIR PAGAMENTO",
                url=BOT_PRIVADO
            )
        ]]

        reply_markup = InlineKeyboardMarkup(teclado)

        await update.message.reply_text(

            "💰 TABELA DE PLANOS XBOT 💰\n\n"

            "📦 PIX:\n\n"

            "1 MÊS — R$20\n"
            "2 MESES — R$38\n"
            "3 MESES — R$54\n"
            "4 MESES — R$68\n"
            "5 MESES — R$80\n"
            "6 MESES — R$90\n"
            "1 ANO — R$162\n\n"

            "🌍 USDT:\n\n"

            "1 MONTH — 4 USDT\n"
            "2 MONTHS — 7.60 USDT\n"
            "3 MONTHS — 10.80 USDT\n"
            "4 MONTHS — 13.60 USDT\n"
            "5 MONTHS — 16 USDT\n"
            "6 MONTHS — 18 USDT\n"
            "1 YEAR — 32.40 USDT\n\n"

            "👇 ABRIR PAGAMENTO NO PRIVADO 👇",

            reply_markup=reply_markup
        )

# =========================================
# BOTÕES
# =========================================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    usuario_id = query.from_user.id

    if query.data == "pagamento":

        dados = clientes.get(usuario_id)

        if dados and dados.get("ativado") == True:

            await query.answer(
                "PAGAMENTO JÁ UTILIZADO",
                show_alert=True
            )

            return

        teclado = [

            [
                InlineKeyboardButton(
                    "💳 PIX (PT-BR)",
                    callback_data="pix"
                )
            ],

            [
                InlineKeyboardButton(
                    "🌍 USDT / DOLAR (ENGLISH)",
                    callback_data="usdt"
                )
            ],

            [
                InlineKeyboardButton(
                    "❌ CANCELAR / CANCEL",
                    callback_data="cancelar"
                )
            ]

        ]

        reply_markup = InlineKeyboardMarkup(teclado)

        await query.message.reply_text(

            "💰 ESCOLHA A FORMA DE PAGAMENTO / CHOOSE PAYMENT METHOD",

            reply_markup=reply_markup
        )

    elif query.data == "pix":

        dados = clientes.get(usuario_id)

        if dados and dados.get("ativado") == True:

            await query.answer(
                "PAGAMENTO JÁ UTILIZADO",
                show_alert=True
            )

            return

        teclado = [

            [InlineKeyboardButton("1 MÊS — R$20", callback_data="plano_20")],
            [InlineKeyboardButton("2 MESES — R$38", callback_data="plano_38")],
            [InlineKeyboardButton("3 MESES — R$54", callback_data="plano_54")],
            [InlineKeyboardButton("4 MESES — R$68", callback_data="plano_68")],
            [InlineKeyboardButton("5 MESES — R$80", callback_data="plano_80")],
            [InlineKeyboardButton("6 MESES — R$90", callback_data="plano_90")],
            [InlineKeyboardButton("1 ANO — R$162", callback_data="plano_162")]

        ]

        reply_markup = InlineKeyboardMarkup(teclado)

        await query.message.reply_text(
            "💳 ESCOLHA O PLANO PIX",
            reply_markup=reply_markup
        )

    elif query.data == "usdt":

        dados = clientes.get(usuario_id)

        if dados and dados.get("ativado") == True:

            await query.answer(
                "PAYMENT ALREADY USED",
                show_alert=True
            )

            return

        teclado = [

            [InlineKeyboardButton("1 MONTH — 4 USDT", callback_data="usdt_4")],
            [InlineKeyboardButton("2 MONTHS — 7.60 USDT", callback_data="usdt_7.60")],
            [InlineKeyboardButton("3 MONTHS — 10.80 USDT", callback_data="usdt_10.80")],
            [InlineKeyboardButton("4 MONTHS — 13.60 USDT", callback_data="usdt_13.60")],
            [InlineKeyboardButton("5 MONTHS — 16 USDT", callback_data="usdt_16")],
            [InlineKeyboardButton("6 MONTHS — 18 USDT", callback_data="usdt_18")],
            [InlineKeyboardButton("1 YEAR — 32.40 USDT", callback_data="usdt_32.40")]

        ]

        reply_markup = InlineKeyboardMarkup(teclado)

        await query.message.reply_text(
            "🌍 CHOOSE YOUR USDT / DOLLAR PLAN",
            reply_markup=reply_markup
        )

    elif query.data == "cancelar":

        dados = clientes.get(usuario_id)
        is_usdt = dados and dados.get("tipo") == "usdt"

        if usuario_id in status_cliente:
            del status_cliente[usuario_id]

        if usuario_id in clientes:
            del clientes[usuario_id]

        salvar_estado()

        msg_cancel = "❌ PAYMENT CANCELED." if is_usdt else "❌ PAGAMENTO CANCELADO."
        await query.message.reply_text(msg_cancel)

    elif query.data.startswith("plano_"):

        valor = query.data.replace("plano_", "")

        planos = {

            "20": "1 MÊS",
            "38": "2 MESES",
            "54": "3 MESES",
            "68": "4 MESES",
            "80": "5 MESES",
            "90": "6 MESES",
            "162": "1 ANO"

        }

        clientes[usuario_id] = {

            "valor": valor,
            "plano": planos[valor],
            "tipo": "pix",
            "ativado": False

        }

        status_cliente[usuario_id] = "aguardando_comprovante"
        salvar_estado()

        await query.message.reply_text(

            f"💳 PAGAMENTO PIX\n\n"

            f"💰 Valor: R${valor}\n\n"

            "PIX:\n"
            "choplivre@gmail.com\n\n"

            "👤 Natanael S Castro\n\n"

            "📩 Após o pagamento, envie o comprovante em imagem (print). Não envie o comprovante em arquivo."

        )

    elif query.data.startswith("usdt_"):

        valor_usdt = query.data.replace("usdt_", "")

        planos_usdt = {
            "4": "1 MONTH (USDT)",
            "7.60": "2 MONTHS (USDT)",
            "10.80": "3 MONTHS (USDT)",
            "13.60": "4 MONTHS (USDT)",
            "16": "5 MONTHS (USDT)",
            "18": "6 MONTHS (USDT)",
            "32.40": "1 YEAR (USDT)"
        }

        clientes[usuario_id] = {
            "valor": valor_usdt,
            "plano": planos_usdt[valor_usdt],
            "tipo": "usdt",
            "ativado": False
        }

        status_cliente[usuario_id] = "aguardando_comprovante"
        salvar_estado()

        await query.message.reply_text(
            f"🌍 **USDT / DOLLAR PAYMENT** 🌍\n\n"
            f"💰 **Selected Amount:** {valor_usdt} USDT\n\n"
            f"📌 **Binance ID:** `38862841`\n"
            f"📌 **Deposit Address:** `TTHDbaSSGhWvmfQfykqxanYWisbNrMDcBE`\n"
            f"📌 **Network:** Tron (TRC20)\n\n"
            f"📩 After paying, please send the payment confirmation screenshot (image). Do not send documents.",
            parse_mode="Markdown"
        )

    elif query.data == "email":

        dados = clientes.get(usuario_id)
        is_usdt = dados and dados.get("tipo") == "usdt"

        if dados and dados.get("ativado") == True:
            msg_alert = "PAYMENT ALREADY USED" if is_usdt else "PAGAMENTO JÁ UTILIZADO"
            await query.answer(msg_alert, show_alert=True)
            return

        if status_cliente.get(usuario_id) == "aguardando_ativacao":
            msg_alert = "EMAIL ALREADY SENT" if is_usdt else "EMAIL JÁ ENVIADO"
            await query.answer(msg_alert, show_alert=True)
            return

        status_cliente[usuario_id] = "aguardando_email"
        salvar_estado()

        msg_email = "📧 Enter your email address." if is_usdt else "📧 Digite seu email."
        await query.message.reply_text(msg_email)


    elif query.data.startswith("email_errado_"):

        cliente_id = int(
            query.data.replace("email_errado_", "")
        )

        status_cliente[cliente_id] = "aguardando_email"
        salvar_estado()
        
        dados_c = clientes.get(cliente_id)
        if dados_c and dados_c.get("tipo") == "usdt":
            text_errado = (
                "❌ THE SENT EMAIL IS INCORRECT.\n\n"
                "📸 Check the image below to find your correct email:\n\n"
                "https://t.me/x_bot_automatizador/2/29316\n\n"
                "📧 Then send the correct email address again."
            )
        else:
            text_errado = (
                "❌ O EMAIL ENVIADO ESTÁ ERRADO.\n\n"
                "📸 Veja a imagem abaixo para encontrar o email correto:\n\n"
                "https://t.me/x_bot_automatizador/2/29316\n\n"
                "📧 Depois envie o email correto novamente."
            )

        await context.bot.send_message(
            chat_id=cliente_id,
            text=text_errado
        )

        await query.answer(
            "EMAIL DESIGNADO COMO ERRADO",
            show_alert=True
        )

    elif query.data.startswith("ativar_"):

        try:

            cliente_id = int(
                query.data.replace("ativar_", "")
            )

            dados = clientes.get(cliente_id)

            if not dados:

                await query.message.reply_text(
                    "❌ CLIENTE NÃO ENCONTRADO"
                )

                return

            if dados.get("ativado_financeiro") == True:

                await query.answer(
                    "CLIENTE JÁ FOI ATIVADO",
                    show_alert=True
                )

                return

            email = dados.get(
                "email",
                "não informado"
            )

            valor_original = dados["valor"]
            is_usdt = dados.get("tipo") == "usdt"
            
            import financeiro
            
            if is_usdt:
                valor_desconto_real = TABELA_DESCONTO_USDT.get(str(valor_original), 0.00)
                valor_final_financeiro = -valor_desconto_real
            else:
                valor_final_financeiro = float(valor_original) * 0.5

            financeiro.registrar_cliente(

                usuario_id=cliente_id,
                email=email,
                plano=dados["plano"],
                valor=valor_final_financeiro,
                tipo=dados["tipo"]

            )

            clientes[cliente_id]["ativado_financeiro"] = True
            salvar_estado()

            # Confirmação adaptada ao idioma escolhido
            if is_usdt:
                text_sucesso_cliente = (
                    "✅ YOUR ACCOUNT HAS BEEN ACTIVATED.\n\n"
                    "🔥 Your access is now completely free.\n"
                    "🔥 If your bot is currently running, turn it off.\n"
                    "🔥 Then turn it back on to refresh your license."
                )
            else:
                text_sucesso_cliente = (
                    "✅ SUA CONTA FOI ATIVADA.\n\n"
                    "🔥 Seu acesso já está liberado.\n"
                    "🔥 Se o bot estiver ligado desligue.\n"
                    "🔥 Depois ligue para atualizar licença."
                )

            await context.bot.send_message(
                chat_id=cliente_id,
                text=text_sucesso_cliente
            )

            total = financeiro.total_faturado()
            total_clientes = len(financeiro.clientes)

            await context.bot.send_message(

                chat_id=ATIVADOR_ID,

                text=(

                    "✅ CLIENTE ATIVADO\n\n"

                    f"👥 CLIENTES ATIVOS: {total_clientes}\n\n"

                    f"💰 VALOR TOTAL DO CAIXA:\n"
                    f"R${total:.2f}"

                )

            )

            await query.edit_message_text(

                text="✅ CLIENTE ATIVADO COM SUCESSO"

            )

            if cliente_id in status_cliente:
                del status_cliente[cliente_id]

            if cliente_id in clientes:
                del clientes[cliente_id]

            salvar_estado()

        except Exception as erro:

            print("ERRO:", erro)

            await query.message.reply_text(
                f"❌ ERRO:\n{erro}"
            )

# =========================================
# MENSAGENS E VERIFICAÇÃO TOTAL ANTI-FRAUDE (CORRIGIDO)
# =========================================

async def mensagens(update: Update, context: ContextTypes.DEFAULT_TYPE):

    usuario_id = update.effective_chat.id
    status = status_cliente.get(usuario_id)

    if status == "aguardando_comprovante":

        # Se o usuário enviou um documento (arquivo) em vez de imagem/print
        if update.message.document:
            await update.message.reply_text(
                "❌ Envie a imagem, não envie arquivo! Por favor, envie o print do comprovante."
            )
            return

        # Se o usuário enviou texto (ou outra coisa que não seja foto) em vez do print
        if not update.message.photo:
            await update.message.reply_text(
                "Esta é uma área restrita, não tera ninguém para atender. Por favor, envie a imagem ou print do seu comprovante."
            )
            return

        if update.message.photo:

            dados = clientes.get(usuario_id)
            is_usdt = dados and dados.get("tipo") == "usdt"

            msg_rec = "🔍 Receipt received.\n\n⏳ Performing security check. Please wait..." if is_usdt else "🔍 Comprovante recebido.\n\n⏳ Fazendo análise de segurança Aguarde..."
            await update.message.reply_text(msg_rec)

            foto = update.message.photo[-1]
            arquivo = await foto.get_file()
            
            timestamp_nome = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho = f"comprovante_{usuario_id}_{timestamp_nome}.jpg"
            await arquivo.download_to_drive(caminho)

            resultado = leitor.readtext(caminho, detail=0)
            texto_original = " ".join(resultado).lower().strip()

            texto_limpo = (
                texto_original
                .replace(" ", "")
                .replace("/", "")
                .replace("-", "")
                .replace(".", "")
                .replace(",", "")
                .replace("_", "")
            )

            # REGRA 1: VERIFICAÇÃO DE DUPLICIDADE
            recibo_atual = texto_original[:300]

            if recibo_atual in recibos_usados:
                msg_dup = "❌ ERROR: THIS RECEIPT WAS ALREADY USED AND HAS BEEN AUTOMATICALLY DECLINED." if is_usdt else "❌ ERRO: ESTE COMPROVANTE JÁ FOI UTILIZADO EM OUTRO MOMENTO E FOI RECUSADO AUTOMATICAMENTE."
                await update.message.reply_text(msg_dup)
                if os.path.exists(caminho):
                    os.remove(caminho)
                return

            valor = str(dados["valor"])

            # FLUXO SE FOR USDT (Totalmente em Inglês)
            if is_usdt:
                if valor in texto_original or valor.replace(".", ",") in texto_original:
                    recibos_usados.add(recibo_atual)
                    
                    status_cliente[usuario_id] = "aguardando_email"
                    salvar_estado()

                    teclado = [[InlineKeyboardButton("📧 SEND EMAIL", callback_data="email")]]
                    reply_markup = InlineKeyboardMarkup(teclado)
                    
                    await update.message.reply_text(
                        f"✅ {valor} USDT RECEIPT VALIDATED SUCCESSFULY.\n\n📧 Now please submit your email address.",
                        reply_markup=reply_markup
                    )
                else:
                    if os.path.exists(caminho):
                        os.remove(caminho)
                    teclado = [
                        [InlineKeyboardButton("🔄 TRY AGAIN", callback_data="pagamento")],
                        [InlineKeyboardButton("❌ CANCEL", callback_data="cancelar")]
                    ]
                    reply_markup = InlineKeyboardMarkup(teclado)
                    await update.message.reply_text(
                        f"❌ USDT RECEIPT REJECTED.\n\nThe amount of {valor} USDT was not clearly identified in the image.",
                        reply_markup=reply_markup
                    )
                return

            # REGRA 2: VERIFICAÇÃO DO VALOR (Flexibilizada para aceitar o formato padrão do print)
            valor_ok = False
            valores_validos = [
                f"r${valor}", f"r$ {valor}", 
                f"{valor},00", f"{valor}.00", 
                f"{valor},0", f"{valor}.0", 
                f"{valor},", f"{valor}.",
                f"{valor}"
            ]
            for valor_texto in valores_validos:
                if valor_texto in texto_original or valor_texto in texto_limpo:
                    valor_ok = True
                    break

            # REGRA 3: VERIFICAÇÃO DO TITULAR RECEBEDOR (Ajustada para o nome completo / partes isoladas)
            nome_ok = (
                ("natanael" in texto_original and "castro" in texto_original)
                or "natanael" in texto_original
                or "castro" in texto_original
                or "natan" in texto_original
                or "s castro" in texto_original
            )

            # REGRA 4: VALIDAÇÃO DA DATA DE HOJE ABSOLUTA (Com tolerância flexível para formato de barras/traços)
            hoje = datetime.now()
            d = f"{hoje.day:02d}"    
            m = f"{hoje.month:02d}"  
            a = str(hoje.year)        
            a_curto = a[2:]          

            meses_pt = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
            nome_mes = meses_pt[hoje.month - 1]

            padrao_data_1 = f"{d}{m}{a}"        
            padrao_data_2 = f"{d}{m}{a_curto}"  
            padrao_data_3 = f"{d}{nome_mes}"    
            padrao_data_4 = f"{d}{m}"            

            data_hoje_ok = (
                padrao_data_1 in texto_limpo 
                or padrao_data_2 in texto_limpo 
                or padrao_data_3 in texto_limpo
                or padrao_data_4 in texto_limpo
                or f"{d}/{m}/{a}" in texto_original
                or f"{d}-{m}-{a}" in texto_original
            )

            for mes_passado in range(1, hoje.month):
                m_passado_str = f"{mes_passado:02d}"
                if f"{m_passado_str}{a}" in texto_limpo or f"{m_passado_str}{a_curto}" in texto_limpo:
                    data_hoje_ok = False 

            if valor_ok and nome_ok and data_hoje_ok:

                recibos_usados.add(recibo_atual)

                status_cliente[usuario_id] = "aguardando_email"
                salvar_estado()

                teclado = [[
                    InlineKeyboardButton(
                        "📧 ENVIAR EMAIL",
                        callback_data="email"
                    )
                ]]

                reply_markup = InlineKeyboardMarkup(teclado)

                await update.message.reply_text(

                    "✅ COMPROVANTE DO DIA ATUAL VALIDADO COM SUCESSO.\n\n"
                    "📧 Agora envie seu email.",

                    reply_markup=reply_markup
                )

            else:
                if os.path.exists(caminho):
                    os.remove(caminho)

                teclado = [
                    [InlineKeyboardButton("🔄 TENTAR NOVAMENTE", callback_data="pagamento")],
                    [InlineKeyboardButton("💬 FALA COM ATENDENTE", url="https://t.me/nscnatan")]
                ]

                reply_markup = InlineKeyboardMarkup(teclado)

                await update.message.reply_text(

                    "❌ COMPROVANTE RECUSADO (SISTEMA ANTI-FRAUDE).\n\n"
                    "⚠️ Motivos possíveis:\n"
                    "1. A data do comprovante não é de HOJE (comprovantes antigos são bloqueados).\n"
                    "2. O valor do print não bate com o plano escolhido.\n"
                    "3. O nome do recebedor (Natanael) não foi identificado.\n\n"
                    "📩 Se isso for um erro, envie um print nítido ou fale com o suporte @nscnatan",

                    reply_markup=reply_markup
                )

    elif status == "aguardando_email":

        email = str(update.message.text)

        if "@" in email and ".com" in email:

            dados = clientes.get(usuario_id)

            if usuario_id not in clientes:
                clientes[usuario_id] = {}

            clientes[usuario_id]["email"] = email
            status_cliente[usuario_id] = "aguardando_ativacao"
            salvar_estado()

            teclado = [
                [InlineKeyboardButton("✅ ATIVAR CLIENTE", callback_data=f"ativar_{usuario_id}")],
                [InlineKeyboardButton("❌ EMAIL ERRADO", callback_data=f"email_errado_{usuario_id}")]
            ]

            reply_markup = InlineKeyboardMarkup(teclado)

            moeda_exibicao = "USDT" if dados['tipo'] == "usdt" else "R$"
            await context.bot.send_message(

                chat_id=ATIVADOR_ID,

                text=(

                    "📧 NOVO EMAIL\n\n"
                    f"📧 {email}\n\n"
                    f"📦 {dados['plano']}\n\n"
                    f"💰 {moeda_exibicao} {dados['valor']}"

                ),

                reply_markup=reply_markup
            )

            msg_sucesso = "✅ Email received.\n\n⏳ Please wait for manual activation." if dados['tipo'] == "usdt" else "✅ Email recebido.\n\n⏳ Aguarde ativação."
            await update.message.reply_text(msg_sucesso)

# =========================================
# EXCLUIR CLIENTE
# =========================================

async def comando_excluir(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != DONO_ID:
        return

    try:

        email = context.args[0].lower()

        removido = False

        import financeiro
        for cliente in financeiro.clientes[:]:

            if cliente["email"].lower() == email:

                financeiro.clientes.remove(cliente)

                removido = True

        if removido:

            total = financeiro.total_faturado()

            clientes_total = len(financeiro.clientes)

            await update.message.reply_text(

                "❌ CLIENTE REMOVIDO\n\n"

                f"📧 {email}\n\n"

                f"👥 CLIENTES ATIVOS: {clientes_total}\n\n"

                f"💸 VALOR TOTAL:\n"
                f"R${total:.2f}"

            )

        else:

            await update.message.reply_text(
                "❌ CLIENTE NÃO ENCONTRADO."
            )

    except:

        await update.message.reply_text(
            "❌ Use:\n/excluir email@gmail.com"
        )


# =========================================
# APP
# =========================================

print("BOT ONLINE")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", menu))
app.add_handler(CommandHandler("4JAB4515", teste))
app.add_handler(CommandHandler("financeiro", comando_financeiro))
app.add_handler(CommandHandler("clientes", comando_clientes))
app.add_handler(CommandHandler("pagar", comando_pagar))
app.add_handler(CommandHandler("retira", comando_retira))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, grupo))
app.add_handler(CallbackQueryHandler(botoes))
app.add_handler(MessageHandler(filters.PHOTO, mensagens))
app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, mensagens))
app.add_handler(CommandHandler("resetar", comando_resetar))
app.add_handler(CommandHandler("addsaldo", comando_addsaldo))
app.add_handler(CommandHandler("divida", comando_divida))
app.add_handler(CommandHandler("excluir", comando_excluir))

app.run_polling()
