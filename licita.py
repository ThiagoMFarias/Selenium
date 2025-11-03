import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import time

response = requests.get("http://s2gpr.sefaz.ce.gov.br/licita-web/paginas/licita/PublicacaoList.seam") # Realiza a requisição GET para a URL especificada

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

# Substitua 'nome-da-classe' pelo nome da classe que deseja procurar
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
""" for d in dados:
    print(d) """

time.sleep(5)
