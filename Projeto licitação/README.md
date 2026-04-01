# 📊 Projeto de Web Scraping para Análise de Licitações

## 🎯 Objetivo
Desenvolver um projeto de **web scraping** para coletar dados do site oficial da SEFAZ-CE:  
https://s2gpr.sefaz.ce.gov.br/licita-web/paginas/licita/PublicacaoList.seam  

O objetivo é estruturar essas informações e transformá-las em um **dashboard interativo**, capaz de fornecer insights relevantes e apoiar a tomada de decisões em futuras buscas por orçamentos de materiais.

## ⚙️ Descrição do Projeto
O projeto consiste em:

- Extração automatizada de dados de licitações públicas;
- Tratamento e organização das informações coletadas;
- Armazenamento estruturado dos dados;
- Criação de visualizações analíticas por meio de um dashboard.

## 📈 Resultados Esperados
Com a implementação do projeto, espera-se:

- Maior agilidade na análise de preços e fornecedores;
- Identificação de padrões e tendências em licitações;
- Apoio estratégico na tomada de decisões para aquisição de materiais;
- Redução de retrabalho em pesquisas manuais.

## 🛠️ Tecnologias Sugeridas
- **Python** (Selenium, BeautifulSoup, Pandas)
- **Banco de Dados** (PostgreSQL)
- **Ferramentas de Visualização** (Dash/Streamlit)

## 🚀 Benefícios
- Automação de processos repetitivos;
- Base de dados confiável e atualizada;
- Melhor embasamento para decisões administrativas e financeiras.

## 🧭 Etapas do Desenvolvimento do Projeto

A seguir estão os principais passos e desafios enfrentados durante a execução do projeto de web scraping:

### 1️⃣ Dificuldade na Navegação entre Licitações
Inicialmente, houve dificuldade na extração dos dados ao tentar abrir cada licitação individualmente e navegar entre as páginas.  
Observou-se que o **CID das licitações permanecia inalterado**, mesmo ao acessar diferentes registros, inviabilizando a identificação única de cada item.

### 2️⃣ Estratégia de Abertura de Novas Páginas
Diante desse problema, foi necessário adotar uma nova abordagem:  
- A cada leitura de licitação, uma **nova página era aberta**;
- Nessa nova instância, todos os filtros eram reaplicados.

Essa solução resolveu a limitação anterior, porém **aumentou significativamente o tempo de captura dos dados**.

### 3️⃣ Bloqueio por Detecção de Automação
Durante a execução do scraping, o site passou a identificar a automação, resultando em:
- Bloqueio de acesso;
- Retorno de erro **403 (Forbidden)**.

### 4️⃣ Implementação de Delay Randômico
Para contornar a detecção, foi implementado um mecanismo de:
- **Tempo de espera aleatório (random delay)** entre as requisições;

O objetivo foi simular um comportamento mais próximo ao de um usuário humano.

### 5️⃣ Estratégia de Persistência e Recuperação
Mesmo com as tentativas de mitigação, o erro persistiu em alguns momentos.  
Assim, foi implementada uma estratégia de segurança:

- Ao finalizar o scraping de cada página:
  - Os dados são **salvos imediatamente** para evitar perdas;
- Em caso de erro:
  - O processo pode ser retomado **a partir da última página com falha**;
- Em caso de execução sem erros:
  - Todos os dados são consolidados em **um único arquivo final**.

---
📌 Essa abordagem garantiu maior robustez e confiabilidade ao processo de coleta de dados.