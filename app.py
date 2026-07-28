import os
from flask import Flask, request, jsonify
from iqoptionapi.stable_api import IQ_Option

app = Flask(__name__)

# Configurações da sua conta IQ Option (Recomendado usar conta Demo para testes!)
# Substitua abaixo pelos seus dados de login reais
IQ_EMAIL = "choplivre@gmail.com"
IQ_SENHA = "SAFira0001974"

# Conecta na IQ Option ao iniciar o servidor
print("Conectando à IQ Option...")
API = IQ_Option(IQ_EMAIL, IQ_SENHA)
check, reason = API.connect()

if check:
    print("Conexão com a IQ Option realizada com sucesso!")
    # Define a conta como PRACTICE (Demo) por segurança
    API.change_balance("PRACTICE")
else:
    print(f"Erro ao conectar na IQ Option: {reason}")

@app.route("/")
def home():
    return "Servidor de Sinais MT4 -> IQ Option online e conectado!"

@app.route("/sinal", methods=["POST"])
def receber_sinal():
    dados = request.json
    
    if not dados:
        return jsonify({"erro": "Nenhum dado recebido"}), 400
    
    ativo = dados.get("ativo", "EURUSD")
    acao = dados.get("acao", "call").lower() # 'call' ou 'put'
    valor = float(dados.get("valor", 2.0))   # Valor da entrada
    
    print(f"Sinal recebido: Ativo={ativo} | Ação={acao.upper()} | Valor={valor}")
    
    # Verifica se a API está conectada antes de enviar a ordem
    if not API.check_connect():
        print("Reconectando à IQ Option...")
        API.connect()
        API.change_balance("PRACTICE")

    # Tempo de expiração para Opções Binárias/Digitais (1 minuto = 1)
    expiracao = 1 
    
    # Executa a ordem na IQ Option
    # Nota: Para opções binarias usamos 'binary', para digitais usamos 'digital'
    status, id_pedido = API.buy(valor, ativo, acao, expiracao)
    
    if status:
        print(f"Ordem executada com sucesso! ID: {id_pedido}")
        return jsonify({"status": "sucesso", "id_pedido": id_pedido}), 200
    else:
        print(f"Erro ao executar ordem: {id_pedido}")
        return jsonify({"status": "erro", "detalhe": str(id_pedido)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
