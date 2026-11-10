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