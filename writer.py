import pandas as pd
import yfinance as yf
import locale
from datetime import datetime, timedelta
import random
import time
from pathlib import Path

# Attempt to set locale for Portuguese Brazil date formatting
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')  # Windows alternative
    except:
        print("Could not set Brazilian locale, using default")

# Lista de frases
frases = [
    "As principais novidades do mercado estão aqui. Acompanhe e fique à frente!",
    "Fique por dentro das principais tendências e oportunidades do mercado. Sua dose semanal de insights está aqui!",
    "Fique informado: análises rápidas e notícias essenciais sobre finanças, agro e cripto para você tomar decisões assertivas.",
    "Insights valiosos sobre finanças, agro e cripto para você começar a semana bem informado.",
    "Resumimos as notícias que importam: tudo sobre finanças, agro e muito mais de forma rápida e direta. Economize tempo e fique informado!",
    # ... other phrases ...
]

# Seleciona uma frase aleatória
subtitulo = random.choice(frases)

def contar_palavras(resumo):
    return len(resumo.split()) if isinstance(resumo, str) else 0

def calcular_tempo_economizado(df, coluna_tempo):
    total_minutos = df[coluna_tempo].sum()
    minuto_inteiro = int(total_minutos)
    segundo_inteiro = int((total_minutos - minuto_inteiro) * 60)
    return minuto_inteiro, segundo_inteiro

def obter_fechamentos_com_retry():
    """Obter fechamentos com mecanismo de retry e valores default para casos de falha"""
    tickers = {'IBOV': '^BVSP', 'BTC': 'BTC-USD', 'USD': 'BRL=X'}
    resultados = {}
    
    # Valores padrão para casos de falha - usando dados recentes como fallback
    valores_default = {
        'IBOV': (125000.25, 0.35),  # Valor aproximado do Ibovespa 
        'BTC': (62500.50, 1.20),    # Valor aproximado do Bitcoin
        'USD': (5.10, -0.25)        # Valor aproximado do Dólar
    }
    
    print("Coletando cotações do Yahoo Finance...")
    
    for nome, ticker in tickers.items():
        # Tentativa com retry
        tentativas_maximas = 3
        for tentativa in range(tentativas_maximas):
            try:
                time.sleep(2 + tentativa * 3)  # Aumenta o tempo entre tentativas
                # Tenta baixar dados dos últimos 2 dias para calcular variação
                dados = yf.download(ticker, period="2d", progress=False)
                
                # Verificação robusta
                if dados.empty or 'Close' not in dados.columns or len(dados) < 1:
                    raise ValueError(f"Dados insuficientes para {nome}")
                
                fechamento = round(float(dados['Close'].iloc[-1]), 2)
                if len(dados) > 1:
                    variacao = round(((dados['Close'].iloc[-1] / dados['Close'].iloc[-2]) - 1) * 100, 2)
                else:
                    variacao = 0.00
                
                resultados[nome] = (fechamento, variacao)
                print(f"{nome}: Fechamento={fechamento}, Variação={variacao}%")
                break  # Sai do loop de tentativas se for bem-sucedido
                
            except Exception as e:
                print(f"Tentativa {tentativa+1} falhou para {nome}: {e}")
                if tentativa == tentativas_maximas - 1:  # Última tentativa
                    print(f"Usando valores padrão para {nome}")
                    resultados[nome] = valores_default[nome]
    
    return resultados

def parse_custom_date(date_str):
    """
    Função para lidar com diferentes formatos de data que podem estar no CSV
    """
    try:
        # Tenta formatos diferentes
        formats = [
            '%d %b %Y, %H:%M',    # ex: 08 maio 2025, 16:10
            '%d %B %Y, %H:%M',    # ex: 08 maio 2025, 16:10 (nome do mês completo)
            '%d/%m/%Y %H:%M',     # ex: 08/05/2025 16:10
            '%Y-%m-%d %H:%M:%S'   # formato ISO
        ]
        
        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
                
        # Se nenhum formato funcionar, tenta com o parser flexível
        return pd.to_datetime(date_str, dayfirst=True)
    except:
        # Retorna a data atual como fallback
        print(f"Não foi possível parsear a data: {date_str}. Usando data atual.")
        return datetime.now()

