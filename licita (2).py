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


def aplicar_filtros(nav):
    # Natureza da Aquisição
    natureza = nav.find_element(By.ID, "formularioDeCrud:naturezaAquisicaoDecoration:naturezaAquisicao")
    Select(natureza).select_by_value("1111")
    time.sleep(2)

    # Tipo de aquisição
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    tipo = nav.find_element(By.ID, "formularioDeCrud:tipoAquisicaoDecoration:tipoAquisicao")
    Select(tipo).select_by_value("1206")

    # Tipo de regime
    regime = WebDriverWait(nav, 60).until(
        EC.element_to_be_clickable((By.ID, "formularioDeCrud:j_id259:j_id273:1"))
    )
    regime.click()

    # Sistemática de aquisição
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    sistematica = nav.find_element(By.ID, "formularioDeCrud:sistematicaAquisicaoDecoration:sistAquisicao")
    Select(sistematica).select_by_value("1131")
    time.sleep(2)

    # Forma de aquisição
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    forma = nav.find_element(By.ID, "formularioDeCrud:formaAquisicaoDecoration:formaAquisicao")
    Select(forma).select_by_value("1236")

    # Status da publicação
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    status = nav.find_element(By.ID, "formularioDeCrud:statusDecoration:status")
    Select(status).select_by_value("FINALIZADA_ELETRONICA")

    # Região
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    regiao = nav.find_element(By.ID, "formularioDeCrud:microRegiaoDecoration:microRegiao")
    Select(regiao).select_by_value("1162")

    # Buscar
    botao_buscar = nav.find_element(By.ID, "formularioDeCrud:pesquisar")
    botao_buscar.click()
    time.sleep(3)


def esperar_overlays(nav):
    """Espera os dois overlays sumirem."""
    WebDriverWait(nav, 60).until(
        EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396"))
    )
    WebDriverWait(nav, 60).until(
        EC.invisibility_of_element_located((By.ID, "j_id18"))
    )


def esperar_paginacao(nav):
    """Espera a paginação aparecer na página."""
    WebDriverWait(nav, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "td.rich-datascr-act"))
    )
    time.sleep(2)


def pagina_atual_numero(nav):
    """Retorna o número da página atualmente ativa."""
    return int(nav.find_element(By.CSS_SELECTOR, "td.rich-datascr-act").text.strip())


def avancar_uma_pagina(nav):
    """Avança apenas uma página e espera o número da página mudar."""
    pagina_antes = pagina_atual_numero(nav)

    botao_proximo = nav.find_element(
        By.XPATH, "//td[contains(@class, 'rich-datascr-button') and contains(., '»') and not(contains(., '»»'))]"
    )
    if "rich-datascr-button-dsbld" in botao_proximo.get_attribute("class"):
        raise Exception("Botão próximo está desabilitado.")

    nav.execute_script("arguments[0].click();", botao_proximo)

    # Espera o número da página mudar de fato
    WebDriverWait(nav, 60).until(
        lambda d: pagina_atual_numero(d) != pagina_antes
    )


def navegar_para_pagina(nav, numero_pagina):
    """Navega clicando no botão próximo até chegar na página desejada.
    Pressupõe que o navegador já está na página 1."""
    if numero_pagina == 1:
        return

    # Espera a paginação estar visível antes de começar
    esperar_paginacao(nav)

    for _ in range(numero_pagina - 1):
        pagina_antes = pagina_atual_numero(nav)

        botao_proximo = nav.find_element(
            By.XPATH, "//td[contains(@class, 'rich-datascr-button') and contains(., '»') and not(contains(., '»»'))]"
        )
        if "rich-datascr-button-dsbld" in botao_proximo.get_attribute("class"):
            raise Exception("Página não existe — botão próximo está desabilitado.")

        nav.execute_script("arguments[0].click();", botao_proximo)

        # Espera o número da página mudar de fato
        WebDriverWait(nav, 60).until(
            lambda d: pagina_atual_numero(d) != pagina_antes
        )

    # Confirma que chegou na página certa
    pagina_confirmada = pagina_atual_numero(nav)
    if pagina_confirmada != numero_pagina:
        raise Exception(f"Esperava página {numero_pagina}, mas está na página {pagina_confirmada}.")


def pagina_existe(nav, numero_pagina):
    """Verifica se a página informada existe na paginação."""
    try:
        navegar_para_pagina(nav, numero_pagina)
        return True
    except Exception:
        return False


def scraping_licitacao(nav):
    """Faz o scraping de todos os grupos de itens de uma licitação."""
    dados = []
    site = BeautifulSoup(nav.page_source, 'html.parser')

    # Busca todos os tbodys — tanto o padrão com botão expandir quanto sem
    todos_tbodys = site.find_all("tbody", id=lambda x: x and (
        "itensGrupoListAction:tb" in x or
        "itemCoEPDataTable:tb" in x
    ))

    if not todos_tbodys:
        print("     Nenhuma tabela de itens encontrada.")
        return dados

    for tbody in todos_tbodys:
        for linha in tbody.select("tr.rich-table-row"):
            colunas = linha.find_all("td")
            if len(colunas) >= 8:
                registro = {
                    "item": colunas[0].get_text(strip=True),
                    "descricao": colunas[1].get_text(strip=True),
                    "fornecedor": colunas[2].get_text(strip=True),
                    "quantidade": colunas[3].get_text(strip=True),
                    "valor_unitario": colunas[4].get_text(strip=True),
                    "valor_total": colunas[5].get_text(strip=True),
                    "melhor_lance": colunas[6].get_text(strip=True),
                    "total_melhor_lance": colunas[7].get_text(strip=True),
                    "marca": colunas[8].get_text(strip=True) if len(colunas) >= 9 else "",
                }
                dados.append(registro)

    return dados


