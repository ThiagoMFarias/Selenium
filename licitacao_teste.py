from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import time

def iniciar_navegador():
    navegador = webdriver.Chrome()
    navegador.get("http://s2gpr.sefaz.ce.gov.br/licita-web/paginas/licita/PublicacaoList.seam")
    navegador.maximize_window()
    return navegador

navegator = iniciar_navegador()
print("Navegador iniciado e página carregada.")

# Preencher o campo "Natureza da Aquisição"
natureza = navegator.find_element(By.ID, "formularioDeCrud:naturezaAquisicaoDecoration:naturezaAquisicao")
select = Select(natureza)
select.select_by_value("1104")
time.sleep(2)

# Preencher tipo de aquisição
tipo = navegator.find_element(By.ID, "formularioDeCrud:tipoAquisicaoDecoration:tipoAquisicao")
select = Select(tipo)
select.select_by_value("1199")
time.sleep(1)

# Tipo de regime
regime = navegator.find_element(By.ID, "formularioDeCrud:j_id260:j_id274:1")
regime.click()
time.sleep(1)

# Sistemática de aquisição
sistematica = navegator.find_element(By.ID, "formularioDeCrud:sistematicaAquisicaoDecoration:sistAquisicao")
select = Select(sistematica)
select.select_by_value("1124")
time.sleep(1)

# Forma de aquisição
forma = navegator.find_element(By.ID, "formularioDeCrud:formaAquisicaoDecoration:formaAquisicao")
select = Select(forma)
select.select_by_value("1229")
time.sleep(1)

# Status da publicação
status = navegator.find_element(By.ID, "formularioDeCrud:statusDecoration:status")
select = Select(status)
select.select_by_value("FINALIZADA_ELETRONICA")

# Região
regiao = navegator.find_element(By.ID, "formularioDeCrud:microRegiaoDecoration:microRegiao")
select = Select(regiao)
select.select_by_value("1155")
time.sleep(1)

# Clicar no botão de buscar
navegator.execute_script("window._selenium_active_requests = 0;")  # Inicializa a variável para rastrear requisições ativas no contexto da página
botao_buscar = navegator.find_element(By.ID, "formularioDeCrud:pesquisar")
botao_buscar.click()
WebDriverWait(navegator, 30).until(lambda d: d.execute_script(
    "return document.readyState === 'complete' && "
    "(window._selenium_active_requests === 0) && "
    "(window.jQuery ? jQuery.active === 0 : true);"
))
time.sleep(10)

dados_totais = []
max_paginas = 20
pagina_atual = 0

while pagina_atual < max_paginas:
    WebDriverWait(navegator, 30).until(
        EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396"))
    )
    site = BeautifulSoup(navegator.page_source, 'html.parser') # Analisa o conteúdo da página atual com BeautifulSoup

    for licitacao in site.select("table.rich-table tr.rich-table-row"):
        colunas = licitacao.find_all("td")
        if len(colunas) >= 8:
            registro = {
                "numero": colunas[1].get_text(strip=True),
                "status": colunas[2].get_text(strip=True),
                "codigo": colunas[3].get_text(strip=True),
                "descricao": colunas[4].get_text(strip=True),
                "orgao": colunas[5].get_text(strip=True),
                "modalidade": colunas[6].get_text(strip=True),
                "periodo": colunas[7].get_text(strip=True),
            }
            dados_totais.append(registro)
            print(dados_totais)
    pagina_atual += 1
    try:
        botao_proximo = navegator.find_element(
            By.XPATH, "//td[contains(@class, 'rich-datascr-button') and contains(., '»')]"
        )

        WebDriverWait(navegator, 30).until(
            EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396"))
        )

        # Verifica se o botão está desabilitado
        if "rich-datascr-button-dsbld" in botao_proximo.get_attribute("class"):
            print("Fim da paginação.")
            break

        # Clica na próxima página
        navegator.execute_script("arguments[0].click();", botao_proximo)

    except Exception as e:
        print("Não foi possível encontrar o botão de próxima página:", e)
        break
df = pd.DataFrame(dados_totais, columns=["numero", "status", "codigo", "descricao", "orgao", "modalidade", "periodo"])
df.to_excel("licitacoes.xlsx", index=False) # O false é para não salvar o índice como uma coluna no arquivo Excel

# Exibe a quantidade total de registros coletados
print(f"Total de registros coletados: {len(dados_totais)}")
