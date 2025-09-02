import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import datetime

inicio = datetime.datetime.now()
# Função de debug
def debug(message):
    print(f"[DEBUG] {message}")

# Configuração do WebDriver Manager
def setup_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=service, options=options)

### SCRAPPING DO AGROTIMES ###
def collect_links_and_titles_until_limit(driver):
    data = []
    debug("Iniciando coleta de links e títulos até data_limit.")
    
    for x in range(1, 21):
        try:
            link_element = driver.find_element(By.XPATH, f'//*[@id="ultimas-home"]/div[{x}]/div/h2/a')
            link = link_element.get_attribute("href")
            title = link_element.text

            date_element = driver.find_element(By.XPATH, f'//*[@id="ultimas-home"]/div[{x}]/div/div[2]/span')
            date_text = date_element.text
            debug(f"Data encontrada em x={x}: {date_text}")

            if "dia(s) atrás" in date_text:
                debug("Data_limit encontrada. Parando coleta nesta página.")
                return data

            data.append({"Link": link, "Título": title})

        except NoSuchElementException:
            debug(f"Elemento não encontrado para x={x}. Parando a coleta nesta página.")
            break

    debug(f"Coletados {len(data)} links e títulos nesta página até data_limit.")
    return data

def scrape_agrotimes():
    driver = setup_driver()
    data_collection = []
    current_page = 1
    base_url = "https://www.moneytimes.com.br/agrotimes/"

    try:
        while True:
            driver.get(f"{base_url}page/{current_page}/" if current_page > 1 else base_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="ultimas-home"]'))
            )

            new_data = collect_links_and_titles_until_limit(driver)
            data_collection.extend(new_data)

            if len(new_data) < 20:
                debug("CABO ESSE SCRAPING")
                break

            current_page += 1

    except TimeoutException:
        debug("Tempo limite excedido ao carregar a página.")
    finally:
        driver.quit()
    
    df = pd.DataFrame(data_collection)
    df['Segmentação'] = 'Agronegócio'
    return df

### FUNÇÃO PRINCIPAL DE SCRAPING ###
def scrape_moneytimes(url_site, segmentacao):
    driver = setup_driver()
    data = []
    page = 1

    try:
        while True:
            url = f"{url_site}page/{page}/" if page > 1 else url_site
            driver.get(url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'main'))
            )

            for x in range(1, 11):
                try:
                    title_element = driver.find_element(By.XPATH, f"/html/body/div[8]/main/div/div[{x}]/div/h2/a")
                    title = title_element.text
                    link = title_element.get_attribute('href')
                except:
                    title = "ausente"
                    link = "ausente"

                try:
                    date_element = driver.find_element(By.XPATH, f"/html/body/div[8]/main/div/div[{x}]/div/div[2]/span")
                    date = date_element.text
                except:
                    date = "ausente"

                data.append({"Título": title, "Link": link, "Segmentação": segmentacao})

                if "dia(s) atrás" in date:
                    debug("Data limite encontrada. Encerrando scraping.")
                    return pd.DataFrame(data)

            page += 1

    except Exception as e:
        debug(f"Erro durante o scraping: {str(e)}")
    finally:
        driver.quit()
    
    return pd.DataFrame(data)

### SCRAPING DE CONTEÚDO DOS ARTIGOS ###
def scrape_articles(df):
    driver = setup_driver()
    dados = []
    total_artigos = len(df)
    
    try:
        for count, (index, row) in enumerate(df.iterrows(), 1):
            try:
                driver.get(row['Link'])
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/article/div[2]/div/div[1]/div[2]/div[2]/span[1]'))
                )

                # Data
                try:
                    data = driver.find_element(By.XPATH, '/html/body/article/div[2]/div/div[1]/div[2]/div[2]/span[1]').text
                except:
                    data = "ausente"

                # Artigo
                artigo = []
                i = 1
                while True:
                    try:
                        paragrafo = driver.find_element(
                            By.XPATH, f'/html/body/article/div[3]/div[1]/div[1]/p[{i}]').text
                        artigo.append(paragrafo)
                        i += 1
                    except:
                        break

                dados.append({
                    'Data': data,
                    'Artigo': "\n".join(artigo)
                })

                # Cálculo corrigido do progresso
                percentual = (count / total_artigos) * 100
                debug(f"Progresso: {percentual:.2f}% concluído")

            except Exception as e:
                debug(f"Erro no artigo {row['Link']}: {str(e)}")
                dados.append({'Data': None, 'Artigo': None})

            time.sleep(random.uniform(1, 3))

    finally:
        driver.quit()

    return pd.concat([df, pd.DataFrame(dados)], axis=1)
### EXECUÇÃO PRINCIPAL ###
if __name__ == "__main__":
    # Coleta de dados de todas as seções
    df_agro = scrape_agrotimes()
    
    secoes = [
        ("https://www.moneytimes.com.br/tag/empresas/", "Empresas"),
        ("https://www.moneytimes.com.br/tag/resultados/", "Resultados"),
        ("https://www.moneytimes.com.br/tag/imoveis/", "Imóveis/FIIs"),
        ("https://www.moneytimes.com.br/tag/bitcoin-btc/", "Bitcoin"),
        ("https://www.moneytimes.com.br/tag/commodities/", "Commodities")
    ]

    dfs = [df_agro]
    for url, segmento in secoes:
        df_temp = scrape_moneytimes(url, segmento)
        dfs.append(df_temp)
        time.sleep(random.uniform(2, 5))

    # Combina todos os DataFrames
    df_final = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicatas
    df_final = df_final.drop_duplicates(subset=['Link'])
    
    # Coleta conteúdo dos artigos
    df_final = scrape_articles(df_final)
    
    # Salva em CSV
    df_final.to_csv(r'Notícias_scrapped.csv', index=False, encoding='utf-8-sig')
    
    fim = datetime.datetime.now()
    print(f"Demorou: {fim - inicio}")
    
    debug("ARQUIVO SALVO E SCRAPPING CONCLUIDO")