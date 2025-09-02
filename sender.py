import smtplib
import pandas as pd
import os
from email.message import EmailMessage
import random
import datetime

# Configurações do Gmail (Enviar pelo email do marketing)

#EMAIL_REMETENTE = "neuron.dsai@gmail.com"
#SENHA_APP = "vdpz hdhv jskh dxwy"

EMAIL_REMETENTE = "neurondsai.marketing@gmail.com"
SENHA_APP = "ftkn svrk fsov awrg"

inicio = datetime.datetime.now()
# Lendo os e-mails dos inscritos
emails = []
for arquivo_inscritos in ["emails_parte1.xlsx", "emails_parte2.xlsx"]:
    if os.path.exists(arquivo_inscritos):
        df_inscritos = pd.read_excel(arquivo_inscritos, engine="openpyxl")
        emails += df_inscritos["email"].dropna().tolist()
    else:
        print(f"Arquivo de inscritos não encontrado: {arquivo_inscritos}")

# Encontrar o último arquivo HTML gerado
arquivos_html = [f for f in os.listdir() if f.startswith("noticias_") and f.endswith(".html")]
if not arquivos_html:
    print("Nenhum arquivo de newsletter encontrado.")
    exit()

arquivo_newsletter = max(arquivos_html, key=os.path.getctime)

# Ler o conteúdo do HTML
with open(arquivo_newsletter, "r", encoding="utf-8") as file:
    conteudo_html = file.read()

chamada = [
    "📰 Neuron Daily - Seu resumo diário do mercado!",
    "🚀 Neuron Daily - O essencial do dia para você!",
    "📊 Neuron Daily - As notícias que movem o mercado!",
    "🔎 Neuron Daily - Fique por dentro do mercado!",
    "🧠 Neuron Daily - Inteligência de mercado direto no seu e-mail!",
    "⏳ Neuron Daily - Seu update financeiro rápido!",
    "🌎 Neuron Daily - O giro financeiro essencial do dia!",
    "📉 Neuron Daily - Seu jornal diário!",
    "⚡ Neuron Daily - Informação rápida, decisão inteligente!",
    "📬 Neuron Daily - O mercado na sua caixa de entrada!",
    "📢 Neuron Daily - Notícias essenciais, sem ruído!",
    "💹 Neuron Daily - Acompanhe as tendências do mercado!",
    "📥 Neuron Daily - O que importa no mercado, direto para você!",
    "📰 Neuron Daily - O resumo que você precisa para começar o dia!",
    "💼 Neuron Daily - Informação estratégica para quem acompanha o mercado!",
    "📡 Neuron Daily - Seu radar do mercado financeiro!",
    "🔮 Neuron Daily - Antecipe os movimentos do mercado!",
    "🕒 Neuron Daily - Informação precisa, no momento certo!"
]

# Seleciona uma frase aleatória
subfrase = random.choice(chamada)

# Criar e enviar e-mails
def enviar_email(destinatario, html_content):
    msg = EmailMessage()
    msg["Subject"] = subfrase
    msg["From"] = "Neuron DSAI<" + EMAIL_REMETENTE + ">"
    msg["To"] = destinatario
    msg.set_content("Sua newsletter está disponível em HTML. Se não visualizar corretamente, ative a exibição de e-mails em HTML.")
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_REMETENTE, SENHA_APP)
            server.send_message(msg)
        print(f"E-mail enviado para {destinatario}")
    except Exception as e:
        print(f"Erro ao enviar para {destinatario}: {e}")


# Enviar para todos os inscritos
for email in emails:
    enviar_email(email, conteudo_html)

print("Todos os e-mails foram enviados!")

fim = datetime.datetime.now()
print(f"Demorou: {fim - inicio}")
