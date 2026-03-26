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
    Select(natureza).select_by_value("1112")
    time.sleep(2)

    # Tipo de aquisição
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    WebDriverWait(nav, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#formularioDeCrud\\:tipoAquisicaoDecoration\\:tipoAquisicao option[value='1207']"))
    )
    tipo = nav.find_element(By.ID, "formularioDeCrud:tipoAquisicaoDecoration:tipoAquisicao")
    Select(tipo).select_by_value("1207")

    # Tipo de regime
    regime = WebDriverWait(nav, 60).until(
        EC.element_to_be_clickable((By.ID, "formularioDeCrud:j_id259:j_id273:1"))
    )
    regime.click()

    # Sistemática de aquisição
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    sistematica = nav.find_element(By.ID, "formularioDeCrud:sistematicaAquisicaoDecoration:sistAquisicao")
    Select(sistematica).select_by_value("1132")
    time.sleep(2)

    # Forma de aquisição
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    WebDriverWait(nav, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#formularioDeCrud\\:formaAquisicaoDecoration\\:formaAquisicao option[value='1237']"))
    )
    forma = nav.find_element(By.ID, "formularioDeCrud:formaAquisicaoDecoration:formaAquisicao")
    Select(forma).select_by_value("1237")

    # Status da publicação
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    status = nav.find_element(By.ID, "formularioDeCrud:statusDecoration:status")
    Select(status).select_by_value("FINALIZADA_ELETRONICA")

    # Região
    WebDriverWait(nav, 60).until(EC.invisibility_of_element_located((By.ID, "formularioDeCrud:j_id396")))
    regiao = nav.find_element(By.ID, "formularioDeCrud:microRegiaoDecoration:microRegiao")
    Select(regiao).select_by_value("1163")

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

    # Força o foco na janela do navegador
    nav.switch_to.window(nav.current_window_handle)

    # Espera as linhas da tabela estarem presentes
    WebDriverWait(nav, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar"))
    )

    # Tenta esperar o overlay j_id18 sumir (ignora se não existir)
    try:
        WebDriverWait(nav, 10).until(
            EC.invisibility_of_element_located((By.ID, "j_id18"))
        )
    except:
        pass

    time.sleep(2)
    pagina_antes = pagina_atual_numero(nav)
    print(f"     [avancar] Página atual antes do clique: {pagina_antes}")

    botao_proximo = WebDriverWait(nav, 60).until(
        EC.presence_of_element_located((By.XPATH, "//td[contains(@class, 'rich-datascr-button') and contains(., '»') and not(contains(., '»»'))]"))
    )
    if "rich-datascr-button-dsbld" in botao_proximo.get_attribute("class"):
        raise Exception("Botão próximo está desabilitado.")

    # Rola para o TOPO da página antes de clicar
    nav.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    # Clica via execute_script direto no botão
    nav.execute_script("arguments[0].click();", botao_proximo)
    time.sleep(3)

    pagina_depois = pagina_atual_numero(nav)
    print(f"     [avancar] Página após o clique: {pagina_depois}")

    # Espera chegar exatamente na página seguinte
    pagina_esperada = pagina_antes + 1
    WebDriverWait(nav, 30).until(
        lambda d: pagina_atual_numero(d) == pagina_esperada
    )


def navegar_para_pagina(nav, numero_pagina):
    """Navega clicando no botão próximo até chegar na página desejada.
    Pressupõe que o navegador já está na página 1."""
    from selenium.webdriver.common.action_chains import ActionChains

    if numero_pagina == 1:
        return

    # Espera a paginação estar visível antes de começar
    esperar_paginacao(nav)

    for _ in range(numero_pagina - 1):
        pagina_antes = pagina_atual_numero(nav)

        botao_proximo = WebDriverWait(nav, 60).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(@class, 'rich-datascr-button') and contains(., '»') and not(contains(., '»»'))]"))
        )
        if "rich-datascr-button-dsbld" in botao_proximo.get_attribute("class"):
            raise Exception("Página não existe — botão próximo está desabilitado.")

        # Rola para o TOPO da página antes de clicar — evita overlay cobrir o botão
        nav.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        nav.execute_script("arguments[0].click();", botao_proximo)
        time.sleep(3)

        # Espera o número da página mudar de fato
        pagina_esperada = pagina_antes + 1
        WebDriverWait(nav, 30).until(
            lambda d: pagina_atual_numero(d) == pagina_esperada
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


def converter_valor(texto):
    """Converte string no formato brasileiro para float."""
    try:
        return float(texto.replace(".", "").replace(",", "."))
    except:
        return None


def converter_data(texto):
    """Converte data DD/MM/AAAA para AAAA-MM-DD."""
    try:
        from datetime import datetime
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except:
        return None


def scraping_licitacao(nav, numero_processo, data_inicio):
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
                    "numero_processo": numero_processo,
                    "data_inicio": converter_data(data_inicio),
                    "item": colunas[0].get_text(strip=True),
                    "descricao": colunas[1].get_text(strip=True),
                    "fornecedor": colunas[2].get_text(strip=True),
                    "quantidade": colunas[3].get_text(strip=True),
                    "valor_unitario": converter_valor(colunas[4].get_text(strip=True)),
                    "valor_total": converter_valor(colunas[5].get_text(strip=True)),
                    "melhor_lance": converter_valor(colunas[6].get_text(strip=True)),
                    "total_melhor_lance": converter_valor(colunas[7].get_text(strip=True)),
                    "marca": colunas[8].get_text(strip=True) if len(colunas) >= 9 else "",
                }
                dados.append(registro)

    return dados


# ─── ESCOLHA DO INTERVALO ────────────────────────────────────────────────────

from datetime import datetime
inicio = datetime.now()
print(f"Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}")