def gerar_html(df, resultados, minutos_leitura, segundos_leitura, minutos, segundos):
    """Gera o arquivo HTML da newsletter"""
    html = f"""
    <html>
    <head>
        <title>Neuron Daily</title>
        <meta charset='utf-8'>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
            body {{ 
                font-family: 'Poppins', sans-serif; 
                color: #000; 
                background-color: #020f2b; 
                padding: 20px; 
                background-image: url('https://imgur.com/AOe2EN5.png'); 
                background-repeat: repeat; 
                min-height: 100vh;
            }}
            .container {{ 
                width: 90%;
                max-width: 900px; 
                margin: auto; 
                background: white; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); 
            }}
            .header {{ 
                text-align: center;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px;
                background-color: white;
            }}
            .logoneuron {{ 
                max-width: 150px; 
                top: 10px; 
                right: 20px; 
                height: auto;
            }}
            .title-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                flex-grow: 1;
            }}
            .title {{ 
                font-size: 32px; 
                font-weight: 700; 
                color: #063799; 
                font-family: 'Merriweather', serif;
                text-transform: uppercase;
            }}
            .slogan {{ 
                font-size: 14px; 
                color: #555; 
                margin-top: -10px; 
            }}
            .market-info {{ 
                display: flex;
                color: white;
                justify-content: center; 
                gap: 20px; 
                flex-wrap: wrap; 
                text-align: center;
                margin-top: 20px;
            }}
            .market-info div {{
                background-color: #063799;
                padding: 10px 15px;
                border-radius: 5px;
                min-width: 120px;
                font-weight: bold;
            }}
            .news-container {{
                padding: 20px 0;
            }}
            .news-section-title {{
                font-family: 'Merriweather', serif;
                font-size: 26px;
                font-weight: bold;
                border-bottom: 3px solid #000;
                margin-bottom: 15px;
                padding-bottom: 5px;
                text-transform: uppercase;
            }}
            .news-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr; /* Duas colunas para o estilo de jornal */
                gap: 20px;
            }}
            .news-article {{
                padding: 15px;
                border-bottom: 1px solid #ccc;
                font-family: 'Merriweather', serif;
            }}
            .news-title {{
                font-size: 20px;
                font-weight: bold;
            }}
            .news-summary {{
                font-size: 16px;
                text-align: justify;
            }}
            .news-link a {{
                font-weight: bold;
                color: #063799;
            }}
            .sponsors {{
                margin: 30px 0;
                text-align: center;
                padding: 15px;
                background: #f0f0f0;
                border-radius: 8px;
            }}
            .footer-container {{ 
                text-align: center;
                background: #063799;
                color: white;
                padding: 20px;
                border-radius: 12px;
                margin: 20px auto;
                max-width: 90%;
            }}
            .footer-container h3 {{
                font-size: 22px;
                margin-bottom: 10px;
            }}
            .footer-container p {{
                font-size: 16px;
                margin-bottom: 15px;
            }}
            .noticia {{ 
                border-bottom: 1px solid #063799; 
                padding: 15px 0;
            }}
            .bold {{ 
                font-weight: bold; 
            }}
            .noticia-title {{ 
                font-size: 18px; 
                font-weight: bold; 
            }}
            a {{ 
                color: #063799; 
                text-decoration: none; 
                font-weight: bold; 
            }}
            .footer-links {{
                margin: 10px 0;
            }}
            .footer-links a {{
                display: inline-block;
                margin: 5px 10px;
                padding: 8px 15px;
                background: white;
                color: #007BFF;
                font-weight: bold;
                text-decoration: none;
                border-radius: 5px;
                transition: 0.3s ease-in-out;
            }}
            .footer-links a:hover{{
                background: #0056b3;
                color: white;
            }}
            .about-section {{
                margin-top: 20px;
                padding: 15px;
                background: #f0f0f0;
                border-radius: 8px;
                text-align: center;
            }}
            .about-title {{
                font-size: 20px;
                font-weight: bold;
            }}
            .about-text {{
                font-size: 12px;
                margin-bottom: 10px;
            }}
            .about-link a {{
                color: #063799;
                font-weight: bold;
            }}
            .powered {{
                font-size: 14px;
                margin-top: 20px;
                opacity: 0.9;
            }}
            @media (max-width: 600px) {{
                .container {{
                    width: 95%;
                    padding: 15px;
                }}
                .news-grid {{
                    grid-template-columns: 1fr;
                }}
                .news-title {{
                    font-size: 16px;
                }}
                .market-info {{
                    flex-direction: column; 
                    align-items: center;
                    text-align: center;
                }}
                .logoneuron {{
                    max-width: 120px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class='container'>
            <div class='header'>
                <img src='https://imgur.com/RIFKqS9.png' class='logoneuron' alt='Neuron'>
            </div>
            <div class="title-container">
                <h2>{subtitulo}</h2>  
            </div>
            <div class="market-info">
                <div>IBOV: {resultados['IBOV'][0]} ({resultados['IBOV'][1]}%)</div>
                <div>USD: {resultados['USD'][0]} ({resultados['USD'][1]}%)</div>
                <div>BTC: {resultados['BTC'][0]} ({resultados['BTC'][1]}%)</div>
            </div>
            <p class='bold'>Tempo estimado de leitura: {minutos_leitura} min {segundos_leitura} seg</p>
    """
    
    html += "<div class='news-container'>"
    
    # Verifica se há categorias para criar seções
    if 'Segmentação' in df.columns and not df['Segmentação'].isna().all():
        # Agrupa por segmentação
        for segmento in df['Segmentação'].unique():
            if pd.isna(segmento):
                continue
                
            segmentada = df[df['Segmentação'] == segmento]
            html += f"<h2 class='news-section-title'>{segmento.upper()}</h2>"
            html += "<div class='news-grid'>"

            for _, row in segmentada.iterrows():
                titulo = row['Título'] if 'Título' in row and not pd.isna(row['Título']) else "Notícia"
                resumo = row['Resumo'] if 'Resumo' in row and not pd.isna(row['Resumo']) else "Resumo não disponível"
                link = row['Link'] if 'Link' in row and not pd.isna(row['Link']) else "#"
                
                html += f"""
                <div class='news-article'>
                    <h3 class='news-title'>{titulo}</h3>
                    <p class='news-summary'>{resumo}</p>
                    <p class='news-link'><a href='{link}' target='_blank'>Leia mais...</a></p>
                </div>
                """
            
            html += "</div>"  # Fechando a news-grid para cada segmento
    else:
        # Se não houver segmentação, exibe todas as notícias juntas
        html += "<h2 class='news-section-title'>NOTÍCIAS DO DIA</h2>"
        html += "<div class='news-grid'>"
        
        for _, row in df.iterrows():
            titulo = row['Título'] if 'Título' in row and not pd.isna(row['Título']) else "Notícia"
            resumo = row['Resumo'] if 'Resumo' in row and not pd.isna(row['Resumo']) else "Resumo não disponível"
            link = row['Link'] if 'Link' in row and not pd.isna(row['Link']) else "#"
            
            html += f"""
            <div class='news-article'>
                <h3 class='news-title'>{titulo}</h3>
                <p class='news-summary'>{resumo}</p>
                <p class='news-link'><a href='{link}' target='_blank'>Leia mais...</a></p>
            </div>
            """
            
        html += "</div>"  # Fechando a news-grid
   
    html += f"""
            <p class='bold'>Você economizou: {minutos} min {segundos} seg lendo apenas os resumos!</p>
            <div class='footer-container'>
                <h3>📢 Fale com a gente!</h3>
                <p>Queremos saber o que você achou desta edição! Tem sugestões, dúvidas ou ideias incríveis?</p>
                <div class="footer-links">
                    <a href="https://linkedin.com/company/neurondsai" target="_blank" rel="noopener noreferrer">🔗 LinkedIn</a>
                    <a href="https://instagram.com/neurondsai" target="_blank" rel="noopener noreferrer">📸 Instagram</a>
                    <a href="https://wa.link/tu5r04" target="_blank" rel="noopener noreferrer">📱 WhatsApp</a>
                </div>
                <p>🚀 Juntos, podemos tornar o <strong>Neuron Daily</strong> ainda melhor!</p>
                <p class="powered">Powered by <strong>Neuron DSAI</strong></p>
            </div>
            <p style='font-size: 8px; text-align: center;'>Você recebeu este boletim porque se inscreveu no Neuron Daily.</p>
            <p style='font-size: 8px; text-align: center;'>
                <a href='https://neurondsai.substack.com/subscribe' style='color: gray; text-decoration: none;'>Se inscrever</a> |
                <a href='https://neurondsai.substack.com/action/disable_email?utm_source=substack&utm_medium=email' style='color: gray; text-decoration: none;'>Cancelar inscrição</a>
            </p>
            <div class='about-section'>
                <h2 class='about-title'>Quem Somos</h2>
                <p class='about-text'>A Neuron Data Science and Artificial Intelligence (Neuron DSAI) é uma entidade estudantil da Universidade de São Paulo (USP) apaixonada por inteligência artificial e ciência de dados. Nosso objetivo é desenvolver tecnologias inovadoras e acessíveis, promovendo conhecimento e impacto positivo na sociedade.</p>
                <p class='about-text'>O Neuron Daily é uma ferramenta que procura notícias diárias do mercado, as traduz, resume e envia para os emails, ajudando os leitores a economizarem tempo. O projeto começou em 2024 com João Gabriel G. Silveira, aluno de Economia, que criou o "AI Market Now" para compartilhar resumos com amigos. Em 2025, já com o nome de "Neuron Daily", ele orientou os membros a automatizar o processo, permitindo a geração e envio de boletins financeiros de forma rápida e eficiente.</p>
                <p class='about-text'>Através de projetos, como o Neuron Daily, buscamos conectar tecnologia e informação, tornando dados complexos acessíveis para todos.</p>
                <p class='about-link'><a href='https://www.instagram.com/p/DGmJ6_YRDV1/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==' target='_blank'>Saiba mais sobre nós</a></p>
            </div>
            <div style="background-color: black; color: white; text-align: center; padding: 10px; font-size: 12px; font-family: Arial, sans-serif;">
                &copy; 2025 Neuron Data Science And Artificial Inteligence. &middot; FEARP-USP<br>
                Av. Bandeirantes, 3900 &middot; Vila Monte Alegre &middot; 14040-905 &middot; Ribeirão Preto, SP
            </div>
        </div>
    </body>
    </html>
    """
    
    filename = f'noticias_{datetime.now().strftime("%d-%m-%Y")}.html'
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)
    print(f"Arquivo HTML gerado com sucesso: {filename}")
    return filename

