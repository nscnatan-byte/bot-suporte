import json
import os
import requests

ARQUIVO_DADOS = "financeiro.json"
PAGBANK_TOKEN = "DC59C422C80148C1887581D321F1574D"

clientes = [
    {"usuario_id": 1, "email": "carlostenia1@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10, "tipo": "pix"},
    {"usuario_id": 2, "email": "2022sp2@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10, "tipo": "pix"},
    {"usuario_id": 3, "email": "diego.luizpelegrini@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10, "tipo": "pix"},
    {"usuario_id": 4, "email": "geraldomarciano05@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10, "tipo": "pix"},
    {"usuario_id": 5, "email": "marcelosistemasti@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 674527541, "email": "andrei_king@hotmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 7927484407, "email": "Josecarlosnunesdearaujo@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5905610446, "email": "Alcantra.marcelo20@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 0, "email": "retirada@gmail.com", "plano": "RETIRADA", "valor": 0, "historico": -40.0, "tipo": "manual"},
    {"usuario_id": 659959880, "email": "aurelioman8@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 6386260226, "email": "edsoncompact@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 174611186, "email": "luedbavi10@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5506523872, "email": "diego995274033@gmail.com", "plano": "2 MESES", "valor": 0, "historico": 19.0, "tipo": "pix"},
    {"usuario_id": 1598591782, "email": "Jkjchocolates@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5221109408, "email": "adrianodesouzaalvesf29@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1861194662, "email": "leonardozago26@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 852250083, "email": "doug_dmr@hotmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1661482341, "email": "leomayron@hotmail.com", "plano": "2 MESES", "valor": 0, "historico": 19.0, "tipo": "pix"},
    {"usuario_id": 0, "email": "retirada@gmail.com", "plano": "RETIRADA", "valor": 0, "historico": -27.0, "tipo": "manual"},
    {"usuario_id": 6649209900, "email": "rafaelcbn7@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5034337191, "email": "julianobhallu@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1047597829, "email": "brenooliv6+3@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 913890652, "email": "Thy4241@icloud.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 7389065243, "email": "Josemario.silva0000@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 0, "email": "ativador@gmail.com", "plano": "PAGAMENTO", "valor": 0, "historico": 10.0, "tipo": "manual"},
    {"usuario_id": 0, "email": "ativador@gmail.com", "plano": "PAGAMENTO", "valor": 0, "historico": 27.0, "tipo": "manual"},
    {"usuario_id": 5851753521, "email": "cestabasicanato@gmail.com", "plano": "2 MESES", "valor": 0, "historico": 19.0, "tipo": "pix"},
    {"usuario_id": 386958167, "email": "landerangel1@hotmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 934292675, "email": "adilson.stacioni@hotmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5534924933, "email": "boredhott@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 6145272301, "email": "eder_alves0209@hotmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 7177396064, "email": "eliton.prado2020@outlook.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1102136518, "email": "shynaydder.legal@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 842377203, "email": "ricardo_brz@hotmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5375151434, "email": "michaelspb87@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1447379944, "email": "saulokamui@yahoo.com.br", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5214223745, "email": "julianoreis88@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1038866052, "email": "jamessonmagno51@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 7453642632, "email": "nemesiodepacoti@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 2043722403, "email": "victorwendelsg@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1075980533, "email": "mercadodebens@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 0, "email": "retirada@gmail.com", "plano": "RETIRADA", "valor": 0, "historico": -10.0, "tipo": "manual"},
    {"usuario_id": 181438316, "email": "magrzd22@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 814084466, "email": "willerreis@outlook.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 8524841134, "email": "israelgomes.rlz@gmail.com", "plano": "6 MESES", "valor": 0, "historico": 45.0, "tipo": "pix"},
    {"usuario_id": 1223798942, "email": "alexandreddpinvest@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 2110876572, "email": "wildessantos80@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1569773079, "email": "getulyo@hotmail.com", "plano": "2 MESES", "valor": 0, "historico": 19.0, "tipo": "pix"},
    {"usuario_id": 8295976658, "email": "Saiasaparecido672@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 8248667978, "email": "descarregador118877@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 8397637224, "email": "adilson.alves.macena@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 235277735, "email": "ricaleo21@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5533392335, "email": "marcos-rd@hotmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 246767692, "email": "1pepec7583@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 8453473771, "email": "emizael27@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5380771240, "email": "zatipaula06@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1777902617, "email": "gestormarioadm@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 6162860441, "email": "rico979497.r@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1089943004, "email": "za_silva35@hotmail.com", "plano": "3 MESES", "valor": 0, "historico": 27.0, "tipo": "pix"},
    {"usuario_id": 5424968001, "email": "thedhieimison@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1167452808, "email": "salazzar007@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 534638482, "email": "maiquelfl09@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 8653380476, "email": "daniellek69c@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 6034851283, "email": "Claudioneicamila@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 6073497524, "email": "descubrapromo@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5990889311, "email": "Roberto.frayn1988for@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1642832397, "email": "alexandredobecos2@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 1360846210, "email": "zencohe@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"},
    {"usuario_id": 5502009704, "email": "fenlorin@gmail.com", "plano": "1 MÊS", "valor": 0, "historico": 10.0, "tipo": "pix"}
]

def carregar():
    global clientes
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                clientes = json.load(f)
        except:
            pass

def salvar():
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=4)

def total_faturado():
    return sum(float(c.get("historico", 0)) for c in clientes)

def painel():
    carregar()
    total = total_faturado()
    total_clientes = len([c for c in clientes if c.get("usuario_id", 0) != 0])
    return f"💰 **FINANCEIRO XBOT** 💰\n\n👥 CLIENTES ATIVOS: {total_clientes}\n\n💸 VALOR TOTAL:\nR${total:.2f}"

def listar_clientes():
    carregar()
    if not clientes:
        return "Nenhum cliente cadastrado."
    texto = "📋 **LISTA DE CLIENTES** 📋\n\n"
    for c in clientes[-20:]:  
        if c.get("usuario_id") != 0:
            texto += f"📧 {c.get('email')[:30]} | 📦 {c.get('plano')} | 💰 R${c.get('historico')}\n"
    return texto

def registrar_cliente(usuario_id, email, plano, valor, tipo):
    carregar()
    clientes.append({
        "usuario_id": usuario_id,
        "email": email,
        "plano": plano,
        "valor": 0,
        "historico": float(valor),
        "tipo": tipo
    })
    salvar()

def pagar_ativador(valor):
    carregar()
    clientes.append({
        "usuario_id": 0,
        "email": "ativador@gmail.com",
        "plano": "PAGAMENTO",
        "valor": 0,
        "historico": float(valor),
        "tipo": "manual"
    })
    salvar()

def adicionar_valor(email, plano, valor):
    carregar()
    clientes.append({
        "usuario_id": 0,
        "email": email,
        "plano": plano,
        "valor": 0,
        "historico": float(valor),
        "tipo": "manual"
    })
    salvar()

def resetar_financeiro():
    global clientes
    clientes = []
    salvar()

def gerar_pix_pagbank(valor_reais, nome_cliente, email_cliente="cliente@email.com"):
    url = "https://api.pagseguro.com/orders"
    valor_centavos = int(float(valor_reais) * 100)
    
    headers = {
        "Authorization": f"Bearer {PAGBANK_TOKEN}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    payload = {
        "reference_id": "pedido_bot_xbot",
        "customer": {
            "name": nome_cliente,
            "email": email_cliente,
            "tax_id": "00000000000"
        },
        "qr_codes": [
            {
                "amount": {
                    "value": valor_centavos
                }
            }
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        dados = response.json()
        order_id = dados.get("id")
        pix_texto = dados["qr_codes"][0]["text"]
        return order_id, pix_texto
    else:
        print("Erro ao gerar Pix no PagBank:", response.text)
        return None, None

def verificar_status_pagamento(order_id):
    if not order_id:
        return False
        
    url = f"https://api.pagseguro.com/orders/{order_id}"
    headers = {
        "Authorization": f"Bearer {PAGBANK_TOKEN}",
        "accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        dados = response.json()
        charges = dados.get("charges", [])
        for charge in charges:
            if charge.get("status") == "PAID":
                return True
    return False

carregar()
