from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

# =====================================
# TOKEN
# =====================================

TOKEN = "8810903311:AAGBzMaAxzywD19Ol3RaeGWd5PVwhfAyqO8"

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
# FUNÇÃO PRINCIPAL
# =====================================

async def mensagens_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        # IGNORA BOT
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

        # =====================================
        # CLIENTE -> SUPORTE
        # =====================================

        if chat_id == GRUPO_PRINCIPAL:

            # Verifica se quem enviou a mensagem é Administrador ou Criador do grupo
            eh_admin = False
            if update.effective_chat and update.effective_user:
                try:
                    membro = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
                    if membro.status in ["administrator", "creator"]:
                        eh_admin = True
                except Exception:
                    pass

            # =====================================
            # BLOQUEIO DE LINK (GRUPO PRINCIPAL) - SÓ APLICA PARA CLIENTES/VISITANTES
            # =====================================
            if not eh_admin:
                texto_verificacao = mensagem.text or mensagem.caption or ""
                if "http://" in texto_verificacao or "https://" in texto_verificacao or "t.me/" in texto_verificacao:
                    
                    # Verifica se a mensagem contém APENAS os links permitidos ou se não contém links restritos
                    contem_link_nao_permitido = False
                    
                    # Procura por links na mensagem
                    import re
                    urls_encontradas = re.findall(r'(https?://[^\s]+|t\.me/[^\s]+)', texto_verificacao)
                    
                    for url in urls_encontradas:
                        # Remove o prefixo http:// ou https:// para facilitar a comparação
                        url_limpa = url.replace("https://", "").replace("http://", "").lower()
                        
                        # Checa se a URL bate com algum dos permitidos
                        permitido = False
                        for link_ok in LINKS_PERMITIDOS:
                            if link_ok.lower() in url_limpa:
                                permitido = True
                                break
                        
                        if not permitido:
                            contem_link_nao_permitido = True
                            break

                    if contem_link_nao_permitido:
                        # 1. Apaga a mensagem contendo o link não permitido
                        await context.bot.delete_message(
                            chat_id=GRUPO_PRINCIPAL,
                            message_id=mensagem.message_id
                        )
                        
                        # 2. Envia o aviso para o usuário
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

            # =====================================
            # EDITAR TEXTO
            # =====================================

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

            # =====================================
            # FOTO
            # =====================================

            if mensagem.photo:

                foto = (
                    mensagem.photo[-1].file_id
                )

                legenda = (
                    mensagem.caption
                    or ""
                )

                enviada = await context.bot.send_photo(

                    chat_id=GRUPO_SUPORTE,

                    photo=foto,

                    caption=(
                        f"👤 {usuario}\n\n"
                        f"{legenda}"
                    )

                )

            # =====================================
            # VIDEO
            # =====================================

            elif mensagem.video:

                video = (
                    mensagem.video.file_id
                )

                legenda = (
                    mensagem.caption
                    or ""
                )

                enviada = await context.bot.send_video(

                    chat_id=GRUPO_SUPORTE,

                    video=video,

                    caption=(
                        f"👤 {usuario}\n\n"
                        f"{legenda}"
                    )

                )

            # =====================================
            # ÁUDIO / VOZ (ADICIONADO)
            # =====================================

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

                    caption=(
                        f"👤 {usuario}\n\n"
                        f"{legenda}"
                    )

                )

            # =====================================
            # DOCUMENTO / ARQUIVO (ADICIONADO)
            # =====================================

            elif mensagem.document:

                document_id = mensagem.document.file_id

                legenda = mensagem.caption or ""

                enviada = await context.bot.send_document(

                    chat_id=GRUPO_SUPORTE,

                    document=document_id,

                    caption=(
                        f"👤 {usuario}\n\n"
                        f"{legenda}"
                    )

                )

            # =====================================
            # TEXTO
            # =====================================

            elif mensagem.text:

                texto = (
                    mensagem.text
                    or ""
                )

                enviada = await context.bot.send_message(

                    chat_id=GRUPO_SUPORTE,

                    text=(
                        f"👤 {usuario}\n\n"
                        f"{texto}"
                    )

                )

            # =====================================
            # SALVA IDS
            # =====================================

            if enviada:

                mensagens_gp_para_sup[
                    msg_original
                ] = enviada.message_id

                mensagens_sup_para_gp[
                    enviada.message_id
                ] = msg_original

            print("CLIENTE -> SUPORTE")

        # =====================================
        # SUPORTE -> GRUPO
        # =====================================

        elif chat_id == GRUPO_SUPORTE:

            msg_original = (
                mensagem.message_id
            )

            # =====================================
            # COMANDO EXCLUIR
            # =====================================

            if (
                mensagem.text
                and mensagem.text == "/excluir"
            ):

                if not mensagem.reply_to_message:
                    return

                reply_id = (
                    mensagem.reply_to_message.message_id
                )

                if (
                    reply_id
                    not in mensagens_sup_para_gp
                ):
                    return

                destino_id = (
                    mensagens_sup_para_gp[
                        reply_id
                    ]
                )

                await context.bot.delete_message(

                    chat_id=GRUPO_PRINCIPAL,

                    message_id=destino_id

                )

                print("MENSAGEM EXCLUIDA")

                return

            # =====================================
            # EDITAR TEXTO
            # =====================================

            if update.edited_message:

                if (
                    msg_original
                    not in mensagens_sup_para_gp
                ):
                    return

                destino_id = (
                    mensagens_sup_para_gp[
                        msg_original
                    ]
                )

                texto = (
                    mensagem.text
                    or ""
                )

                await context.bot.edit_message_text(

                    chat_id=GRUPO_PRINCIPAL,

                    message_id=destino_id,

                    text=texto

                )

                print("EDITADO SUPORTE")

                return

            # =====================================
            # FOTO
            # =====================================

            if mensagem.photo:

                foto = (
                    mensagem.photo[-1].file_id
                )

                legenda = (
                    mensagem.caption
                    or ""
                )

                enviada = await context.bot.send_photo(

                    chat_id=GRUPO_PRINCIPAL,

                    photo=foto,

                    caption=legenda,

                    message_thread_id=TOPICO_ID

                )

            # =====================================
            # VIDEO
            # =====================================

            elif mensagem.video:

                video = (
                    mensagem.video.file_id
                )

                legenda = (
                    mensagem.caption
                    or ""
                )

                enviada = await context.bot.send_video(

                    chat_id=GRUPO_PRINCIPAL,

                    video=video,

                    caption=legenda,

                    message_thread_id=TOPICO_ID

                )

            # =====================================
            # ÁUDIO / VOZ (ADICIONADO)
            # =====================================

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

            # =====================================
            # DOCUMENTO / ARQUIVO (ADICIONADO)
            # =====================================

            elif mensagem.document:

                document_id = mensagem.document.file_id

                legenda = mensagem.caption or ""

                enviada = await context.bot.send_document(

                    chat_id=GRUPO_PRINCIPAL,

                    document=document_id,

                    caption=legenda,

                    message_thread_id=TOPICO_ID

                )

            # =====================================
            # TEXTO
            # =====================================

            elif mensagem.text:

                texto = (
                    mensagem.text
                    or ""
                )

                enviada = await context.bot.send_message(

                    chat_id=GRUPO_PRINCIPAL,

                    text=texto,

                    message_thread_id=TOPICO_ID

                )

            # =====================================
            # SALVA IDs
            # =====================================

            if enviada:

                mensagens_sup_para_gp[
                    msg_original
                ] = enviada.message_id

                mensagens_gp_para_sup[
                    enviada.message_id
                ] = msg_original

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
