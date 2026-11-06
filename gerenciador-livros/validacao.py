"""Regras de validação do livro. Funções puras: não dependem da tela nem do banco."""


class ErroValidacao(Exception):
    """Dado digitado que não segue as regras. Guarda qual campo tem o problema."""

    def __init__(self, campo, mensagem):
        super().__init__(mensagem)
        self.campo = campo


def validar_livro(titulo, autor, ano, isbn):
    """Confere as regras do livro e devolve os dados prontos para gravar."""
    titulo = titulo.strip()
    autor = autor.strip()
    ano = ano.strip()
    isbn = isbn.strip()

    if not titulo:
        raise ErroValidacao("titulo", "Preencha o título do livro.")
    if not autor:
        raise ErroValidacao("autor", "Preencha o autor do livro.")
    if ano and not ano.isdigit():
        raise ErroValidacao("ano", "O ano deve ter só números, por exemplo 2016.")

    return {
        "titulo": titulo,
        "autor": autor,
        "ano": int(ano) if ano else None,
        "isbn": isbn,
    }