# ─── ESCOLHA DO INTERVALO ────────────────────────────────────────────────────
# Início do programa: pede para o usuário escolher o intervalo de páginas a ser coletado, validando se as páginas existem antes de iniciar o scraping.
print("=== Configuração do intervalo de páginas ===")
pagina_inicio = int(input("Página inicial: "))
pagina_fim = int(input("Página final: "))

# Valida se as páginas existem
print("\nValidando intervalo...")
nav_validacao = iniciar_navegador()
aplicar_filtros(nav_validacao)

if not pagina_existe(nav_validacao, pagina_fim):
    print(f"Página {pagina_fim} não existe. Verifique o intervalo e tente novamente.")
    nav_validacao.quit()
    exit()

nav_validacao.quit()
print(f"Intervalo válido! Rodando da página {pagina_inicio} até {pagina_fim}...")

# ─── LOOP PRINCIPAL ──────────────────────────────────────────────────────────

dados_totais = []

# Abre navegador principal, aplica filtros, espera carregar e navega para pagina_inicio
nav_principal = iniciar_navegador()
aplicar_filtros(nav_principal)
esperar_overlays(nav_principal)   # garante que a página carregou
esperar_paginacao(nav_principal)  # garante que a paginação está visível
navegar_para_pagina(nav_principal, pagina_inicio)

for pagina_atual in range(pagina_inicio, pagina_fim + 1):
    print(f"\n=== Processando página {pagina_atual}/{pagina_fim} ===")

    # Na primeira iteração já está na página certa
    # Nas demais, avança apenas 1 página
    if pagina_atual > pagina_inicio:
        avancar_uma_pagina(nav_principal)

    linhas = nav_principal.find_elements(By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar")
    total_linhas = len(linhas)

    print(f"Licitações encontradas na página {pagina_atual}: {total_linhas}")

    for indice in range(total_linhas):
        print(f"  → Abrindo licitação {indice + 1}/{total_linhas} da página {pagina_atual}...")

        # Abre navegador limpo para cada licitação
        nav = iniciar_navegador()
        aplicar_filtros(nav)

        try:
            # Espera carregar e navega até a página correta
            esperar_overlays(nav)
            esperar_paginacao(nav)
            navegar_para_pagina(nav, pagina_atual)

            # Espera os overlays sumirem antes de clicar na licitação
            esperar_overlays(nav)

            linhas_nav = WebDriverWait(nav, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar")))
            linhas_nav[indice].click()
            time.sleep(2)

            # Visualizar proposta
            visu_proposta = WebDriverWait(nav, 20).until(
                EC.element_to_be_clickable((By.ID, "formularioDeCrud:visualizarSuperior"))
            )
            visu_proposta.click()
            time.sleep(3)

            # Tentar expandir itens (só existe quando os itens estão recolhidos)
            try:
                ver_resultados = WebDriverWait(nav, 5).until(
                    EC.element_to_be_clickable((By.ID, "formularioDeCrud:grupoItensCoEPDataTable:0:j_id293"))
                )
                ver_resultados.click()
                time.sleep(10)
            except:
                print("     Botão expandir não encontrado, verificando tabela diretamente...")
                site_check = BeautifulSoup(nav.page_source, 'html.parser')
                tbodys_check = site_check.find_all("tbody", id=lambda x: x and (
                    "itensGrupoListAction:tb" in x or
                    "itemCoEPDataTable:tb" in x
                ))
                if not tbodys_check:
                    print("     Nenhuma tabela encontrada, pulando licitação.")
                    nav.quit()
                    continue
                print(f"     {len(tbodys_check)} tabela(s) já visível(is), capturando dados...")
                time.sleep(3)

            # Scraping dos itens
            dados = scraping_licitacao(nav)
            dados_totais.extend(dados)
            print(f"     {len(dados)} itens coletados.")

        except Exception as e:
            print(f"     Erro na licitação {indice + 1} da página {pagina_atual}: {e}")

        finally:
            nav.quit()

nav_principal.quit()

# ─── EXPORTAR PARA EXCEL ─────────────────────────────────────────────────────
if dados_totais:
    nome_arquivo = f"licitacoes_pag{pagina_inicio}_ate_{pagina_fim}.xlsx"
    df = pd.DataFrame(dados_totais, columns=[
        "item", "descricao", "fornecedor", "quantidade",
        "valor_unitario", "valor_total", "melhor_lance",
        "total_melhor_lance", "marca"
    ])
    df.to_excel(nome_arquivo, index=False)
    print(f"\nConcluído! {len(dados_totais)} registros salvos em {nome_arquivo}")
else:
    print("\nNenhum dado coletado.")
