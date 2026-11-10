-- Gerenciador de Livros: esquema do banco SQLite.
-- As regras importantes também ficam no banco: a tela valida antes,
-- e o banco recusa o que escapar.

CREATE TABLE IF NOT EXISTS livro (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo      TEXT    NOT NULL CHECK (length(trim(titulo)) > 0),
    autor       TEXT    NOT NULL CHECK (length(trim(autor)) > 0),
    ano         INTEGER,
    isbn        TEXT,
    quantidade  INTEGER NOT NULL DEFAULT 1 CHECK (quantidade >= 0)  -- exemplares
);

CREATE TABLE IF NOT EXISTS usuario (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    nome             TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    cpf              TEXT NOT NULL UNIQUE CHECK (length(cpf) = 11),  -- só dígitos
    email            TEXT NOT NULL CHECK (email LIKE '%_@_%'),
    endereco         TEXT,                                           -- opcional
    data_nascimento  TEXT,                                           -- opcional, AAAA-MM-DD
    ativo            INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS funcionario (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo           TEXT NOT NULL UNIQUE,                           -- ex.: CAPR30
    nome             TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    cpf              TEXT NOT NULL UNIQUE CHECK (length(cpf) = 11),
    email            TEXT NOT NULL CHECK (email LIKE '%_@_%'),
    endereco         TEXT NOT NULL,
    data_nascimento  TEXT NOT NULL,                                  -- AAAA-MM-DD
    ativo            INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS reserva (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id      INTEGER NOT NULL REFERENCES usuario (id)     ON DELETE RESTRICT,
    funcionario_id  INTEGER NOT NULL REFERENCES funcionario (id) ON DELETE RESTRICT,
    criada_em       TEXT    NOT NULL,                            -- AAAA-MM-DD HH:MM:SS
    retirar_ate     TEXT    NOT NULL,                            -- prazo para retirar
    situacao        TEXT    NOT NULL DEFAULT 'ativa'
                    CHECK (situacao IN ('ativa', 'concluida', 'cancelada', 'expirada')),
    CHECK (retirar_ate >= criada_em)
);

CREATE TABLE IF NOT EXISTS livro_reservado (
    reserva_id  INTEGER NOT NULL REFERENCES reserva (id) ON DELETE CASCADE,
    livro_id    INTEGER NOT NULL REFERENCES livro (id)   ON DELETE RESTRICT,
    PRIMARY KEY (reserva_id, livro_id)  -- o mesmo livro não entra duas vezes na reserva
);

CREATE TABLE IF NOT EXISTS livro_em_uso (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id      INTEGER NOT NULL REFERENCES usuario (id)     ON DELETE RESTRICT,
    livro_id        INTEGER NOT NULL REFERENCES livro (id)       ON DELETE RESTRICT,
    funcionario_id  INTEGER NOT NULL REFERENCES funcionario (id) ON DELETE RESTRICT,
    reserva_id      INTEGER REFERENCES reserva (id)              ON DELETE RESTRICT,  -- opcional
    tipo            TEXT    NOT NULL CHECK (tipo IN ('local', 'retirada')),
    inicio          TEXT    NOT NULL,
    devolver_ate    TEXT,                -- só existe na retirada
    fim             TEXT,                -- vazio (NULL) = livro ainda em uso
    CHECK (fim IS NULL OR fim >= inicio),
    CHECK ((tipo = 'retirada') = (devolver_ate IS NOT NULL))
);

-- Um usuário não pode estar com o mesmo livro duas vezes ao mesmo tempo.
CREATE UNIQUE INDEX IF NOT EXISTS ux_uso_aberto
    ON livro_em_uso (usuario_id, livro_id) WHERE fim IS NULL;

-- Login do sistema. A senha nunca é guardada: só o resumo (hash) com sal.
CREATE TABLE IF NOT EXISTS acesso (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    login       TEXT NOT NULL UNIQUE,
    senha_hash  TEXT NOT NULL,
    sal         TEXT NOT NULL
);

-- Quantos exemplares de cada livro estão livres agora.
CREATE VIEW IF NOT EXISTS disponibilidade AS
SELECT l.id AS livro_id,
       l.quantidade
       - (SELECT COUNT(*) FROM livro_em_uso u
           WHERE u.livro_id = l.id AND u.fim IS NULL)
       - (SELECT COUNT(*) FROM livro_reservado lr
            JOIN reserva r ON r.id = lr.reserva_id
           WHERE lr.livro_id = l.id AND r.situacao = 'ativa') AS disponiveis
  FROM livro l;