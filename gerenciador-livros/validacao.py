"""Regras de validação do livro. Funções puras: não dependem da tela nem do banco."""

import re
import unicodedata
from datetime import date, datetime

class ErroValidacao(Exception):
    """Dado digitado que não segue as regras. Guarda qual campo tem o problema."""

    def __init__(self, campo, mensagem):
        super().__init__(mensagem)
        self.campo = campo


def validar_livro(titulo, autor, ano, isbn, quantidade=1):
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
    if quantidade < 1:
        raise ErroValidacao("quantidade", "O livro precisa de pelo menos 1 exemplar.")

    return {
        "titulo": titulo,
        "autor": autor,
        "ano": int(ano) if ano else None,
        "isbn": isbn,
        "quantidade": quantidade,
    }

PARTICULAS = {"de", "da", "do", "das", "dos", "e"}  # não entram no código
def gerar_codigo_funcionario(nome, cpf):
    """Iniciais de cada nome + 2 últimos dígitos do CPF: Claudio de Araujo Pereira Rodrigues -> CAPR30."""
    sem_acento = unicodedata.normalize("NFKD", nome)
    sem_acento = "".join(letra for letra in sem_acento if not unicodedata.combining(letra))
    iniciais = "".join(
        parte[0] for parte in sem_acento.split() if parte.lower() not in PARTICULAS
    )
    digitos = "".join(c for c in cpf if c.isdigit())
    return iniciais.upper() + digitos[-2:]


# ---------- usuários e funcionários ----------

def normalizar_cpf(valor):
    """Deixa só os dígitos: '529.982.247-25' -> '52998224725'."""
    return re.sub(r"\D", "", valor or "")


def cpf_valido(valor):
    """Confere os dois dígitos verificadores do CPF."""
    d = normalizar_cpf(valor)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for posicao in (9, 10):
        soma = sum(int(d[i]) * (posicao + 1 - i) for i in range(posicao))
        if (soma * 10) % 11 % 10 != int(d[posicao]):
            return False
    return True


def mascarar_cpf(valor):
    """Mostra só o final do CPF na tela: ***.***.247-25

    Os 2 últimos dígitos já aparecem no código do funcionário. Mostrar o miolo
    junto deixaria só 3 dígitos escondidos, fáceis de descobrir.
    """
    d = normalizar_cpf(valor)
    return f"***.***.{d[6:9]}-{d[9:]}" if len(d) == 11 else "***"


def converter_data(texto):
    """'25/12/1990' -> '1990-12-25' (formato do banco). Vazio -> None."""
    texto = texto.strip()
    if not texto:
        return None
    return datetime.strptime(texto, "%d/%m/%Y").date().isoformat()


def formatar_data(iso):
    """'1990-12-25' -> '25/12/1990' (formato da tela). None -> ''."""
    if not iso:
        return ""
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")


def validar_pessoa(nome, cpf, email, endereco, nascimento, obrigatorios=()):
    """Regras comuns de usuário e funcionário. Devolve os dados prontos para gravar."""
    dados = {
        "nome": " ".join(nome.split()),
        "cpf": normalizar_cpf(cpf),
        "email": email.strip().lower(),
        "endereco": " ".join(endereco.split()) or None,
        "data_nascimento": None,
    }
    if not dados["nome"]:
        raise ErroValidacao("nome", "Preencha o nome.")
    if not cpf_valido(dados["cpf"]):
        raise ErroValidacao("cpf", "CPF inválido. Confira os 11 dígitos.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", dados["email"]):
        raise ErroValidacao("email", "E-mail inválido. Exemplo: nome@dominio.com")
    if "endereco" in obrigatorios and not dados["endereco"]:
        raise ErroValidacao("endereco", "Preencha o endereço.")
    try:
        dados["data_nascimento"] = converter_data(nascimento)
    except ValueError:
        raise ErroValidacao("data_nascimento", "Data inválida. Use dd/mm/aaaa.") from None
    if dados["data_nascimento"] is None and "data_nascimento" in obrigatorios:
        raise ErroValidacao("data_nascimento", "Preencha a data de nascimento.")
    if dados["data_nascimento"] and dados["data_nascimento"] > date.today().isoformat():
        raise ErroValidacao("data_nascimento", "A data de nascimento não pode estar no futuro.")
    return dados
