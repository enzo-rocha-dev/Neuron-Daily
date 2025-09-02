
import pandas as pd
import os

# Configurações
ARQUIVO_ENTRADA = "inscritos.xlsx"
SHEET = "Sheet1"
ARQUIVO_SAIDA_1 = "emails_parte1.xlsx"
ARQUIVO_SAIDA_2 = "emails_parte2.xlsx"

try:
    # Carregar o arquivo Excel
    df = pd.read_excel(ARQUIVO_ENTRADA, sheet_name=SHEET)
except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")
    exit(1)

# Extrair e-mails da coluna "Email"
emails = []
for linha in df.get("Email", []):
    if pd.notna(linha):
        campos = [campo.strip() for campo in str(linha).split(",") if campo.strip()]
        if campos:
            emails.append(campos[0].lower())

# Remover duplicados
emails = list(set(emails))

# Criar DataFrame
emails_df = pd.DataFrame(emails, columns=["email"])

# Dividir em duas partes iguais
metade = len(emails_df) // 2
df_parte1 = emails_df.iloc[:metade]
df_parte2 = emails_df.iloc[metade:]

# Salvar em arquivos Excel
df_parte1.to_excel(ARQUIVO_SAIDA_1, index=False, engine="openpyxl")
df_parte2.to_excel(ARQUIVO_SAIDA_2, index=False, engine="openpyxl")

print("Arquivos criados com sucesso!")