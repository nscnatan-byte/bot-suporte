import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Configuração de logs para acompanhar o robô
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Variáveis globais de controle da banca e meta de 2%
DADOS_BANCA = {
    "banca_inicial": 0.0,
    "lucro_acumulado": 0.0,
    "meta_diaria": 0.0,
    "ativo": "EURUSD"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Robô de Operações Automáticas Ativo!**\n\n"
        "Use o comando `/banca <valor>` para configurar seu capital inicial.\n"
        "Exemplo: `/banca 1000`"
    )

async def set_banca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DADOS_BANCA
    args = context.args
    if not args:
        await update.message.reply_text("❌ Uso correto: /banca <valor_inicial>\nExemplo: /banca 1000")
        return
    
    try:
        valor = float(args[0])
        DADOS_BANCA["banca_inicial"] = valor
        DADOS_BANCA["lucro_acumulado"] = 0.0
        DADOS_BANCA["meta_diaria"] = valor * 0.02
        
        await update.message.reply_text(
            f"✅ Banca configurada com sucesso!\n"
            f"💰 Valor Inicial: ${valor}\n"
            f"🎯 Meta de 2% (Lucro Alvo): ${DADOS_BANCA['meta_diaria']:.2f}"
        )
    except ValueError:
        await update.message.reply_text("❌ Por favor, insira um número válido para la banca.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 **Status Atual do Robô**\n"
        f"Banca Inicial: ${DADOS_BANCA['banca_inicial']}\n"
        f"Lucro Atual: ${DADOS_BANCA['lucro_acumulado']:.2f}\n"
        f"Meta de 2%: ${DADOS_BANCA['meta_diaria']:.2f}"
    )

if __name__ == '__main__':
    # Token configurado diretamente no código
    TOKEN_TELEGRAM = '8947979521:AAHUNCEDhJU5Ee6YOEvtJeUSo01YAFXiSpI'
    
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('banca', set_banca))
    app.add_handler(CommandHandler('status', status))

    print('Robô iniciado e pronto na nuvem...')
    app.run_polling()
