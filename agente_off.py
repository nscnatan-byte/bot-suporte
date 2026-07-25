from telegram import Update

from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

from datetime import datetime

# =========================================
# TOKEN
# =========================================

TOKEN = "8568503789:AAEOsoZYEhImCFWxClgRln-RsMyJSqeQut8"

# =========================================
# CONTROLE
# =========================================

usuarios_respondidos = {}

# =========================================
# ATENDIMENTO OFF
# =========================================

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        usuario_id = update.effective_chat.id

        hora = datetime.now().hour

        # =========================================
        # OFFLINE
        # =========================================

        if hora >= 20 or hora < 8:

            # EVITA SPAM
            if usuario_id in usuarios_respondidos:
                return

            usuarios_respondidos[usuario_id] = True

            await update.message.reply_text(

                "🌟 ATENDIMENTO E SUPORTE XBOT 🌟\n\n"

                "Olá, pessoal! 👋\n\n"

                "Gostaria de lembrar que o suporte e a renovação de licenças estão disponíveis até às 20h, todos os dias.\n\n"

                "Após esse horário, não estarei respondendo, mas fiquem à vontade para deixar sua mensagem que responderei assim que possível.\n\n"

                "🕗 Retorno às 08:00 da manhã (Horário de Brasília).\n\n"

                "🌐 SITE OFICIAL:\n"
                "https://xbot.net.br/?rep=nsc\n\n"

                "🔗 LINK DO SUPORTE:\n"
                "https://t.me/x_bot_automatizador/19\n\n"

                "🙏 Agradeço pela compreensão!"

            )

    except Exception as erro:

        print("ERRO:", erro)

# =========================================
# APP
# =========================================

print("AGENTE OFF ONLINE")

app = Application.builder().token(TOKEN).build()

app.add_handler(

    MessageHandler(

        filters.TEXT
        & (
            filters.ChatType.PRIVATE
            | filters.ChatType.GROUPS
        )
        & ~filters.COMMAND,

        responder

    )

)

app.run_polling()