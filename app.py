import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    MessageHandler, 
    ConversationHandler, 
    filters
)

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Estados da Conversa
EMAIL, SENHA = range(2)
BANCA_VALOR = range(1)

# Variáveis globais de controle
DADOS_USUARIO = {}
DADOS_BANCA = {
    "banca_inicial": 0.0,
    "lucro_acumulado": 0.0,
    "meta_diaria": 0.0
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Robô de Operações Automáticas Ativo!**\n\n"
        "Comandos disponíveis:\n"
        "🔹 `/conectar` - Inicia o login passo a passo na IQ Option\n"
        "🔹 `/banca` - Configura o valor da sua banca\n"
        "🔹 `/status` - Vê o progresso atual e a meta de 2%"
    )

async def conectar_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📧 Por favor, digite o seu **e-mail** de acesso da IQ Option:")
    return EMAIL

async def receber_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DADOS_USUARIO['email'] = update.message.text
    await update.message.reply_text("🔑 Agora, digite a sua **senha** da IQ Option:")
    return SENHA

async def receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DADOS_USUARIO['senha'] = update.message.text
    await update.message.reply_text("✅ Credenciais recebidas com sucesso! (Módulo de conexão pronto)")
    return ConversationHandler.END

async def banca_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Qual é o valor da sua **banca inicial** hoje? (Digite apenas o número, ex: 1000)")
    return BANCA_VALOR

async def receber_banca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DADOS_BANCA
    try:
        valor = float(update.message.text)
        DADOS_BANCA["banca_inicial"] = valor
        DADOS_BANCA["lucro_acumulado"] = 0.0
        DADOS_BANCA["meta_diaria"] = valor * 0.02
        
        await update.message.reply_text(
            f"✅ **Banca configurada com sucesso!**\n"
            f"💰 Valor Inicial: ${valor}\n"
            f"🎯 Meta de 2% (Lucro Alvo): ${DADOS_BANCA['meta_diaria']:.2f}"
        )
    except ValueError:
        await update.message.reply_text("❌ Valor inválido. Digite apenas números (ex: 500).")
        
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operação cancelada.")
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 **Status Atual do Robô**\n"
        f"Banca Inicial: ${DADOS_BANCA['banca_inicial']}\n"
        f"Lucro Atual: ${DADOS_BANCA['lucro_acumulado']:.2f}\n"
        f"Meta de 2%: ${DADOS_BANCA['meta_diaria']:.2f}"
    )

if __name__ == '__main__':
    TOKEN_TELEGRAM = '8947979521:AAHUNCEDhJU5Ee6YOEvtJeUSo01YAFXiSpI'
    
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()

    conv_conectar = ConversationHandler(
        entry_points=[CommandHandler('conectar', conectar_inicio)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_email)],
            SENHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_senha)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    )

    conv_banca = ConversationHandler(
        entry_points=[CommandHandler('banca', banca_inicio)],
        states={
            BANCA_VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_banca)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    )

    app.add_handler(conv_conectar)
    app.add_handler(conv_banca)
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('status', status))

    print('Robô iniciado e pronto na nuvem...')
    app.run_polling()
