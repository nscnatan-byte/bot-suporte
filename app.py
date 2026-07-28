import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor de Sinais MT4 online e pronto!"

@app.route("/sinal", methods=["POST"])
def receber_sinal():
    dados = request.json
    
    if not dados:
        return jsonify({"erro": "Nenhum dado recebido"}), 400
    
    ativo = dados.get("ativo", "EURUSD")
    acao = dados.get("acao", "call").lower() # 'call' ou 'put'
    valor = float(dados.get("valor", 2.0))   # Valor da entrada
    
    print(f"Sinal recebido com sucesso: Ativo={ativo} | Ação={acao.upper()} | Valor={valor}")
    
    return jsonify({
        "status": "sucesso", 
        "mensagem": f"Sinal de {acao.upper()} para {ativo} no valor de {valor} processado com sucesso!"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
