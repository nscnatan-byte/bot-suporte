import subprocess
import time

def rodar_script(nome_arquivo):
    return subprocess.Popen(["python", nome_arquivo])

if __name__ == "__main__":
    print("🚀 Iniciando os dois bots juntos...")
    
    # Inicia o bot de pagamento
    p1 = rodar_script("bot.py")
    
    # Aguarda 2 segundos para organizar
    time.sleep(2)
    
    # Inicia o bot de suporte
    p2 = rodar_script("suporte_bot.py")
    
    # Mantém ambos rodando
    p1.wait()
    p2.wait()
