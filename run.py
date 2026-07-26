import subprocess
import sys

def rodar_script(nome_arquivo):
    return subprocess.Popen([sys.executable, nome_arquivo])

if __name__ == "__main__":
    print("🚀 Iniciando todos os bots...")
    
    # Inicia o suporte, o chat e o financeiro juntos
    p1 = rodar_script("suporte_bot.py")
    p2 = rodar_script("chat_bot.py")
    p3 = rodar_script("financeiro.py")
    
    try:
        p1.wait()
        p2.wait()
        p3.wait()
    except KeyboardInterrupt:
        p1.terminate()
        p2.terminate()
        p3.terminate()
        print("🛑 Bots encerrados.")
