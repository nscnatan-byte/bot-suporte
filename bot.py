import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# =====================================
# SERVIDOR WEB PARA O RENDER NÃO DESLIGAR
# =====================================
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

import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters
)

# =====================================
# TOKEN
# =====================================
TOKEN = "8810903311:AAF5Kwav8KvySPcb0eIrj-2hmagCKAOqYvw"

# =====================================
# IDS
# =====================================
GRUPO_PRINCIPAL = -1002260588784
GRUPO_SUPORTE = -1003985207456

# =====================================
# TOPICO
# =====================================
TOPICO_ID = 19

# =====================================
# CACHE
# =====================================
mensagens_gp_para_sup = {}
mensagens_sup_para_gp = {}

# =====================================
# LISTA DE LINKS PERMITIDOS (DOMÍNIOS / URLS)
# =====================================
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

# =====================================
# MENSAGEM DE BOAS-VINDAS PARA NOVOS MEMBROS
# =====================================
async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return

    if result.chat.id == GRUPO_PRINCIPAL:
        old_status = result.old_chat_member.status
        new_status = result.new_chat_member.status

        if old_status in ["left", "banned"] and new_status in ["member", "restricted"]:
            user = result.new_chat_member.user
            nome = user.first_name

            texto_boas_vindas = (
                f"🔥 Seja muito bem-vindo(a), {nome}!\n\n"
                "🚀 Este é o grupo oficial do XBOT.\n"
                "• Leia as regras fixadas.\n"
                "• Evite enviar links não autorizados.\n"
                "• Para dúvidas ou suporte, utilize os canais oficiais."
            )

            await context.bot.send_message(
                chat_id=GRUPO_PRINCIPAL,
                text=texto_boas_vindas,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤖 SUPORTE / PRIVADO", url="https://t.me/suporte_xbotbot")]])
            )

