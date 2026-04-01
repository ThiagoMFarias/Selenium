##  Repositórios Relacionados à Biblioteca Selenium

Esta seção reúne repositórios que utilizam ou estão relacionados à biblioteca **Selenium**, amplamente empregada para automação de navegadores e projetos de web scraping.

### Conteúdo dos Repositórios
- Exemplos de automação de testes web;
- Scripts de web scraping com Selenium;
- Integrações com outras bibliotecas (BeautifulSoup, Pandas, etc.);
- Boas práticas e padrões de automação;
- Projetos completos utilizando Selenium em diferentes contextos.

### Tecnologias Envolvidas
- Python
- Selenium WebDriver
- BeautifulSoup
- Pandas
- Frameworks de testes (não implementado ainda)

### Objetivo
Facilitar o acesso a implementações práticas e servir como base de estudo ou reaproveitamento em projetos que envolvam automação e coleta de dados na web.

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