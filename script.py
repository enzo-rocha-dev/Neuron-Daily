import subprocess
import sys
import datetime

def install_dependencies():
    required = ["pandas"]  # Adicione outras dependências se necessário
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

if __name__ == "__main__":
    install_dependencies()  # Instala dependências no ambiente atual

    inicio = datetime.datetime.now()

    scripts = [
        r"C:\Users\scorz\OneDrive\Área de Trabalho\Luiz\neuron\newsletter neuron\scraping.py",
        r"C:\Users\scorz\OneDrive\Área de Trabalho\Luiz\neuron\newsletter neuron\summarizer.py",
        r"C:\Users\scorz\OneDrive\Área de Trabalho\Luiz\neuron\newsletter neuron\writer.py",
        r"C:\Users\scorz\OneDrive\Área de Trabalho\Luiz\neuron\newsletter neuron\extrair.py",
        r"C:\Users\scorz\OneDrive\Área de Trabalho\Luiz\neuron\newsletter neuron\sender.py",
        r"C:\Users\scorz\OneDrive\Área de Trabalho\Luiz\neuron\newsletter neuron\sender_mkt.py"
    ]

    for script in scripts:
        try:
            # Use sys.executable para garantir que o mesmo Python seja usado
            subprocess.run([sys.executable, script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erro em {script}: {e}")
            sys.exit(1)

    fim = datetime.datetime.now()
    print(f"Demorou: {fim - inicio}")