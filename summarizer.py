import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator
from transformers import pipeline, BartTokenizer, BartForConditionalGeneration
import locale
from sentence_transformers import SentenceTransformer, util
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import datetime

inicio = datetime.datetime.now()
# Configurar localização para formatação de data
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Tentativa alternativa
    except locale.Error:
        print("Aviso: Não foi possível definir a localização pt_BR. Usando padrão do sistema.")

# Parâmetros de configuração
max_tokens = 200
min_tokens = 50
similaridade = 0.7

def debug(message):
    print(f"[DEBUG] {message}")

def load_data():
    try:
        df = pd.read_csv('Notícias_scrapped.csv')
        debug(f"Arquivo carregado com sucesso. Total de registros: {len(df)}")
        
        # Verificar e remover linhas com valores nulos na coluna 'Artigo'
        null_articles = df['Artigo'].isna().sum()
        if null_articles > 0:
            debug(f"Encontrados {null_articles} artigos nulos. Removendo...")
            df = df.dropna(subset=['Artigo'])
        
        # Filtrar por palavras-chave indesejadas
        filtro = ['patrocinado', "day-trade", "conteudo-de-marca", "xpromo", "empiricus", 'eleicoes', 'prefeito', 'eleicao', 'eleito']
        original_len = len(df)
        df = df[df['Link'].apply(lambda x: isinstance(x, str) and all(excl not in x.lower() for excl in filtro))]
        debug(f"Filtro aplicado. {original_len - len(df)} registros removidos.")
        
        return df
    except Exception as e:
        debug(f"Erro ao carregar dados: {e}")
        raise

def create_retry_session(retries=3, backoff_factor=0.3):
    """Criar uma sessão HTTP com retry para solicitações instáveis"""
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def translate_text(text, chunk_size=4000):
    """Traduz texto de português para inglês, com tratamento de erros"""
    # Se o texto for nulo ou não for uma string, retornar texto vazio
    if not isinstance(text, str) or pd.isna(text):
        debug("Texto nulo ou não é string. Pulando...")
        return ""
    
    debug(f"Traduzindo texto de {len(text)} caracteres")
    translated_chunks = []
    
    # Dividir o texto em chunks para evitar limites de API
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        if not chunk.strip():  # Ignorar chunks vazios
            continue
            
        success = False
        attempts = 0
        
        while not success and attempts < 3:
            try:
                # Adicionar um tempo aleatório entre solicitações para evitar bloqueios
                time.sleep(np.random.uniform(0.5, 2.0))
                translated = GoogleTranslator(source='pt', target='en').translate(chunk)
                if translated:
                    translated_chunks.append(translated)
                    success = True
                else:
                    debug("Tradução retornou texto vazio")
                    attempts += 1
            except Exception as e:
                debug(f"Erro na tentativa {attempts+1}: {str(e)}")
                time.sleep(2 ** attempts)  # Backoff exponencial
                attempts += 1
                
        if not success:
            debug("Falha na tradução após 3 tentativas - retornando texto parcial")
            
    return ' '.join(translated_chunks)

def process_translations(df):
    """Processa todas as traduções com controle de progresso"""
    translated_texts = []
    total = len(df)
    
    for i, article in enumerate(df['Artigo']):
        try:
            translated = translate_text(article)
            translated_texts.append(translated)
            progress = ((i + 1) / total) * 100
            debug(f"Progresso da tradução: {round(progress, 2)}% ({i+1}/{total})")
        except Exception as e:
            debug(f"Erro ao traduzir artigo {i}: {e}")
            translated_texts.append("")  # Adicionar string vazia para manter o alinhamento
    
    return translated_texts

def summarize_text(text, min_tokens, max_tokens):
    """Resumir texto usando o modelo BART"""
    if not isinstance(text, str) or not text.strip():
        debug("Texto vazio para resumo - pulando")
        return ""
        
    try:
        # Limitar o texto de entrada para evitar problemas de memória
        if len(text) > 10000:
            text = text[:10000]
            
        inputs = tokenizer(text, max_length=1024, truncation=True, return_tensors="pt")
        summary_ids = model_large.generate(
            inputs["input_ids"], 
            max_length=max_tokens, 
            min_length=min_tokens,
            no_repeat_ngram_size=3,
            early_stopping=True
        )
        return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    except Exception as e:
        debug(f"Erro ao resumir texto: {e}")
        return ""

def process_summaries(df):
    """Processa todos os resumos com controle de progresso"""
    summaries = []
    total = len(df)
    
    for i, text in enumerate(df['artigo_ingles']):
        try:
            summary = summarize_text(text, min_tokens, max_tokens)
            summaries.append(summary)
            progress = ((i + 1) / total) * 100
            debug(f"Progresso dos resumos: {round(progress, 2)}% ({i+1}/{total})")
        except Exception as e:
            debug(f"Erro ao resumir texto {i}: {e}")
            summaries.append("")
    
    return summaries

