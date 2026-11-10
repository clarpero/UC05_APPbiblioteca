import sqlite3
from pathlib import Path
from seguranca import gerar_hash

ARQUIVO_BANCO = Path(__file__).with_name("livros.db")
ESQUEMA = Path(__file__).with_name("schema.sql")


def conectar():
    conn = sqlite3.connect(ARQUIVO_BANCO)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrar_livro(conn)
    conn.executescript(ESQUEMA.read_text(encoding="utf-8"))
    criar_admin(conn)
    return conn


def migrar_livro(conn):
    """Bancos antigos não têm a coluna quantidade: acrescenta sem perder os livros."""
    colunas = [c["name"] for c in conn.execute("PRAGMA table_info(livro)")]
    if colunas and "quantidade" not in colunas:
        with conn:
            conn.execute(
                "ALTER TABLE livro ADD COLUMN "
                "quantidade INTEGER NOT NULL DEFAULT 1 CHECK (quantidade >= 0)"
            )


def criar_admin(conn):
    """Conta padrão para teste: login admin, senha admin."""
    if conn.execute("SELECT 1 FROM acesso WHERE login = 'admin'").fetchone() is None:
        senha_hash, sal = gerar_hash("admin")
        with conn:
            conn.execute(
                "INSERT INTO acesso (login, senha_hash, sal) VALUES ('admin', ?, ?)",
                (senha_hash, sal),
            )

def inserir_livro(conn, titulo, autor, ano, isbn):
    with conn:
        cursor = conn.execute(
            "INSERT INTO livro (titulo, autor, ano, isbn) VALUES (?, ?, ?, ?)",
            (titulo, autor, ano, isbn),
        )
    return cursor.lastrowid


def listar_livros(conn):
    return conn.execute(
        "SELECT id, titulo, autor, ano, isbn FROM livro ORDER BY id"
    ).fetchall()

def pesquisar_livros(conn, termo):
    padrao = f"%{termo}%"
    return conn.execute(
        "SELECT id, titulo, autor, ano, isbn FROM livro "
        "WHERE titulo LIKE ? OR autor LIKE ? ORDER BY id",
        (padrao, padrao),
    ).fetchall()


def obter_livro(conn, livro_id):
    return conn.execute(
        "SELECT id, titulo, autor, ano, isbn FROM livro WHERE id = ?", (livro_id,)
    ).fetchone()

def excluir_livro(conn, livro_id):
    with conn:
        conn.execute("DELETE FROM livro WHERE id = ?", (livro_id,))

def atualizar_livro(conn, livro_id, titulo, autor, ano, isbn):
    with conn:
        conn.execute(
            "UPDATE livro SET titulo = ?, autor = ?, ano = ?, isbn = ? WHERE id = ?",
            (titulo, autor, ano, isbn, livro_id),
        )

def buscar_acesso(conn, login):
    return conn.execute(
        "SELECT login, senha_hash, sal FROM acesso WHERE login = ?", (login,)
    ).fetchone()

# ---------- usuários e funcionários ----------

TABELAS_PESSOA = ("usuario", "funcionario")  # só estes nomes podem entrar no SQL


def _tabela(tabela):
    if tabela not in TABELAS_PESSOA:
        raise ValueError(f"Tabela desconhecida: {tabela}")
    return tabela


def listar_pessoas(conn, tabela, termo=""):
    """Pesquisa por parte do nome ou do CPF."""
    padrao = f"%{termo.strip()}%"
    digitos = "".join(c for c in termo if c.isdigit())
    return conn.execute(
        f"SELECT * FROM {_tabela(tabela)} "
        "WHERE nome LIKE ? OR (? <> '' AND cpf LIKE ?) ORDER BY nome",
        (padrao, digitos, f"%{digitos}%"),
    ).fetchall()


def obter_pessoa(conn, tabela, pessoa_id):
    return conn.execute(
        f"SELECT * FROM {_tabela(tabela)} WHERE id = ?", (pessoa_id,)
    ).fetchone()


def cpf_em_uso(conn, tabela, cpf, ignorar_id=None):
    """True se outra pessoa da mesma tabela já tem este CPF."""
    linha = conn.execute(
        f"SELECT id FROM {_tabela(tabela)} WHERE cpf = ?", (cpf,)
    ).fetchone()
    return linha is not None and linha["id"] != ignorar_id


def inserir_usuario(conn, dados):
    with conn:
        return conn.execute(
            "INSERT INTO usuario (nome, cpf, email, endereco, data_nascimento) "
            "VALUES (:nome, :cpf, :email, :endereco, :data_nascimento)",
            dados,
        ).lastrowid


def inserir_funcionario(conn, dados, codigo_base):
    """Grava o funcionário e devolve o código. Se o código já existir, acrescenta -2, -3..."""
    codigo, numero = codigo_base, 1
    while conn.execute("SELECT 1 FROM funcionario WHERE codigo = ?", (codigo,)).fetchone():
        numero += 1
        codigo = f"{codigo_base}-{numero}"
    with conn:
        conn.execute(
            "INSERT INTO funcionario (codigo, nome, cpf, email, endereco, data_nascimento) "
            "VALUES (:codigo, :nome, :cpf, :email, :endereco, :data_nascimento)",
            {**dados, "codigo": codigo},
        )
    return codigo


def atualizar_pessoa(conn, tabela, pessoa_id, dados):
    with conn:
        conn.execute(
            f"UPDATE {_tabela(tabela)} SET nome = :nome, cpf = :cpf, email = :email, "
            "endereco = :endereco, data_nascimento = :data_nascimento WHERE id = :id",
            {**dados, "id": pessoa_id},
        )


def definir_ativo(conn, tabela, pessoa_id, ativo):
    with conn:
        conn.execute(
            f"UPDATE {_tabela(tabela)} SET ativo = ? WHERE id = ?", (int(ativo), pessoa_id)
        )

def buscar_funcionario_por_codigo(conn, codigo):
    return conn.execute(
        "SELECT id, codigo, nome, ativo FROM funcionario WHERE codigo = ?",
        (codigo.strip().upper(),),
    ).fetchone()