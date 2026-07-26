import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

def run_fake_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bots are alive!")
        def log_message(self, format, *args):
            return

    server = HTTPServer(("0.0.0.0", 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

import json
import os
import time
import re
from datetime import datetime

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
# TOKENS E IDS
# =========================================
TOKEN_PAGAMENTO = "8977968510:AAEbZAKEeeBbxRsK50eMT1kStaHN9-_j5f4"

GRUPO_PRINCIPAL = -1002260588784
GRUPO_SUPORTE = -1003985207456
TOPICO_ID = 19
ATIVADOR_ID = 674527541
DONO_ID = 674527541
BOT_PRIVADO = "https://t.me/suporte_xbotbot"

ARQUIVO_ESTADO = "dados_clientes.json"
ARQUIVO_BLOQUEIOS = "bloqueio_usuarios.json"

mensagens_gp_para_sup = {}
mensagens_sup_para_gp = {}

LINKS_PERMITIDOS = [
    "youtube.com/watch?v=Q3-YBHNE254",
    "t.me/x_bot_automatizador/2/33481",
    "t.me/x_bot_automatizador/7/33320",
    "t.me/x_bot_automatizador/19",
    "t.me/x_bot_automatizador/23232",
    "youtube.com/watch?v=jt9XkiC1Dbo",
    "youtu.be/cJuT4MX7UtM",
    "sio.tools/signal-converter",
    "t.me/biblioteca_indicador",
    "t.me/suporte_xbotbot",
    "xbot.net.br"
]

def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        try:
            with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados.get("clientes", {}), dados.get("status_cliente", {})
        except:
            pass
    return {}, {}

def salvar_estado():
    try:
        with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
            json.dump({"clientes": clientes, "status_cliente": status_cliente}, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_bloqueios():
    if os.path.exists(ARQUIVO_BLOQUEIOS):
        try:
            with open(ARQUIVO_BLOQUEIOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_bloqueios():
    try:
        with open(ARQUIVO_BLOQUEIOS, "w", encoding="utf-8") as f:
            json.dump(bloqueios_usuarios, f, ensure_ascii=False, indent=4)
    except:
        pass

clientes, status_cliente = carregar_estado()
clientes = {int(k): v for k, v in clientes.items()}
status_cliente = {int(k): v for k, v in status_cliente.items()}
bloqueios_usuarios = {int(k): v for k, v in carregar_bloqueios().items()}

TABELA_DESCONTO_USDT = {
    "4": 10.00, "7.60": 19.00, "10.80": 27.00,
    "13.60": 34.00, "16": 40.00, "18": 45.00, "32.40": 81.00
}

# =========================================
# FUNÇÕES DE PAGAMENTO E MENU
# =========================================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_chat.id
    if usuario_id != DONO_ID and usuario_id in bloqueios_usuarios:
        if (time.time() - bloqueios_usuarios[usuario_id]) < (20 * 24 * 60 * 60):
            await update.message.reply_text("⚠️ **COMPRA BLOQUEADA**\n\nVocê já possui uma licença ativa recente. Fale com o suporte @nscnatan")
            return
    await update.message.reply_text("🔥 BEM VINDO 🔥\n\nClique abaixo para continuar.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 PROSEGUIR COM PAGAMENTO", callback_data="pagamento")]]))

async def teste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_chat.id
    clientes[usuario_id] = {"valor": "0", "plano": "TESTE", "tipo": "pix"}
    status_cliente[usuario_id] = "aguardando_email"
    salvar_estado()
    await update.message.reply_text("✅ PAGAMENTO LIBERADO.\n\n📧 Agora envie seu email.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📧 ENVIAR EMAIL", callback_data="email")]]))

