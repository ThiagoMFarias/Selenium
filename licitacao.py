from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
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

# Clicar no link da primeira licitação
primeira_licitacao = navegator.find_element(By.ID, "formularioDeCrud:pagedDataTable:397177:j_id429")
if primeira_licitacao.is_displayed():
    WebDriverWait(navegator, 2).until(EC.element_to_be_clickable((By.ID,
                                      "formularioDeCrud:pagedDataTable:397177:j_id429")))
    primeira_licitacao.click()
time.sleep(3)

# Vsualizar propostas
visu_proposta = navegator.find_element(By.ID, "formularioDeCrud:visualizarSuperior")
if visu_proposta.is_displayed():
    WebDriverWait(navegator, 2).until(EC.element_to_be_clickable((By.ID,
                                      "formularioDeCrud:visualizarSuperior")))
    visu_proposta.click()
time.sleep(3)

# Ver resultados
ver_resultados = navegator.find_element(By.ID, "formularioDeCrud:grupoItensCoEPDataTable:0:j_id294")
ver_resultados.click()

# Guardar valores numa variável para uso futuro
valores = navegator.find_element(By.ID, "formularioDeCrud:itensCoEPDataTable:0:valorItem")
print("Valor do item:", valores.text)

time.sleep(30)
