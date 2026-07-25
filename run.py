import subprocess
import sys

def rodar_script(nome_arquivo):
    return subprocess.Popen([sys.executable, nome_arquivo])

if __name__ == "__main__":
    print("🚀 Iniciando os dois bots...")
    
    # Inicia o bot de suporte principal e o bot de chat dos grupos
    p1 = rodar_script("suporte_bot.py")
    p2 = rodar_script("chat_bot.py")
    
    try:
        p1.wait()
        p2.wait()
    except KeyboardInterrupt:
        p1.terminate()
        p2.terminate()
        print("🛑 Bots encerrados.")
