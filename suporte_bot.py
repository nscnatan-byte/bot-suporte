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
import json
import os

TOKEN = "8977968510:AAH5gCJ8UeS6-DbfwN-AlTFxqbHDUQXxUjc"
ATIVADOR_ID = 674527541
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

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [[
        InlineKeyboardButton("💳 PROSEGUIR COM PAGAMENTO", callback_data="pagamento")
    ]]
    reply_markup = InlineKeyboardMarkup(teclado)
    await update.message.reply_text("🔥 BEM VINDO 🔥\n\nClique abaixo para continuar.", reply_markup=reply_markup)

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    usuario_id = query.from_user.id
    user_name = query.from_user.first_name or "Cliente"

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

    elif query.data.startswith("plano_"):
        valor = query.data.replace("plano_", "")
        planos = {
            "20": "1 MÊS", "38": "2 MESES", "54": "3 MESES", 
            "68": "4 MESES", "80": "5 MESES", "90": "6 MESES", "162": "1 ANO"
        }

        try:
            import financeiro
            order_id, codigo_pix = financeiro.gerar_pix_pagbank(valor, user_name)

            if not codigo_pix:
                await query.message.reply_text("❌ PagBank retornou vazio. Verifique o token no arquivo financeiro.py")
                return

            clientes[usuario_id] = {
                "valor": valor,
                "plano": planos[valor],
                "tipo": "pix",
                "order_id": order_id,
                "ativado": False
            }
            status_cliente[usuario_id] = "aguardando_pagamento_api"
            salvar_estado()

            teclado_verificacao = [[
                InlineKeyboardButton("🔄 JÁ PAGUEI / VERIFICAR", callback_data="verificar_pagamento")
            ]]
            reply_markup = InlineKeyboardMarkup(teclado_verificacao)

            await query.message.reply_text(
                f"💳 **COBRANÇA PIX PAGBANK GERADA**\n\n"
                f"💰 **Valor:** R${valor}\n\n"
                f"🔗 **Pix Copia e Cola:**\n`{codigo_pix}`",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except Exception as e:
            await query.message.reply_text(f"❌ ERRO TÉCNICO NO PAGBANK:\n{str(e)}")

print("BOT ONLINE COM API PAGBANK")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", menu))
app.add_handler(CallbackQueryHandler(botoes))
app.run_polling()
