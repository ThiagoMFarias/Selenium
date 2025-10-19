from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# Open a new Chrome browser instance
navegator = webdriver.Chrome()

# Open the target webpage
navegator.get("https://www.hashtagtreinamentos.com/")

# Put the navegator in maximized mode
navegator.maximize_window()

# Close popup
botao_fechar = WebDriverWait(navegator, 10).until(
    EC.element_to_be_clickable((By.ID, "botaoPopupFechar")))
botao_fechar.click()

# reduzir zoom para 50% pois o botão não estava aparecendona tela
WebDriverWait(navegator, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
navegator.execute_script("document.body.style.zoom='50%'")

# Select a element by its class name
# O find_element seleciona o primeiro elemento encontrado
element = navegator.find_element(By.CLASS_NAME, "botao-verde") 
if element.is_displayed():
    WebDriverWait(navegator, 2).until(EC.element_to_be_clickable((By.CLASS_NAME, "botao-verde")))
element.click()

time.sleep(10)