# =========================================
# MANUTENÇÃO DE MENSAGENS E SUPORTE
# =========================================
async def mensagens_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user and update.effective_user.is_bot:
            return
        mensagem = update.message or update.edited_message
        if not mensagem:
            return
        chat_id = update.effective_chat.id
        enviada = None

        if chat_id == GRUPO_PRINCIPAL:
            texto_verificacao = mensagem.text or mensagem.caption or ""
            if any(p in texto_verificacao.lower() for p in ["passes", "tabela", "licença", "preço", "aluguel", "meis", "pass", "planos", "plano", "mensalidade", "pagamento"]):
                await mensagem.reply_text("💰 TABELA DE PLANOS XBOT 💰\n\nAbra o privado para comprar 👇", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 ABRIR PAGAMENTO", url=BOT_PRIVADO)]]))
                return

            if "http://" in texto_verificacao or "https://" in texto_verificacao or "t.me/" in texto_verificacao:
                urls = re.findall(r'(https?://[^\s]+|t\.me/[^\s]+)', texto_verificacao)
                nao_permitido = any(not any(ok.lower() in u.replace("https://", "").replace("http://", "").lower() for ok in LINKS_PERMITIDOS) for u in urls)
                if nao_permitido:
                    await context.bot.delete_message(chat_id=GRUPO_PRINCIPAL, message_id=mensagem.message_id)
                    await context.bot.send_message(chat_id=GRUPO_PRINCIPAL, text=f"{update.effective_user.first_name}, links não autorizados não são permitidos!")
                    return

            usuario = update.effective_user.first_name
            msg_original = mensagem.message_id

            if mensagem.photo:
                enviada = await context.bot.send_photo(chat_id=GRUPO_SUPORTE, photo=mensagem.photo[-1].file_id, caption=f"👤 {usuario}\n\n{mensagem.caption or ''}")
            elif mensagem.video:
                enviada = await context.bot.send_video(chat_id=GRUPO_SUPORTE, video=mensagem.video.file_id, caption=f"👤 {usuario}\n\n{mensagem.caption or ''}")
            elif mensagem.voice:
                enviada = await context.bot.send_voice(chat_id=GRUPO_SUPORTE, voice=mensagem.voice.file_id, caption=f"👤 {usuario}")
            elif mensagem.document:
                enviada = await context.bot.send_document(chat_id=GRUPO_SUPORTE, document=mensagem.document.file_id, caption=f"👤 {usuario}\n\n{mensagem.caption or ''}")
            elif mensagem.text:
                enviada = await context.bot.send_message(chat_id=GRUPO_SUPORTE, text=f"👤 {usuario}\n\n{mensagem.text}")

            if enviada:
                mensagens_gp_para_sup[msg_original] = enviada.message_id
                mensagens_sup_para_gp[enviada.message_id] = msg_original

        elif chat_id == GRUPO_SUPORTE:
            msg_original = mensagem.message_id
            if mensagem.text and mensagem.text == "/excluir" and mensagem.reply_to_message:
                reply_id = mensagem.reply_to_message.message_id
                if reply_id in mensagens_sup_para_gp:
                    await context.bot.delete_message(chat_id=GRUPO_PRINCIPAL, message_id=mensagens_sup_para_gp[reply_id])
                return

            if mensagem.photo:
                enviada = await context.bot.send_photo(chat_id=GRUPO_PRINCIPAL, photo=mensagem.photo[-1].file_id, caption=mensagem.caption or "", message_thread_id=TOPICO_ID)
            elif mensagem.video:
                enviada = await context.bot.send_video(chat_id=GRUPO_PRINCIPAL, video=mensagem.video.file_id, caption=mensagem.caption or "", message_thread_id=TOPICO_ID)
            elif mensagem.voice:
                enviada = await context.bot.send_voice(chat_id=GRUPO_PRINCIPAL, voice=mensagem.voice.file_id, message_thread_id=TOPICO_ID)
            elif mensagem.document:
                enviada = await context.bot.send_document(chat_id=GRUPO_PRINCIPAL, document=mensagem.document.file_id, caption=mensagem.caption or "", message_thread_id=TOPICO_ID)
            elif mensagem.text:
                enviada = await context.bot.send_message(chat_id=GRUPO_PRINCIPAL, text=mensagem.text, message_thread_id=TOPICO_ID)

            if enviada:
                mensagens_sup_para_gp[msg_original] = enviada.message_id
                mensagens_gp_para_sup[enviada.message_id] = msg_original
    except Exception as e:
        print("Erro:", e)

# =========================================
# BOTÕES E CALLBACKS DE PAGAMENTO
# =========================================
async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    usuario_id = query.from_user.id

    if query.data == "pagamento":
        await query.message.reply_text("💰 ESCOLHA A FORMA DE PAGAMENTO", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 PIX", callback_data="pix")], [InlineKeyboardButton("🌍 USDT", callback_data="usdt")], [InlineKeyboardButton("❌ CANCELAR", callback_data="cancelar")]]))
    elif query.data == "pix":
        await query.message.reply_text("💳 ESCOLHA O PLANO PIX", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("1 MÊS — R$20", callback_data="plano_20")], [InlineKeyboardButton("1 ANO — R$162", callback_data="plano_162")]]))
    elif query.data == "usdt":
        await query.message.reply_text("🌍 CHOOSE USDT PLAN", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("1 MONTH — 4 USDT", callback_data="usdt_4")], [InlineKeyboardButton("1 YEAR — 32.40 USDT", callback_data="usdt_32.40")]]))
    elif query.data == "cancelar":
        clientes.pop(usuario_id, None)
        status_cliente.pop(usuario_id, None)
        salvar_estado()
        await query.message.reply_text("❌ CANCELADO.")
    elif query.data.startswith("plano_"):
        v = query.data.replace("plano_", "")
        clientes[usuario_id] = {"valor": v, "plano": f"{v} Reais", "tipo": "pix", "ativado": False}
        status_cliente[usuario_id] = "aguardando_comprovante"
        salvar_estado()
        await query.message.reply_text(f"💳 PIX R${v}\nChave: choplivre@gmail.com\nEnvie o print do comprovante.")
    elif query.data.startswith("usdt_"):
        v = query.data.replace("usdt_", "")
        clientes[usuario_id] = {"valor": v, "plano": f"{v} USDT", "tipo": "usdt", "ativado": False}
        status_cliente[usuario_id] = "aguardando_comprovante"
        salvar_estado()
        await query.message.reply_text(f"🌍 USDT {v}\nBinance ID: 38862841\nEnvie o print do comprovante.")
    elif query.data == "email":
        status_cliente[usuario_id] = "aguardando_email"
        salvar_estado()
        await query.message.reply_text("📧 Digite seu email:")
    elif query.data.startswith("ativar_"):
        cid = int(query.data.replace("ativar_", ""))
        d = clientes.get(cid, {})
        bloqueios_usuarios[cid] = time.time()
        salvar_bloqueios()
        await context.bot.send_message(chat_id=cid, text="✅ SUA CONTA FOI ATIVADA!")
        await query.edit_message_text("✅ ATIVADO COM SUCESSO")
        clientes.pop(cid, None)
        status_cliente.pop(cid, None)
        salvar_estado()

# =========================================
# CONFIGURAÇÃO DO APP
# =========================================
print("BOT ONLINE")
app = Application.builder().token(TOKEN_PAGAMENTO).build()

app.add_handler(CommandHandler("start", menu))
app.add_handler(CommandHandler("4JAB4515", teste))
app.add_handler(CallbackQueryHandler(botoes))
app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, mensagens_handler))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, mensagens_handler))
app.add_handler(MessageHandler(filters.ALL & ~filters.ChatType.PRIVATE, mensagens_handler))

app.run_polling()
