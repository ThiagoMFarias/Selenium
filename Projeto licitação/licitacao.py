from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import time


def iniciar_navegador():
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    navegador = webdriver.Chrome(options=options)
    navegador.get("http://s2gpr.sefaz.ce.gov.br/licita-web/paginas/licita/PublicacaoList.seam")
    navegador.maximize_window()
    return navegador


def aplicar_filtros(nav):
    # Trata aviso de conexão não segura se aparecer
    try:
        botao_ir = WebDriverWait(nav, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Ir para o site') or contains(text(),'Proceed') or contains(text(),'Continue')]"))
        )
        botao_ir.click()
        time.sleep(2)
    except:
        pass

    # Natureza da Aquisição
    natureza = WebDriverWait(nav, 60).until(
        EC.presence_of_element_located((By.ID, "formularioDeCrud:naturezaAquisicaoDecoration:naturezaAquisicao"))
    )
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


def paginas_visiveis(nav):
    """Retorna lista de números de páginas visíveis na paginação superior."""
    site = BeautifulSoup(nav.page_source, 'html.parser')
    paginador = site.find("div", id="formularioDeCrud:datascrollerSuperior")
    if not paginador:
        return []
    tds = paginador.find_all("td", class_=lambda c: c and ("rich-datascr-inact" in c or "rich-datascr-act" in c))
    numeros = []
    for td in tds:
        try:
            numeros.append(int(td.get_text(strip=True)))
        except:
            pass
    return numeros


def navegar_para_pagina(nav, numero_pagina):
    """Navega clicando no maior número visível da paginação
    até a página desejada aparecer e então clica direto nela."""
    if numero_pagina == 1:
        return

    esperar_paginacao(nav)

    while True:
        numeros = paginas_visiveis(nav)
        print(f"     Navegando para página {numero_pagina} — visível mais próxima: {max(numeros) if numeros else '?'}")

        # Página desejada está visível — clica direto nela
        if numero_pagina in numeros:
            if pagina_atual_numero(nav) == numero_pagina:
                return
            botao = nav.find_element(
                By.XPATH, f"//td[contains(@class,'rich-datascr-inact') and text()='{numero_pagina}']"
            )
            nav.execute_script("window.scrollTo(0, 0);")
            nav.execute_script("arguments[0].click();", botao)
            WebDriverWait(nav, 120).until(
                lambda d: pagina_atual_numero(d) == numero_pagina
            )
            return

        # Página desejada não está visível — clica no maior número visível
        maximo_visivel = max(numeros) if numeros else 0
        if maximo_visivel == 0:
            raise Exception("Nenhum número visível na paginação.")

        print(f"     Clicando no maior visível: {maximo_visivel}")
        botao_maximo = nav.find_element(
            By.XPATH, f"//td[contains(@class,'rich-datascr-inact') and text()='{maximo_visivel}']"
        )
        nav.execute_script("window.scrollTo(0, 0);")
        nav.execute_script("arguments[0].click();", botao_maximo)
        time.sleep(3)
        WebDriverWait(nav, 120).until(
            lambda d: pagina_atual_numero(d) == maximo_visivel
        )


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
esperar_paginacao(nav_validacao)
time.sleep(2)

print(f"Verificando se página {pagina_fim} existe...")
if not pagina_existe(nav_validacao, pagina_fim):
    print(f"Página {pagina_fim} não existe. Verifique o intervalo e tente novamente.")
    nav_validacao.quit()
    exit()

nav_validacao.quit()
print(f"Intervalo válido! Rodando da página {pagina_inicio} até {pagina_fim}...")

# ─── LOOP PRINCIPAL ──────────────────────────────────────────────────────────

dados_totais = []
contador_licitacoes = 0  # contador global de licitações lidas

for pagina_atual in range(pagina_inicio, pagina_fim + 1):
    print(f"\n=== Processando página {pagina_atual}/{pagina_fim} ===")
    dados_pagina = []
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
            break
        except Exception as e:
            print(f"     Erro ao navegar para página {pagina_atual}, tentando novamente: {e}")
        finally:
            nav_pagina.quit()

    for indice in range(total_linhas):
        print(f"  → Abrindo licitação {indice + 1}/{total_linhas} da página {pagina_atual}...")

        # Pequena pausa aleatória entre licitações para parecer mais humano
        import random
        time.sleep(random.uniform(1.5, 4.0))

        while True:
            nav = iniciar_navegador()
            aplicar_filtros(nav)
            dados = []

            try:
                WebDriverWait(nav, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tr.linhaImpar, tr.linhaPar"))
                )
                time.sleep(2)
                navegar_para_pagina(nav, pagina_atual)

                # Verifica se caiu na página de debug
                if "debug.seam" in nav.current_url:
                    print("     Página de debug detectada, aguardando 60s...")
                    time.sleep(60)
                    raise Exception("Página de debug do servidor.")

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

                # Verifica debug após clicar na licitação
                if "debug.seam" in nav.current_url:
                    print("     Página de debug detectada, aguardando 60s...")
                    time.sleep(60)
                    raise Exception("Página de debug do servidor.")

                # Visualizar proposta
                visu_proposta = WebDriverWait(nav, 20).until(
                    EC.element_to_be_clickable((By.ID, "formularioDeCrud:visualizarSuperior"))
                )
                visu_proposta.click()
                time.sleep(3)

                # Verifica debug após visualizar proposta
                if "debug.seam" in nav.current_url:
                    print("     Página de debug detectada, aguardando 60s...")
                    time.sleep(60)
                    raise Exception("Página de debug do servidor.")

                # Tentar expandir itens
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
                contador_licitacoes += 1
                # Pausa aleatória a cada 6 licitações lidas
                if contador_licitacoes % 6 == 0:
                    import random
                    pausa = random.randint(180, 300)
                    minutos = pausa // 60
                    segundos = pausa % 60
                    print(f"\n  ⏸ Pausa de {minutos}min {segundos}s após {contador_licitacoes} licitações lidas...")
                    time.sleep(pausa)
                    print("  ▶ Retomando...\n")
                break

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
