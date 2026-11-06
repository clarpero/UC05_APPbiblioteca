import sqlite3
from pathlib import Path

ARQUIVO_BANCO = Path(__file__).with_name("livros.db")


def conectar():
    conn = sqlite3.connect(ARQUIVO_BANCO)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS livro (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL CHECK (length(trim(titulo)) > 0),
            autor  TEXT NOT NULL CHECK (length(trim(autor)) > 0),
            ano    INTEGER,
            isbn   TEXT
        )
        """
    )
    return conn

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