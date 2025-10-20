from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

navegator = webdriver.Chrome()
navegator.get("https://www.hashtagtreinamentos.com/")
navegator.maximize_window()

# Close popup
botao_fechar = WebDriverWait(navegator, 10).until(EC.element_to_be_clickable((By.ID, "botaoPopupFechar")))
botao_fechar.click()

# reduzir zoom para 50% pois o botão não estava aparecendona tela
WebDriverWait(navegator, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
navegator.execute_script("document.body.style.zoom='50%'")

# O find_element seleciona o primeiro elemento encontrado
element = navegator.find_element(By.CLASS_NAME, "botao-verde") 
if element.is_displayed():
    WebDriverWait(navegator, 2).until(EC.element_to_be_clickable((By.CLASS_NAME, "botao-verde")))
element.click()

# Está clicando no elemento cursos pois existem diversos elementos com a classe header__titulo e o find_element retorna o primeiro.
assinatura = navegator.find_element(By.CLASS_NAME, "header__titulo")
assinatura.click()

# Encontrar vários elementos
lista_botes = navegator.find_elements(By.CLASS_NAME, "header__titulo")
for botao in lista_botes:
    if "Assinatura" in botao.text: # aqui eu verifico o texto do botão
        botao.click()
        break

# Selecionar uma aba específica
abas = navegator.window_handles
navegator.switch_to.window(abas[1])  # volta para a primeira aba

# Navegar para um site diferente
navegator.get("https://www.hashtagtreinamentos.com/curso-python")

# Diminuir o zoom da página para 75%
navegator.execute_script("document.body.style.zoom='75%'")

# Escrever em um campo de texto
navegator.find_element(By.ID, "firstname").send_keys("Thiago")
navegator.find_element(By.ID, "email").send_keys("teste@yahoo.com.br")
navegator.find_element(By.ID, "phone").send_keys("85999999999")

# Enviando o formulário
navegator.find_element(By.ID, "_form_2475_submit").click()

time.sleep(10)