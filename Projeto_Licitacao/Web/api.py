from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
import os
import hashlib
import jwt
import datetime

app = FastAPI(title="Licitações SEFAZ-CE API", version="1.0.0")

# ─── CORS — permite o HTML acessar a API ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, coloque só o domínio do seu site
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── CONFIGURAÇÕES ────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-trocar-em-producao")

USUARIOS = {
    "admin":  hashlib.sha256("senha123".encode()).hexdigest(),
    "thiago": hashlib.sha256("licitacao2025".encode()).hexdigest(),
}

# ─── CONEXÃO COM O BANCO ──────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 6543),
        sslmode="require",
        options="-c search_path=public",
        cursor_factory=psycopg2.extras.RealDictCursor
    )

# ─── AUTENTICAÇÃO JWT ─────────────────────────────────────────────────────────
security = HTTPBearer()

def criar_token(usuario: str) -> str:
    payload = {
        "sub": usuario,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# ─── MODELS ───────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    usuario: str
    senha: str

class ProcessoCreate(BaseModel):
    numero_processo: str
    data_inicio: str

class ItemUpdate(BaseModel):
    nome_item: str
    descricao: str = None
    marca: str = None

class FornecedorCreate(BaseModel):
    nome: str
    cnpj: str = None

# ─── ENDPOINTS DE AUTENTICAÇÃO ────────────────────────────────────────────────

@app.post("/login")
def login(dados: LoginRequest):
    """Autentica o usuário e retorna um token JWT."""
    hash_senha = hashlib.sha256(dados.senha.encode()).hexdigest()
    if dados.usuario in USUARIOS and USUARIOS[dados.usuario] == hash_senha:
        token = criar_token(dados.usuario)
        return {"ok": True, "token": token, "usuario": dados.usuario}
    raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

# ─── ENDPOINTS DO DASHBOARD ───────────────────────────────────────────────────

@app.get("/stats")
def stats(usuario: str = Depends(verificar_token)):
    """Retorna os totais gerais para os cards do dashboard."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM processo")
    processos = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM fornecedor")
    fornecedores = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM item")
    itens = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM lance")
    lances = cur.fetchone()["total"]
    cur.execute("SELECT COALESCE(SUM(total_melhor_lance), 0) AS total FROM lance WHERE vencedor = true")
    valor = cur.fetchone()["total"]
    cur.close()
    conn.close()
    return {
        "processos": processos,
        "fornecedores": fornecedores,
        "itens": itens,
        "lances": lances,
        "valor_homologado": float(valor)
    }

@app.get("/dashboard/top-itens")
def top_itens(usuario: str = Depends(verificar_token)):
    """Top 10 itens mais comprados por quantidade."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.nome_item, SUM(pi.quantidade) AS total
        FROM processo_item pi
        JOIN item i ON i.id = pi.item_id
        GROUP BY i.nome_item
        ORDER BY total DESC
        LIMIT 10
    """)
    dados = cur.fetchall()
    cur.close(); conn.close()
    return list(dados)

@app.get("/dashboard/top-fornecedores")
def top_fornecedores(usuario: str = Depends(verificar_token)):
    """Top 10 fornecedores por valor total ganho."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.nome, SUM(l.total_melhor_lance) AS valor
        FROM lance l
        JOIN fornecedor f ON f.id = l.fornecedor_id
        WHERE l.vencedor = true
        GROUP BY f.nome
        ORDER BY valor DESC
        LIMIT 10
    """)
    dados = cur.fetchall()
    cur.close(); conn.close()
    return list(dados)

@app.get("/dashboard/evolucao")
def evolucao(usuario: str = Depends(verificar_token)):
    """Evolução de valores estimado x homologado ao longo do tempo."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.data_inicio,
               SUM(l.valor_total) AS estimado,
               SUM(l.total_melhor_lance) AS homologado
        FROM lance l
        JOIN processo_item pi ON pi.id = l.processo_item_id
        JOIN processo p ON p.id = pi.processo_id
        WHERE l.vencedor = true
        GROUP BY p.data_inicio
        ORDER BY p.data_inicio
    """)
    dados = cur.fetchall()
    cur.close(); conn.close()
    return [{"data": str(r["data_inicio"]), "estimado": float(r["estimado"] or 0),
             "homologado": float(r["homologado"] or 0)} for r in dados]

# ─── ENDPOINTS DE BUSCA ───────────────────────────────────────────────────────

@app.get("/buscar")
def buscar(
    termo: str,
    fornecedor: str = None,
    apenas_vencedores: bool = True,
    usuario: str = Depends(verificar_token)
):
    """Busca itens por nome com filtros opcionais."""
    conn = get_conn()
    cur = conn.cursor()
    sql = """
        SELECT
            p.numero_processo,
            p.data_inicio::text AS data_inicio,
            i.nome_item,
            f.nome AS fornecedor,
            pi.quantidade,
            l.valor_unitario,
            l.valor_total,
            l.melhor_lance,
            l.total_melhor_lance,
            l.vencedor,
            ROUND(
                (1 - l.total_melhor_lance / NULLIF(l.valor_total, 0)) * 100, 2
            ) AS reducao_pct,
            i.marca
        FROM lance l
        JOIN processo_item pi ON pi.id = l.processo_item_id
        JOIN processo p ON p.id = pi.processo_id
        JOIN item i ON i.id = pi.item_id
        JOIN fornecedor f ON f.id = l.fornecedor_id
        WHERE i.nome_item ILIKE %s
    """
    params = [f"%{termo}%"]
    if fornecedor:
        sql += " AND f.nome = %s"
        params.append(fornecedor)
    if apenas_vencedores:
        sql += " AND l.vencedor = true"
    sql += " ORDER BY p.data_inicio DESC"
    cur.execute(sql, params)
    dados = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in dados]

# ─── ENDPOINTS DE RANKINGS ────────────────────────────────────────────────────

@app.get("/ranking/produtos")
def ranking_produtos(usuario: str = Depends(verificar_token)):
    """Ranking de produtos mais comprados com estatísticas de preço."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.nome_item,
            COUNT(*) AS ocorrencias,
            SUM(pi.quantidade) AS quantidade_total,
            ROUND(AVG(l.melhor_lance)::numeric, 2) AS media_lance,
            MIN(l.melhor_lance) AS menor_lance,
            MAX(l.melhor_lance) AS maior_lance,
            ROUND(AVG(
                (1 - l.total_melhor_lance / NULLIF(l.valor_total,0)) * 100
            )::numeric, 2) AS reducao_media_pct
        FROM lance l
        JOIN processo_item pi ON pi.id = l.processo_item_id
        JOIN item i ON i.id = pi.item_id
        WHERE l.vencedor = true AND i.nome_item IS NOT NULL
        GROUP BY i.nome_item
        ORDER BY quantidade_total DESC
    """)
    dados = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in dados]

@app.get("/ranking/fornecedores")
def ranking_fornecedores(usuario: str = Depends(verificar_token)):
    """Ranking de fornecedores por valor total ganho."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.nome AS fornecedor, f.cnpj,
            COUNT(DISTINCT pi.processo_id) AS total_processos,
            COUNT(l.id) AS total_itens_ganhos,
            SUM(l.total_melhor_lance) AS valor_total_ganho,
            ROUND(AVG(
                (1 - l.total_melhor_lance / NULLIF(l.valor_total,0)) * 100
            )::numeric, 2) AS reducao_media_pct
        FROM lance l
        JOIN fornecedor f ON f.id = l.fornecedor_id
        JOIN processo_item pi ON pi.id = l.processo_item_id
        WHERE l.vencedor = true
        GROUP BY f.nome, f.cnpj
        ORDER BY valor_total_ganho DESC NULLS LAST
    """)
    dados = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in dados]

@app.get("/ranking/processos")
def ranking_processos(usuario: str = Depends(verificar_token)):
    """Resumo por processo com percentual de economia."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.numero_processo,
            p.data_inicio::text AS data_inicio,
            COUNT(DISTINCT l.fornecedor_id) AS fornecedores,
            COUNT(pi.id) AS total_itens,
            ROUND(SUM(l.valor_total)::numeric, 2) AS valor_estimado,
            ROUND(SUM(l.total_melhor_lance)::numeric, 2) AS valor_homologado,
            ROUND((1 - SUM(l.total_melhor_lance) /
                NULLIF(SUM(l.valor_total),0)) * 100, 2) AS economia_pct
        FROM processo p
        JOIN processo_item pi ON pi.processo_id = p.id
        JOIN lance l ON l.processo_item_id = pi.id
        WHERE l.vencedor = true
        GROUP BY p.numero_processo, p.data_inicio
        ORDER BY p.data_inicio DESC
    """)
    dados = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in dados]

# ─── CRUD PROCESSOS ───────────────────────────────────────────────────────────

@app.get("/processos")
def listar_processos(usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id::text, numero_processo, data_inicio::text, criado_em::text FROM processo ORDER BY data_inicio DESC")
    dados = cur.fetchall(); cur.close(); conn.close()
    return [dict(r) for r in dados]

@app.post("/processos")
def criar_processo(dados: ProcessoCreate, usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO processo (numero_processo, data_inicio) VALUES (%s, %s) RETURNING id::text",
                (dados.numero_processo, dados.data_inicio))
    novo_id = cur.fetchone()["id"]
    conn.commit(); cur.close(); conn.close()
    return {"ok": True, "id": novo_id}

@app.put("/processos/{id}")
def atualizar_processo(id: str, dados: ProcessoCreate, usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE processo SET numero_processo=%s, data_inicio=%s WHERE id=%s::uuid",
                (dados.numero_processo, dados.data_inicio, id))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

@app.delete("/processos/{id}")
def excluir_processo(id: str, usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM processo WHERE id=%s::uuid", (id,))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

# ─── CRUD ITENS ───────────────────────────────────────────────────────────────

@app.get("/itens")
def listar_itens(usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id::text, nome_item, descricao, marca FROM item ORDER BY nome_item")
    dados = cur.fetchall(); cur.close(); conn.close()
    return [dict(r) for r in dados]

@app.put("/itens/{id}")
def atualizar_item(id: str, dados: ItemUpdate, usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE item SET nome_item=%s, descricao=%s, marca=%s WHERE id=%s::uuid",
                (dados.nome_item, dados.descricao, dados.marca, id))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

@app.delete("/itens/{id}")
def excluir_item(id: str, usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM item WHERE id=%s::uuid", (id,))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

# ─── CRUD FORNECEDORES ────────────────────────────────────────────────────────

@app.get("/fornecedores")
def listar_fornecedores(usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id::text, nome, cnpj FROM fornecedor ORDER BY nome")
    dados = cur.fetchall(); cur.close(); conn.close()
    return [dict(r) for r in dados]

@app.post("/fornecedores")
def criar_fornecedor(dados: FornecedorCreate, usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO fornecedor (nome, cnpj) VALUES (%s, %s) RETURNING id::text",
                (dados.nome, dados.cnpj))
    novo_id = cur.fetchone()["id"]
    conn.commit(); cur.close(); conn.close()
    return {"ok": True, "id": novo_id}

@app.put("/fornecedores/{id}")
def atualizar_fornecedor(id: str, dados: FornecedorCreate, usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE fornecedor SET nome=%s, cnpj=%s WHERE id=%s::uuid",
                (dados.nome, dados.cnpj, id))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

@app.delete("/fornecedores/{id}")
def excluir_fornecedor(id: str, usuario: str = Depends(verificar_token)):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM fornecedor WHERE id=%s::uuid", (id,))
    conn.commit(); cur.close(); conn.close()
    return {"ok": True}

# ─── RODAR LOCALMENTE ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)