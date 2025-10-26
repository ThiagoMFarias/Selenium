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
time.sleep(1)

# Preencher tipo de aquisição
tipo = navegator.find_element(By.ID, "formularioDeCrud:tipoAquisicaoDecoration:tipoAquisicao")
select = Select(tipo)
select.select_by_value("1199")

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

# Clicar no botão de buscar
botao_buscar = navegator.find_element(By.ID, "formularioDeCrud:pesquisar")
botao_buscar.click()
WebDriverWait(navegator, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
WebDriverWait(navegator, 20).until(lambda d: d.execute_script("return window.jQuery != undefined && jQuery.active == 0"))
time.sleep(20)