def compute_cosine_similarity(df, column_name):
    """Calcula a similaridade do cosseno entre os textos"""
    debug("Calculando similaridade entre os textos...")
    
    # Verificar se há textos vazios
    empty_texts = df[column_name].apply(lambda x: not isinstance(x, str) or not x.strip()).sum()
    if empty_texts > 0:
        debug(f"Aviso: {empty_texts} textos vazios encontrados na coluna {column_name}")
    
    # Filtra para usar apenas textos não vazios
    valid_texts = df[df[column_name].apply(lambda x: isinstance(x, str) and bool(x.strip()))]
    
    if len(valid_texts) == 0:
        debug("Nenhum texto válido para calcular similaridade")
        return pd.DataFrame()
    
    try:
        # Carrega o modelo para embeddings
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Gera embeddings para cada linha da coluna
        embeddings = model.encode(valid_texts[column_name].tolist(), convert_to_tensor=True)
        
        # Calcula a matriz de similaridade de cosseno entre todos os embeddings
        cosine_similarities = util.cos_sim(embeddings, embeddings)
        
        # Retorna a matriz de similaridade como um DataFrame
        similarity_df = pd.DataFrame(cosine_similarities.cpu().numpy(),
                                     index=valid_texts.index, columns=valid_texts.index)
        
        return similarity_df
    except Exception as e:
        debug(f"Erro ao calcular similaridade: {e}")
        return pd.DataFrame()

def filter_high_similarity(df, similarity_df, threshold):
    """Filtra artigos com alta similaridade"""
    if similarity_df.empty:
        debug("Matriz de similaridade vazia. Pulando filtragem.")
        return df
        
    debug(f"Filtrando artigos com similaridade > {threshold}...")
    
    try:
        # Identificar pares de índices com similaridade maior que o threshold
        high_similarity_pairs = similarity_df.stack() \
            .reset_index() \
            .rename(columns={0: 'similarity', 'level_0': 'idx1', 'level_1': 'idx2'})
        
        # Filtrar apenas pares onde a similaridade é maior que o limite e idx1 != idx2
        high_similarity_pairs = high_similarity_pairs[
            (high_similarity_pairs['similarity'] > threshold) & 
            (high_similarity_pairs['idx1'] != high_similarity_pairs['idx2'])
        ]
        
        if high_similarity_pairs.empty:
            debug("Nenhum par com alta similaridade encontrado.")
            return df
            
        # Inicializar um conjunto para armazenar índices a serem mantidos
        to_keep = set(df.index)
        
        # Iterar sobre os pares de alta similaridade
        for _, row in high_similarity_pairs.iterrows():
            i, j = row['idx1'], row['idx2']
            # Verificar se ambos os índices ainda estão no conjunto
            if i in to_keep and j in to_keep:
                # Seleciona aleatoriamente um dos dois índices para manter
                to_remove = np.random.choice([i, j])
                # Remove o índice selecionado para remoção do conjunto `to_keep`
                to_keep.discard(to_remove)
        
        # Filtrar o DataFrame original com os índices a serem mantidos
        filtered_df = df.loc[list(to_keep)]
        
        debug(f"Removidos {len(df) - len(filtered_df)} artigos similares.")
        return filtered_df
    except Exception as e:
        debug(f"Erro ao filtrar por similaridade: {e}")
        return df

def translate_back_to_pt(text):
    """Traduz o resumo de inglês para português"""
    if not isinstance(text, str) or not text.strip():
        return ""
        
    try:
        return GoogleTranslator(source='en', target='pt').translate(text)
    except Exception as e:
        debug(f"Erro ao traduzir de volta para português: {e}")
        return ""

def process_reverse_translations(df):
    """Processa todas as traduções de volta para português"""
    pt_translations = []
    total = len(df)
    
    for i, text in enumerate(df['Resumo_ingles']):
        try:
            translated = translate_back_to_pt(text)
            pt_translations.append(translated)
            progress = ((i + 1) / total) * 100
            debug(f"Progresso da tradução PT: {round(progress, 2)}% ({i+1}/{total})")
        except Exception as e:
            debug(f"Erro ao traduzir texto {i} para PT: {e}")
            pt_translations.append("")
    
    return pt_translations

def main():
    try:
        # Carregar dados
        df = load_data()
        nmr_noticias = len(df)
        debug(f"Processando {nmr_noticias} notícias")
        
        # Traduzir artigos para inglês
        debug("Iniciando tradução para inglês...")
        df['artigo_ingles'] = process_translations(df)
        
        # Carregar modelo de resumo
        debug("Carregando modelo de resumo...")
        global tokenizer, model_large
        tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
        model_large = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
        
        # Resumir textos em inglês
        debug("Iniciando resumo dos textos...")
        df["Resumo_ingles"] = process_summaries(df)
        
        # Calcular similaridade entre resumos
        debug("Calculando similaridade entre resumos...")
        similarity_matrix = compute_cosine_similarity(df, 'Resumo_ingles')
        
        # Filtrar artigos similares
        debug("Filtrando artigos similares...")
        df_filtered = filter_high_similarity(df, similarity_matrix, threshold=similaridade)
        
        # Traduzir resumos de volta para português
        debug("Traduzindo resumos para português...")
        df_filtered['Resumo'] = process_reverse_translations(df_filtered)
        
        # Salvar resultados
        debug("Salvando resultados...")
        df_filtered.to_csv("Notícias_Resumidas.csv", index=False)
        debug(f"Arquivo salvo com {len(df_filtered)} notícias resumidas e filtradas")
        
        debug("Processamento concluído com sucesso!")
        
    except Exception as e:
        debug(f"Erro no processamento principal: {e}")

if __name__ == "__main__":
    main()
    
fim = datetime.datetime.now()
print(f"Demorou: {fim - inicio}")