print("=== Configuração do intervalo de páginas ===")
pagina_inicio = int(input("Página inicial: "))
pagina_fim = int(input("Página final: "))

# Valida se as páginas existem
print("\nValidando intervalo...")
nav_validacao = iniciar_navegador()
aplicar_filtros(nav_validacao)
WebDriverWait(nav_validacao, 60).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar"))
)
time.sleep(2)

if not pagina_existe(nav_validacao, pagina_fim):
    print(f"Página {pagina_fim} não existe. Verifique o intervalo e tente novamente.")
    nav_validacao.quit()
    exit()

nav_validacao.quit()
print(f"Intervalo válido! Rodando da página {pagina_inicio} até {pagina_fim}...")

# ─── LOOP PRINCIPAL ──────────────────────────────────────────────────────────

dados_totais = []

for pagina_atual in range(pagina_inicio, pagina_fim + 1):
    print(f"\n=== Processando página {pagina_atual}/{pagina_fim} ===")
    dados_pagina = []  # acumula dados só da página atual
    total_linhas = 0
    while True:
        nav_pagina = iniciar_navegador()
        try:
            aplicar_filtros(nav_pagina)
            WebDriverWait(nav_pagina, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar"))
            )
            time.sleep(2)
            navegar_para_pagina(nav_pagina, pagina_atual)
            linhas = nav_pagina.find_elements(By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar")
            linhas = sorted(linhas, key=lambda el: el.location['y'])
            total_linhas = len(linhas)
            print(f"Licitações encontradas na página {pagina_atual}: {total_linhas}")
            break  # conseguiu — sai do while
        except Exception as e:
            print(f"     Erro ao navegar para página {pagina_atual}, tentando novamente: {e}")
        finally:
            nav_pagina.quit()

    for indice in range(total_linhas):
        print(f"  → Abrindo licitação {indice + 1}/{total_linhas} da página {pagina_atual}...")

        while True:
            nav = iniciar_navegador()
            aplicar_filtros(nav)
            dados = []

            try:
                # Espera as linhas da tabela aparecerem antes de navegar
                WebDriverWait(nav, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar"))
                )
                time.sleep(2)
                navegar_para_pagina(nav, pagina_atual)

                # Espera o overlay j_id18 sumir antes de clicar
                WebDriverWait(nav, 60).until(
                    EC.invisibility_of_element_located((By.ID, "j_id18"))
                )

                # Rebusca as linhas após navegar para garantir que estão frescas
                linhas_nav = WebDriverWait(nav, 60).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar"))
                )
                linhas_nav = sorted(linhas_nav, key=lambda el: el.location['y'])
                nav.execute_script("arguments[0].click();", linhas_nav[indice])
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
                        print("     Nenhuma tabela encontrada, tentando novamente...")
                    else:
                        print(f"     {len(tbodys_check)} tabela(s) já visível(is), capturando dados...")
                        time.sleep(3)

                # Captura o número do processo
                site_processo = BeautifulSoup(nav.page_source, 'html.parser')
                span_processo = site_processo.find("span", class_="visual_numero_viproc_coep")
                numero_processo = span_processo.get_text(strip=True) if span_processo else ""
                print(f"     Nº do Processo: {numero_processo}")

                # Captura a data de início (remove a hora)
                span_data = site_processo.find("span", class_="visual_inicio_acolhimento_propostas_coep")
                data_inicio = span_data.get_text(strip=True).split(" ")[0] if span_data else ""
                print(f"     Data início: {data_inicio}")

                # Scraping dos itens
                dados = scraping_licitacao(nav, numero_processo, data_inicio)
                dados_totais.extend(dados)
                dados_pagina.extend(dados)
                print(f"     {len(dados)} itens coletados.")

            except Exception as e:
                print(f"     Erro na licitação {indice + 1}, tentando novamente: {e}")

            finally:
                nav.quit()

            if dados:
                break  # conseguiu — sai do while

    # ─── EXPORTAR PÁGINA ATUAL ───────────────────────────────────────────────
    if dados_pagina:
        nome_arquivo = f"licitacoes_pag{pagina_atual}.xlsx"
        df = pd.DataFrame(dados_pagina, columns=[
            "numero_processo", "data_inicio", "item", "descricao", "fornecedor", "quantidade",
            "valor_unitario", "valor_total", "melhor_lance",
            "total_melhor_lance", "marca"
        ])
        df.to_excel(nome_arquivo, index=False)
        print(f"  → Página {pagina_atual} salva: {len(dados_pagina)} registros em {nome_arquivo}")
    else:
        print(f"  → Página {pagina_atual}: nenhum dado coletado.")

# ─── EXPORTAR EXCEL CONSOLIDADO ──────────────────────────────────────────────
if dados_totais:
    nome_arquivo = f"licitacoes_pag{pagina_inicio}_ate_{pagina_fim}.xlsx"
    df = pd.DataFrame(dados_totais, columns=[
        "numero_processo", "data_inicio", "item", "descricao", "fornecedor", "quantidade",
        "valor_unitario", "valor_total", "melhor_lance",
        "total_melhor_lance", "marca"
    ])
    df.to_excel(nome_arquivo, index=False)
    print(f"\nConcluído! {len(dados_totais)} registros salvos em {nome_arquivo}")
else:
    print("\nNenhum dado coletado.")

fim = datetime.now()
duracao = fim - inicio
horas, resto = divmod(int(duracao.total_seconds()), 3600)
minutos, segundos = divmod(resto, 60)
print(f"\nInício:   {inicio.strftime('%d/%m/%Y %H:%M:%S')}")
print(f"Fim:      {fim.strftime('%d/%m/%Y %H:%M:%S')}")
print(f"Duração:  {horas:02d}h {minutos:02d}min {segundos:02d}s")
