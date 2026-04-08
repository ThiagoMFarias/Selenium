-- ============================================================
--  Schema: Licitações
--  Banco:  PostgreSQL
--  Obs:    Campos opcionais recebem NULL por padrão
-- ============================================================

-- Extensão para UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------
-- Tabela: fornecedor
-- ------------------------------------------------------------
CREATE TABLE fornecedor (
    id          UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    nome        VARCHAR(255)  NOT NULL,
    cnpj        VARCHAR(18)   NULL UNIQUE,
    criado_em   TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Tabela: item
-- ------------------------------------------------------------
CREATE TABLE item (
    id          UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_item   VARCHAR(255)  NULL,
    descricao   TEXT          NULL,
    marca       VARCHAR(255)  NULL,
    criado_em   TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Tabela: processo
-- ------------------------------------------------------------
CREATE TABLE processo (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_processo  VARCHAR(100) NOT NULL UNIQUE,
    data_inicio      DATE         NULL,
    criado_em        TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Tabela: processo_item
-- Relaciona quais itens fazem parte de cada processo
-- e define a quantidade licitada
-- ------------------------------------------------------------
CREATE TABLE processo_item (
    id           UUID     PRIMARY KEY DEFAULT gen_random_uuid(),
    processo_id  UUID     NOT NULL REFERENCES processo(id)  ON DELETE CASCADE,
    item_id      UUID     NOT NULL REFERENCES item(id)      ON DELETE RESTRICT,
    quantidade   INTEGER  NULL,

    UNIQUE (processo_id, item_id)
);

-- ------------------------------------------------------------
-- Tabela: lance
-- Registra as propostas de cada fornecedor por item do processo
-- O campo vencedor = TRUE indica o fornecedor que arrematou
-- aquele item específico (pode haver um vencedor diferente
-- por item dentro do mesmo processo)
-- ------------------------------------------------------------
CREATE TABLE lance (
    id                UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    processo_item_id  UUID           NOT NULL REFERENCES processo_item(id) ON DELETE CASCADE,
    fornecedor_id     UUID           NOT NULL REFERENCES fornecedor(id)    ON DELETE RESTRICT,
    valor_unitario    NUMERIC(15,2)  NULL,
    valor_total       NUMERIC(15,2)  NULL,
    melhor_lance      NUMERIC(15,2)  NULL,
    total_melhor_lance NUMERIC(15,2) NULL,
    vencedor          BOOLEAN        NOT NULL DEFAULT FALSE,
    criado_em         TIMESTAMP      NOT NULL DEFAULT NOW(),

    UNIQUE (processo_item_id, fornecedor_id)
);

-- ------------------------------------------------------------
-- Índices para performance nas junções mais comuns
-- ------------------------------------------------------------
CREATE INDEX idx_processo_item_processo  ON processo_item (processo_id);
CREATE INDEX idx_processo_item_item      ON processo_item (item_id);
CREATE INDEX idx_lance_processo_item     ON lance (processo_item_id);
CREATE INDEX idx_lance_fornecedor        ON lance (fornecedor_id);
CREATE INDEX idx_lance_vencedor          ON lance (vencedor) WHERE vencedor = TRUE;

-- ------------------------------------------------------------
-- View auxiliar: resultado completo de uma licitação
-- Une todos os dados relevantes em uma única consulta
-- ------------------------------------------------------------
CREATE VIEW vw_resultado_licitacao AS
SELECT
    p.numero_processo,
    p.data_inicio,
    i.nome_item,
    i.descricao,
    i.marca,
    pi.quantidade,
    f.nome                    AS fornecedor,
    l.valor_unitario,
    l.valor_total,
    l.melhor_lance,
    l.total_melhor_lance,
    l.vencedor
FROM processo         p
JOIN processo_item    pi ON pi.processo_id   = p.id
JOIN item             i  ON i.id             = pi.item_id
JOIN lance            l  ON l.processo_item_id = pi.id
JOIN fornecedor       f  ON f.id             = l.fornecedor_id
ORDER BY
    p.numero_processo,
    i.nome_item,
    l.vencedor DESC;