# Licitações API

Este projeto é uma API para pesquisa de licitações, permitindo que os usuários busquem licitações onde a "Natureza da aquisição" seja "material de consumo".

## Estrutura do Projeto

O projeto possui a seguinte estrutura de diretórios:

```
licitacoes-api
├── src
│   ├── main.py                  # Ponto de entrada da aplicação
│   ├── controllers              # Controladores da API
│   │   └── licitacoes_controller.py  # Controlador para manipulação de licitações
│   ├── models                   # Modelos de dados
│   │   └── licitacao.py         # Modelo de dados de uma licitação
│   ├── routes                   # Rotas da API
│   │   └── licitacoes_routes.py  # Configuração das rotas
│   └── types                    # Tipos e interfaces
│       └── index.py             # Tipos utilizados na aplicação
├── requirements.txt             # Dependências do projeto
└── README.md                    # Documentação do projeto
```

## Como Executar

1. Clone o repositório:
   ```
   git clone <URL_DO_REPOSITORIO>
   cd licitacoes-api
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```
   python src/main.py
   ```

A API estará disponível em `http://localhost:5000`.

## Endpoints

- `GET /licitacoes`: Busca licitações com a "Natureza da aquisição" igual a "material de consumo".

## Contribuição

Sinta-se à vontade para contribuir com melhorias ou correções. Crie um fork do repositório, faça suas alterações e envie um pull request.