def main():
    try:
        # Verifica se o arquivo CSV existe
        csv_file = "Notícias_Resumidas.csv"
        if not Path(csv_file).exists():
            print(f"Erro: O arquivo {csv_file} não foi encontrado!")
            return
            
        # Lê o CSV
        print(f"Lendo arquivo {csv_file}...")
        df = pd.read_csv(csv_file)
        
        # Processamento das datas de forma robusta
        print("Processando datas...")
        if 'Data' in df.columns:
            df['Data_Parsed'] = df['Data'].apply(parse_custom_date)
            
            # Filtra para notícias recentes (último dia)
            data_corte = datetime.now() - timedelta(days=1)
            df = df[df['Data_Parsed'] >= data_corte]
            
            # Formata de volta para string no formato desejado
            df['Data'] = df['Data_Parsed'].dt.strftime('%d %b %Y, %H:%M')
            
            # Ordena por data e segmentação
            df = df.sort_values(by=['Data_Parsed', 'Segmentação'], ascending=[False, True])
        else:
            print("Aviso: Coluna 'Data' não encontrada no CSV.")
        
        # Remove linhas sem resumo
        df = df.dropna(subset=['Resumo'])
        
        if len(df) == 0:
            print("Aviso: Não há notícias para exibir após a filtragem!")
            return
        
        # Calcula estatísticas de leitura
        df['Tamanho Artigo Completo'] = df['Artigo'].apply(contar_palavras)
        df['Tamanho Resumo'] = df['Resumo'].apply(contar_palavras)
        df['Diferença entre o resumo e o completo'] = df['Tamanho Artigo Completo'] - df['Tamanho Resumo']
        df['Economia de tempo'] = df['Diferença entre o resumo e o completo'] / 180  # Palavras por minuto
        df['Tempo leitura_resumo'] = df['Tamanho Resumo'] / 180
        
        # Obtém fechamentos
        resultados = obter_fechamentos_com_retry()
        
        # Calcula tempos
        minutos, segundos = calcular_tempo_economizado(df, 'Economia de tempo')
        minutos_leitura, segundos_leitura = calcular_tempo_economizado(df, 'Tempo leitura_resumo')
        
        # Gera o HTML
        arquivo_gerado = gerar_html(df, resultados, minutos_leitura, segundos_leitura, minutos, segundos)
        print(f"Processo concluído com sucesso! Arquivo gerado: {arquivo_gerado}")
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()