# =====================================
# FUNÇÃO PRINCIPAL DE MENSAGENS
# =====================================
async def mensagens_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        if (
            update.effective_user
            and update.effective_user.is_bot
        ):
            return

        mensagem = (
            update.message
            or update.edited_message
        )

        if not mensagem:
            return

        chat_id = update.effective_chat.id
        enviada = None

        if chat_id == GRUPO_PRINCIPAL:

            texto_verificacao = mensagem.text or mensagem.caption or ""
            if "http://" in texto_verificacao or "https://" in texto_verificacao or "t.me/" in texto_verificacao:
                
                contem_link_nao_permitido = False
                urls_encontradas = re.findall(r'(https?://[^\s]+|t\.me/[^\s]+)', texto_verificacao)
                
                for url in urls_encontradas:
                    url_limpa = url.replace("https://", "").replace("http://", "").lower()
                    
                    permitido = False
                    for link_ok in LINKS_PERMITIDOS:
                        if link_ok.lower() in url_limpa:
                            permitido = True
                            break
                    
                    if not permitido:
                        contem_link_nao_permitido = True
                        break

                if contem_link_nao_permitido:
                    await context.bot.delete_message(
                        chat_id=GRUPO_PRINCIPAL,
                        message_id=mensagem.message_id
                    )
                    
                    usuario_nome = update.effective_user.first_name if update.effective_user else "Usuário"
                    await context.bot.send_message(
                        chat_id=GRUPO_PRINCIPAL,
                        text=f"{usuario_nome}, o envio de links não autorizados não é permitido neste grupo!"
                    )
                    print("LINK NÃO AUTORIZADO BLOQUEADO NO GRUPO PRINCIPAL")
                    return

            usuario = (
                update.effective_user.first_name
            )

            msg_original = (
                mensagem.message_id
            )

            if update.edited_message:
                if (
                    msg_original
                    not in mensagens_gp_para_sup
                ):
                    return

                destino_id = (
                    mensagens_gp_para_sup[
                        msg_original
                    ]
                )

                texto = (
                    mensagem.text
                    or ""
                )

                await context.bot.edit_message_text(
                    chat_id=GRUPO_SUPORTE,
                    message_id=destino_id,
                    text=texto
                )

                print("EDITADO GP")
                return

            if mensagem.photo:
                foto = mensagem.photo[-1].file_id
                legenda = mensagem.caption or ""
                enviada = await context.bot.send_photo(
                    chat_id=GRUPO_SUPORTE,
                    photo=foto,
                    caption=f"👤 {usuario}\n\n{legenda}"
                )

            elif mensagem.video:
                video = mensagem.video.file_id
                legenda = mensagem.caption or ""
                enviada = await context.bot.send_video(
                    chat_id=GRUPO_SUPORTE,
                    video=video,
                    caption=f"👤 {usuario}\n\n{legenda}"
                )

            elif mensagem.voice:
                voice = mensagem.voice.file_id
                enviada = await context.bot.send_voice(
                    chat_id=GRUPO_SUPORTE,
                    voice=voice,
                    caption=f"👤 {usuario}"
                )

            elif mensagem.audio:
                audio_id = mensagem.audio.file_id
                legenda = mensagem.caption or ""
                enviada = await context.bot.send_audio(
                    chat_id=GRUPO_SUPORTE,
                    audio=audio_id,
                    caption=f"👤 {usuario}\n\n{legenda}"
                )

            elif mensagem.document:
                document_id = mensagem.document.file_id
                legenda = mensagem.caption or ""
                enviada = await context.bot.send_document(
                    chat_id=GRUPO_SUPORTE,
                    document=document_id,
                    caption=f"👤 {usuario}\n\n{legenda}"
                )

            elif mensagem.text:
                texto = mensagem.text or ""
                enviada = await context.bot.send_message(
                    chat_id=GRUPO_SUPORTE,
                    text=f"👤 {usuario}\n\n{texto}"
                )

            if enviada:
                mensagens_gp_para_sup[msg_original] = enviada.message_id
                mensagens_sup_para_gp[enviada.message_id] = msg_original

            print("CLIENTE -> SUPORTE")

        elif chat_id == GRUPO_SUPORTE:
            msg_original = mensagem.message_id

            if (
                mensagem.text
                and mensagem.text == "/excluir"
            ):
                if not mensagem.reply_to_message:
                    return

                reply_id = mensagem.reply_to_message.message_id
                if reply_id not in mensagens_sup_para_gp:
                    return

                destino_id = mensagens_sup_para_gp[reply_id]
                await context.bot.delete_message(
                    chat_id=GRUPO_PRINCIPAL,
                    message_id=destino_id
                )
                print("MENSAGEM EXCLUIDA")
                return

            if update.edited_message:
                if msg_original not in mensagens_sup_para_gp:
                    return

                destino_id = mensagens_sup_para_gp[msg_original]
                texto = mensagem.text or ""
                await context.bot.edit_message_text(
                    chat_id=GRUPO_PRINCIPAL,
                    message_id=destino_id,
                    text=texto
                )
                print("EDITADO SUPORTE")
                return

            if mensagem.photo:
                foto = mensagem.photo[-1].file_id
                legenda = mensagem.caption or ""
                enviada = await context.bot.send_photo(
                    chat_id=GRUPO_PRINCIPAL,
                    photo=foto,
                    caption=legenda,
                    message_thread_id=TOPICO_ID
                )

            elif mensagem.video:
                video = mensagem.video.file_id
                legenda = mensagem.caption or ""
                enviada = await context.bot.send_video(
                    chat_id=GRUPO_PRINCIPAL,
                    video=video,
                    caption=legenda,
                    message_thread_id=TOPICO_ID
                )

            elif mensagem.voice:
                voice = mensagem.voice.file_id
                enviada = await context.bot.send_voice(
                    chat_id=GRUPO_PRINCIPAL,
                    voice=voice,
                    message_thread_id=TOPICO_ID
                )

            elif mensagem.audio:
                audio_id = mensagem.audio.file_id
                legenda = mensagem.caption or ""
                enviada = await context.bot.send_audio(
                    chat_id=GRUPO_PRINCIPAL,
                    audio=audio_id,
                    caption=legenda,
                    message_thread_id=TOPICO_ID
                )

            elif mensagem.document:
                document_id = mensagem.document.file_id
                legenda = mensagem.caption or ""
                enviada = await context.bot.send_document(
                    chat_id=GRUPO_PRINCIPAL,
                    document=document_id,
                    caption=legenda,
                    message_thread_id=TOPICO_ID
                )

            elif mensagem.text:
                texto = mensagem.text or ""
                enviada = await context.bot.send_message(
                    chat_id=GRUPO_PRINCIPAL,
                    text=texto,
                    message_thread_id=TOPICO_ID
                )

            if enviada:
                mensagens_sup_para_gp[msg_original] = enviada.message_id
                mensagens_gp_para_sup[enviada.message_id] = msg_original

            print("SUPORTE -> CLIENTE")

    except Exception as erro:
        print("================================")
        print("ERRO:")
        print(erro)
        print("================================")

# =====================================
# ONLINE
# =====================================
print("================================")
print("BOT ONLINE")
print("================================")

# =====================================
# APP
# =====================================
app = Application.builder().token(TOKEN).build()

app.add_handler(ChatMemberHandler(boas_vindas, ChatMemberHandler.CHAT_MEMBER))

app.add_handler(
    MessageHandler(
        filters.ALL,
        mensagens_handler
    )
)

# =====================================
# START
# =====================================
app.run_polling()
