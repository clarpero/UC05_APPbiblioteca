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

# Livro junto com quantos exemplares estão livres (vem da visão disponibilidade).
SELECT_LIVRO = (
    "SELECT l.id, l.titulo, l.autor, l.ano, l.isbn, l.quantidade, d.disponiveis "
    "FROM livro l JOIN disponibilidade d ON d.livro_id = l.id "
)


def inserir_livro(conn, titulo, autor, ano, isbn, quantidade):
    with conn:
        cursor = conn.execute(
            "INSERT INTO livro (titulo, autor, ano, isbn, quantidade) VALUES (?, ?, ?, ?, ?)",
            (titulo, autor, ano, isbn, quantidade),
        )
    return cursor.lastrowid


def listar_livros(conn):
    return conn.execute(SELECT_LIVRO + "ORDER BY l.id").fetchall()


def pesquisar_livros(conn, termo):
    padrao = f"%{termo}%"
    return conn.execute(
        SELECT_LIVRO + "WHERE l.titulo LIKE ? OR l.autor LIKE ? ORDER BY l.id",
        (padrao, padrao),
    ).fetchall()


def obter_livro(conn, livro_id):
    return conn.execute(SELECT_LIVRO + "WHERE l.id = ?", (livro_id,)).fetchone()


def excluir_livro(conn, livro_id):
    with conn:
        conn.execute("DELETE FROM livro WHERE id = ?", (livro_id,))


def atualizar_livro(conn, livro_id, titulo, autor, ano, isbn, quantidade):
    with conn:
        conn.execute(
            "UPDATE livro SET titulo = ?, autor = ?, ano = ?, isbn = ?, quantidade = ? "
            "WHERE id = ?",
            (titulo, autor, ano, isbn, quantidade, livro_id),
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

# ---------- reservas ----------

def expirar_reservas(conn, momento):
    """Reservas ativas com prazo vencido viram 'expirada' e liberam os exemplares."""
    with conn:
        conn.execute(
            "UPDATE reserva SET situacao = 'expirada' "
            "WHERE situacao = 'ativa' AND retirar_ate < ?",
            (momento,),
        )


def livros_ocupados_do_usuario(conn, usuario_id):
    """Quantos livros o usuário tem agora: em uso + em reservas ativas."""
    return conn.execute(
        """
        SELECT (SELECT COUNT(*) FROM livro_em_uso
                 WHERE usuario_id = :usuario AND fim IS NULL)
             + (SELECT COUNT(*) FROM livro_reservado lr
                  JOIN reserva r ON r.id = lr.reserva_id
                 WHERE r.usuario_id = :usuario AND r.situacao = 'ativa')
        """,
        {"usuario": usuario_id},
    ).fetchone()[0]


def usuario_ja_tem_livro(conn, usuario_id, livro_id):
    """True se o livro já está com o usuário ou numa reserva ativa dele."""
    return conn.execute(
        """
        SELECT EXISTS (SELECT 1 FROM livro_em_uso
                        WHERE usuario_id = :usuario AND livro_id = :livro AND fim IS NULL)
            OR EXISTS (SELECT 1 FROM livro_reservado lr
                         JOIN reserva r ON r.id = lr.reserva_id
                        WHERE r.usuario_id = :usuario AND lr.livro_id = :livro
                          AND r.situacao = 'ativa')
        """,
        {"usuario": usuario_id, "livro": livro_id},
    ).fetchone()[0] == 1


def inserir_reserva(conn, usuario_id, funcionario_id, criada_em, retirar_ate, livros_ids):
    """Grava a reserva e os livros dela. Sem commit: quem chama controla a transação."""
    reserva_id = conn.execute(
        "INSERT INTO reserva (usuario_id, funcionario_id, criada_em, retirar_ate) "
        "VALUES (?, ?, ?, ?)",
        (usuario_id, funcionario_id, criada_em, retirar_ate),
    ).lastrowid
    conn.executemany(
        "INSERT INTO livro_reservado (reserva_id, livro_id) VALUES (?, ?)",
        [(reserva_id, livro_id) for livro_id in livros_ids],
    )
    return reserva_id


def listar_reservas(conn, so_ativas=True):
    filtro = "WHERE r.situacao = 'ativa' " if so_ativas else ""
    return conn.execute(
        "SELECT r.id, u.nome AS usuario, r.retirar_ate, r.situacao, "
        "       GROUP_CONCAT(l.titulo, '; ') AS livros "
        "  FROM reserva r "
        "  JOIN usuario u          ON u.id = r.usuario_id "
        "  JOIN livro_reservado lr ON lr.reserva_id = r.id "
        "  JOIN livro l            ON l.id = lr.livro_id "
        + filtro +
        "GROUP BY r.id ORDER BY r.retirar_ate"
    ).fetchall()


def obter_reserva(conn, reserva_id):
    return conn.execute("SELECT * FROM reserva WHERE id = ?", (reserva_id,)).fetchone()


def mudar_situacao_reserva(conn, reserva_id, situacao):
    with conn:
        conn.execute("UPDATE reserva SET situacao = ? WHERE id = ?", (situacao, reserva_id))


# ---------- livros em uso ----------

def livros_da_reserva(conn, reserva_id):
    linhas = conn.execute(
        "SELECT livro_id FROM livro_reservado WHERE reserva_id = ?", (reserva_id,)
    ).fetchall()
    return [linha["livro_id"] for linha in linhas]


def concluir_reserva(conn, reserva_id):
    """Sem commit: faz parte da transação da retirada."""
    conn.execute("UPDATE reserva SET situacao = 'concluida' WHERE id = ?", (reserva_id,))


def inserir_uso(conn, usuario_id, livro_id, funcionario_id, tipo, inicio, devolver_ate,
                reserva_id=None):
    """Sem commit: quem chama controla a transação."""
    return conn.execute(
        "INSERT INTO livro_em_uso "
        "(usuario_id, livro_id, funcionario_id, reserva_id, tipo, inicio, devolver_ate) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (usuario_id, livro_id, funcionario_id, reserva_id, tipo, inicio, devolver_ate),
    ).lastrowid


def listar_usos(conn, so_abertos=True):
    filtro = "WHERE e.fim IS NULL " if so_abertos else ""
    return conn.execute(
        "SELECT e.id, u.nome AS usuario, l.titulo AS livro, e.tipo, "
        "       e.inicio, e.devolver_ate, e.fim "
        "  FROM livro_em_uso e "
        "  JOIN usuario u ON u.id = e.usuario_id "
        "  JOIN livro l   ON l.id = e.livro_id "
        + filtro +
        "ORDER BY e.fim IS NOT NULL, e.inicio DESC"
    ).fetchall()


def obter_uso(conn, uso_id):
    return conn.execute("SELECT * FROM livro_em_uso WHERE id = ?", (uso_id,)).fetchone()


def encerrar_uso(conn, uso_id, fim):
    with conn:
        conn.execute("UPDATE livro_em_uso SET fim = ? WHERE id = ?", (fim, uso_id))
