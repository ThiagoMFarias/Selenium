import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import time

""" response = requests.get("http://s2gpr.sefaz.ce.gov.br/licita-web/paginas/licita/PublicacaoList.seam") # Realiza a requisição GET para a URL especificada

print("Status Code:", response.status_code)
print("*************************************")
print("Cabeçalho:", response.headers)
print("*************************************")
print("Conteúdo:", response.text)  # Imprime os primeiros 500 caracteres do conteúdo
print("*************************************")

print(response.content) # Imprime o conteúdo bruto da resposta
print(type(response.content)) # Imprime o tipo do conteúdo

conteudo_bruto = response.content

site = BeautifulSoup(conteudo_bruto, 'html.parser') # Analisa o conteúdo bruto com BeautifulSoup
print(site.prettify()) # Imprime o HTML formatado


def iniciar_navegador():
    navegador = webdriver.Chrome()
    navegador.get("http://s2gpr.sefaz.ce.gov.br/licita-web/paginas/licita/PublicacaoList.seam")
    return navegador

navegador = iniciar_navegador()

# Selecionar a primeira linha da tabela
visualizar = navegador.find_elements(By.CSS_SELECTOR, ".rich-table-row.rich-table-firstrow.linhaImpar")
# for elemento in visualizar:
    # print(elemento.text)


# Extração de dados da tabela
dados = []
for linha in site.select("table.rich-table tr.rich-table-row"):
    colunas = linha.find_all("td") # Obtém todas as colunas da linha
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
        dados.append(registro)

df = pd.DataFrame(dados, columns=["numero", "status", "codigo", "descricao", "orgao", "modalidade", "periodo"])
print(df)

df.to_csv("licitacoes.csv", index=False, encoding="utf-8-sig") # Salva os dados em um arquivo CSV
df.to_excel("licitacoes.xlsx", index=False) # O false é para não salvar o índice como uma coluna no arquivo Excel
""" """for d in dados:
    print(d) """

"""time.sleep(5)"""

""" navegador = webdriver.Chrome()
navegador.get("http://s2gpr.sefaz.ce.gov.br/licita-web/paginas/licita/PublicacaoList.seam")
navegador.maximize_window()

WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rich-table-row")))

dados_totais = []
max_paginas = 20
pagina_atual = 0

while pagina_atual < max_paginas:
    WebDriverWait(navegador, 30).until(
        EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396"))
    )
    site = BeautifulSoup(navegador.page_source, 'html.parser') # Analisa o conteúdo da página atual com BeautifulSoup

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
        botao_proximo = navegador.find_element(
            By.XPATH, "//td[contains(@class, 'rich-datascr-button') and contains(., '»')]"
        )

        WebDriverWait(navegador, 30).until(
            EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396"))
        )

        # Verifica se o botão está desabilitado
        if "rich-datascr-button-dsbld" in botao_proximo.get_attribute("class"):
            print("Fim da paginação.")
            break

        # Clica na próxima página
        navegador.execute_script("arguments[0].click();", botao_proximo)

    except Exception as e:
        print("Não foi possível encontrar o botão de próxima página:", e)
        break
df = pd.DataFrame(dados_totais, columns=["numero", "status", "codigo", "descricao", "orgao", "modalidade", "periodo"])
df.to_excel("licitacoes.xlsx", index=False) # O false é para não salvar o índice como uma coluna no arquivo Excel

# Exibe a quantidade total de registros coletados
print(f"Total de registros coletados: {len(dados_totais)}")
 """
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
WebDriverWait(navegator, 30).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
tipo = navegator.find_element(By.ID, "formularioDeCrud:tipoAquisicaoDecoration:tipoAquisicao")
select = Select(tipo)
select.select_by_value("1199")

# Tipo de regime
while True:
    WebDriverWait(navegator, 30).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    regime = navegator.find_element(By.ID, "formularioDeCrud:j_id260:j_id274:1")
    regime.click()
    break

# Sistemática de aquisição
sistematica = navegator.find_element(By.ID, "formularioDeCrud:sistematicaAquisicaoDecoration:sistAquisicao")
select = Select(sistematica)
select.select_by_value("1124")
time.sleep(1)
    

# Forma de aquisição
while True:
    forma = navegator.find_element(By.ID, "formularioDeCrud:formaAquisicaoDecoration:formaAquisicao")
    select = Select(forma)
    WebDriverWait(navegator, 30).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    select.select_by_value("1229")
    break

# Status da publicação
while True:
    WebDriverWait(navegator, 30).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    status = navegator.find_element(By.ID, "formularioDeCrud:statusDecoration:status")
    select = Select(status)
    select.select_by_value("FINALIZADA_ELETRONICA")
    break

# Região
while True:
    WebDriverWait(navegator, 30).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    regiao = navegator.find_element(By.ID, "formularioDeCrud:microRegiaoDecoration:microRegiao")
    select = Select(regiao)
    select.select_by_value("1155")
    break

# Clicar no botão de buscar
navegator.execute_script("window._selenium_active_requests = 0;")  # Inicializa a variável para rastrear requisições ativas no contexto da página
botao_buscar = navegator.find_element(By.ID, "formularioDeCrud:pesquisar")
botao_buscar.click()
time.sleep(3)

# Selecionar a primeira licitação da lista
while True:
    WebDriverWait(navegator, 30).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    linhas = navegator.find_elements(By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar")
    linhas[0].click()
    time.sleep(3)
    break

# Vsualizar propostas
visu_proposta = navegator.find_element(By.ID, "formularioDeCrud:visualizarSuperior")
if visu_proposta.is_displayed():
    WebDriverWait(navegator, 20).until(EC.element_to_be_clickable((By.ID,"formularioDeCrud:visualizarSuperior")))
    visu_proposta.click()
else:
    print("Elemento 'Visualizar Propostas' não está visível.")
time.sleep(3)

# Expandir resultados
while True:
    #WebDriverWait(navegator, 30).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id")))
    ver_resultados = navegator.find_element(By.ID, "formularioDeCrud:grupoItensCoEPDataTable:0:j_id294")
    ver_resultados.click()
    break
time.sleep(3)
site = BeautifulSoup(navegator.page_source, 'html.parser') # Analisa o conteúdo da página atual com BeautifulSoup

dados_totais = []

# Localiza o tbody da tabela desejada pelo ID específico
tabela_itens = site.find("tbody", id="formularioDeCrud:grupoItensCoEPDataTable:0:itensGrupoListAction:tb")

for linha in tabela_itens.select("tr.rich-table-row"):
    colunas = linha.find_all("td")
    
    # Garante que só linhas completas (com as 10 colunas) sejam processadas
    if len(colunas) >= 10:
        registro = {
            "item": colunas[0].get_text(strip=True),
            "descricao": colunas[1].get_text(strip=True),
            "fornecedor": colunas[2].get_text(strip=True),
            "quantidade": colunas[3].get_text(strip=True),
            "valor_unitario": colunas[4].get_text(strip=True),
            "valor_total": colunas[5].get_text(strip=True),
            "melhor_lance": colunas[6].get_text(strip=True),
            "total_melhor_lance": colunas[7].get_text(strip=True),
            "marca": colunas[8].get_text(strip=True),
        }
        dados_totais.append(registro)

df = pd.DataFrame(dados_totais, columns=["item", "descricao", "fornecedor", "quantidade", "valor_unitario", "valor_total", "melhor_lance", "total_melhor_lance", "marca"])
df.to_excel("licitacoes.xlsx", index=False) # O false é para não salvar o índice como uma coluna no arquivo Excel
print(dados_totais)
time.sleep(5)
