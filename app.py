import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor de Sinais MT4 -> IQ Option rodando com sucesso!"

# Rota que vai receber o aviso do MT4 quando a seta aparecer
@app.route("/sinal", methods=["POST"])
def receber_sinal():
    dados = request.json
    
    if not dados:
        return jsonify({"erro": "Nenhum dado recebido"}), 400
    
    # Exemplo de dados que o MT4 vai mandar: ativo, acao (compra/venda), tempo
    ativo = dados.get("ativo", "EURUSD")
    acao = dados.get("acao", "call") # 'call' para compra ou 'put' para venda
    valor = dados.get("valor", 2)    # Valor da entrada em dólares/reais
    
    print(f"Sinal recebido do MT4! Ativo: {ativo} | Ação: {acao.upper()} | Valor: {valor}")
    
    # Aqui é onde entra a lógica de disparo para a IQ Option
    # (Recomendamos sempre testar primeiro na conta Demo da corretora)
    
    return jsonify({
        "status": "sucesso",
        "mensagem": f"Ordem de {acao.upper()} para {ativo} processada com sucesso!"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
