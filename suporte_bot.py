import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import requests

# Servidor HTTP falso para manter o Render acordado na porta 10000
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

# =========================================
# TOKEN E CONFIGURAÇÕES
# =========================================

TOKEN = "8977968510:AAH5gCJ8UeS6-DbfwN-AlTFxqbHDUQXxUjc"
TOKEN_PAGBANK = "d831a01d-d2cf-4b6d-b0cc-5aa4dbd5b063b5b705694a92bd8c81a7f9896db7a74d3647-f8f9-425e-a622-c35a5557685b"

ATIVADOR_ID = 929855491
DONO_ID = 674527541
BOT_PRIVADO = "https://t.me/suporte_xbotbot"

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
clientes = {int(k): v for k, v in clientes.items()}
status_cliente = {int(k): v for k, v in status_cliente.items()}

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
# INTEGRAÇÃO PAGBANK API (PIX AUTOMÁTICO)
# =========================================
def gerar_pix_pagbank(valor_reais):
    url = "https://api.pagseguro.com/orders"
    headers = {
        "Authorization": f"Bearer {TOKEN_PAGBANK}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    valor_centavos = int(float(valor_reais) * 100)
    
    payload = {
        "reference_id": f"pedido_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "customer": {
            "email": "cliente@xbot.com",
            "name": "Cliente XBot",
            "tax_id": "00000000000"
        },
        "items": [
            {
                "name": "Assinatura XBot",
                "quantity": 1,
                "unit_amount": valor_centavos
            }
        ],
        "qr_codes": [
            {
                "amount": {
                    "value": valor_centavos
                },
                "expiration_date": "2026-12-31T23:59:59-03:00"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            dados_resposta = response.json()
            for qr in dados_resposta.get("qr_codes", []):
                qr_text = qr.get("text")
                return {"sucesso": True, "copia_e_cola": qr_text}
        return {"sucesso": False, "erro": response.text}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

# =========================================
# HANDLERS DO BOT
# =========================================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [[InlineKeyboardButton("💳 PROSEGUIR COM PAGAMENTO", callback_data="pagamento")]]
    reply_markup = InlineKeyboardMarkup(teclado)
    await update.message.reply_text("🔥 BEM VINDO 🔥\n\nClique abaixo para continuar.", reply_markup=reply_markup)

async def teste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_chat.id
    if usuario_id not in clientes:
        clientes[usuario_id] = {"valor": "20", "plano": "TESTE", "tipo": "pix"}
    status_cliente[usuario_id] = "aguardando_email"
    salvar_estado()
    await update.message.reply_text("✅ TESTE LIBERADO.\n\n📧 Agora envie seu email para ativação.")

async def comando_financeiro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in [DONO_ID, ATIVADOR_ID]:
        return
    import financeiro
    await update.message.reply_text(financeiro.painel())

async def comando_clientes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in [DONO_ID, ATIVADOR_ID]:
        return
    import financeiro
    await update.message.reply_text(financeiro.listar_clientes())

async def comando_pagar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != DONO_ID:
        return
    try:
        valor = context.args[0]
        import financeiro
        financeiro.pagar_ativador(valor)
        total = financeiro.total_faturado()
        clientes_total = len(financeiro.clientes)
        await update.message.reply_text(f"💰 FINANCEIRO XBOT 💰\n\n👥 CLIENTES ATIVOS: {clientes_total}\n\n💸 VALOR TOTAL:\nR${total:.2f}")
    except:
        await update.message.reply_text("❌ Use:\n/pagar 100")

async def comando_retira(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != DONO_ID:
        return
    try:
        valor = float(context.args[0])
        import financeiro
        financeiro.clientes.append({"usuario_id": 0, "email": "retirada@gmail.com", "plano": "RETIRADA", "valor": 0, "historico": -valor, "tipo": "manual"})
        financeiro.salvar()
        total = financeiro.total_faturado()
        clientes_total = len(financeiro.clientes)
        await update.message.reply_text(f"💸 RETIRADA REALIZADA\n\n👥 CLIENTES ATIVOS: {clientes_total}\n\n💸 VALOR TOTAL:\nR${total:.2f}")
    except:
        await update.message.reply_text("❌ Use:\n/retira 10")

async def comando_resetar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != DONO_ID:
        return
    clientes.clear()
    status_cliente.clear()
    salvar_estado()
    import financeiro
    financeiro.clientes.clear()
    if hasattr(financeiro, 'salvar'):
        financeiro.salvar()
    await update.message.reply_text("✅ **FINANCEIRO RESETADO COM SUCESSO!**")

async def comando_addsaldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != DONO_ID:
        return
    try:
        valor = abs(float(context.args[0].replace(",", ".")))
        import financeiro
        financeiro.adicionar_valor(email="adicao_manual@gmail.com", plano="ADICAO MANUAL", valor=valor)
        total = financeiro.total_faturado()
        await update.message.reply_text(f"✅ SALDO POSITIVO ADICIONADO: R${valor:.2f}\nTOTAL: R${total:.2f}")
    except:
        await update.message.reply_text("❌ Use:\n/addsaldo 10")

async def comando_divida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != DONO_ID:
        return
    try:
        valor = -abs(float(context.args[0].replace(",", ".")))
        import financeiro
        financeiro.adicionar_valor(email="divida_manual@gmail.com", plano="DIVIDA MANUAL", valor=valor)
        total = financeiro.total_faturado()
        await update.message.reply_text(f"⚠️ DÍVIDA LANÇADA: R${valor:.2f}\nTOTAL: R${total:.2f}")
    except:
        await update.message.reply_text("❌ Use:\n/divida 10")

async def grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = str(update.message.text).lower()
    palavras = ["passes", "tabela", "licença", "preço", "aluguel", "planos", "plano", "mensalidade", "pagamento"]
    if any(p in mensagem for p in palavras):
        teclado = [[InlineKeyboardButton("💳 ABRIR PAGAMENTO", url=BOT_PRIVADO)]]
        reply_markup = InlineKeyboardMarkup(teclado)
        await update.message.reply_text("💰 TABELA DE PLANOS XBOT 💰\n\n👇 ABRIR PAGAMENTO NO PRIVADO 👇", reply_markup=reply_markup)

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    usuario_id = query.from_user.id

    if query.data == "pagamento":
        teclado = [
            [InlineKeyboardButton("💳 PIX (PT-BR)", callback_data="pix")],
            [InlineKeyboardButton("🌍 USDT / DOLAR (ENGLISH)", callback_data="usdt")],
            [InlineKeyboardButton("❌ CANCELAR / CANCEL", callback_data="cancelar")]
        ]
        reply_markup = InlineKeyboardMarkup(teclado)
        await query.message.reply_text("💰 ESCOLHA A FORMA DE PAGAMENTO", reply_markup=reply_markup)

    elif query.data == "pix":
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
        await query.message.reply_text("💳 ESCOLHA O PLANO PIX", reply_markup=reply_markup)

    elif query.data == "usdt":
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
        await query.message.reply_text("🌍 CHOOSE YOUR USDT PLAN", reply_markup=reply_markup)

    elif query.data == "cancelar":
        if usuario_id in status_cliente: del status_cliente[usuario_id]
        if usuario_id in clientes: del clientes[usuario_id]
        salvar_estado()
        await query.message.reply_text("❌ PAGAMENTO CANCELADO.")

    elif query.data.startswith("plano_"):
        valor = query.data.replace("plano_", "")
        planos = {"20": "1 MÊS", "38": "2 MESES", "54": "3 MESES", "68": "4 MESES", "80": "5 MESES", "90": "6 MESES", "162": "1 ANO"}
        
        await query.message.reply_text("⏳ Gerando Pix automático na API do PagBank...")
        
        # Gera o Pix imediatamente ao clicar no plano
        resultado = gerar_pix_pagbank(valor)
        
        if resultado["sucesso"]:
            clientes[usuario_id] = {"valor": valor, "plano": planos[valor], "tipo": "pix", "ativado": False}
            status_cliente[usuario_id] = "aguardando_email_pos_pagamento"
            salvar_estado()
            
            copia_e_cola = resultado["copia_e_cola"]
            await query.message.reply_text(
                f"💳 **PIX GERADO COM SUCESSO!**\n\n"
                f"📦 Plano: {planos[valor]} (R$ {valor})\n\n"
                f"Copie o código Pix abaixo e realize o pagamento:\n\n"
                f"`{copia_e_cola}`\n\n"
                f"✅ **Após o pagamento realizado**, envie o seu **e-mail** aqui no chat para liberar o acesso:",
                parse_mode="Markdown"
            )
        else:
            await query.message.reply_text(f"❌ Erro ao gerar Pix na API: {resultado['erro']}")

    elif query.data.startswith("usdt_"):
        valor_usdt = query.data.replace("usdt_", "")
        planos_usdt = {"4": "1 MONTH (USDT)", "7.60": "2 MONTHS (USDT)", "10.80": "3 MONTHS (USDT)", "13.60": "4 MONTHS (USDT)", "16": "5 MONTHS (USDT)", "18": "6 MONTHS (USDT)", "32.40": "1 YEAR (USDT)"}
        clientes[usuario_id] = {"valor": valor_usdt, "plano": planos_usdt[valor_usdt], "tipo": "usdt", "ativado": False}
        status_cliente[usuario_id] = "aguardando_email_pos_pagamento"
        salvar_estado()
        await query.message.reply_text(f"🌍 **USDT PAYMENT**\n\n💰 Amount: {valor_usdt} USDT\n📌 Binance ID: `38862841`\n📌 Address: `TTHDbaSSGhWvmfQfykqxanYWisbNrMDcBE`\n\n📧 After paying, please send your email address below:", parse_mode="Markdown")

    elif query.data.startswith("ativar_"):
        try:
            cliente_id = int(query.data.replace("ativar_", ""))
            dados = clientes.get(cliente_id)
            if not dados:
                await query.message.reply_text("❌ CLIENTE NÃO ENCONTRADO")
                return

            email = dados.get("email", "não informado")
            valor_original = dados["valor"]
            is_usdt = dados.get("tipo") == "usdt"

            import financeiro
            if is_usdt:
                valor_final_financeiro = -TABELA_DESCONTO_USDT.get(str(valor_original), 0.00)
            else:
                valor_final_financeiro = float(valor_original) * 0.5

            financeiro.registrar_cliente(cliente_id, email, dados["plano"], valor_final_financeiro, dados["tipo"])

            await context.bot.send_message(chat_id=cliente_id, text="✅ SUA CONTA FOI ATIVADA COM SUCESSO!")
            total = financeiro.total_faturado()
            
            await context.bot.send_message(
                chat_id=ATIVADOR_ID,
                text=f"✅ CLIENTE ATIVADO\n👥 CLIENTES ATIVOS: {len(financeiro.clientes)}\n💰 TOTAL: R${total:.2f}"
            )
            await query.edit_message_text(text="✅ CLIENTE ATIVADO COM SUCESSO")
            
            if cliente_id in status_cliente: del status_cliente[cliente_id]
            if cliente_id in clientes: del clientes[cliente_id]
            salvar_estado()
        except Exception as erro:
            await query.message.reply_text(f"❌ ERRO:\n{erro}")

async def mensagens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_chat.id
    status = status_cliente.get(usuario_id)

    if status == "aguardando_email_pos_pagamento":
        email = str(update.message.text).strip()
        if "@" in email and ".com" in email:
            dados = clientes.get(usuario_id, {})
            clientes[usuario_id]["email"] = email
            status_cliente[usuario_id] = "aguardando_ativacao"
            salvar_estado()

            teclado = [
                [InlineKeyboardButton("✅ ATIVAR CLIENTE", callback_data=f"ativar_{usuario_id}")],
                [InlineKeyboardButton("❌ EMAIL ERRADO", callback_data=f"email_errado_{usuario_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(teclado)

            moeda = "USDT" if dados.get('tipo') == "usdt" else "R$"
            await context.bot.send_message(
                chat_id=ATIVADOR_ID,
                text=f"💳 **PAGAMENTO REALIZADO / NOVO E-MAIL**\n\n📧 {email}\n\n📦 {dados.get('plano')}\n\n💰 {moeda} {dados.get('valor')}",
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ E-mail recebido com sucesso!\n\n⏳ O ativador já foi avisado e vai liberar sua conta em instantes.")

async def comando_excluir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != DONO_ID:
        return
    try:
        email = context.args[0].lower()
        import financeiro
        removido = False
        for c in financeiro.clientes[:]:
            if c["email"].lower() == email:
                financeiro.clientes.remove(c)
                removido = True
        if removido:
            financeiro.salvar()
            await update.message.reply_text(f"❌ CLIENTE REMOVIDO: {email}")
        else:
            await update.message.reply_text("❌ CLIENTE NÃO ENCONTRADO.")
    except:
        await update.message.reply_text("❌ Use:\n/excluir email@gmail.com")

def main():
    print("BOT ONLINE COM PIX AUTOMÁTICO ANTES DO EMAIL")
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True")
    except:
        pass

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

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
