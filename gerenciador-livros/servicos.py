"""Regras de reserva. Valem para qualquer tela: a janela só pede e mostra."""

from datetime import datetime, timedelta

import banco
from validacao import ErroValidacao

PRAZO_RESERVA_DIAS = 2         # tempo para retirar os livros reservados
LIMITE_LIVROS_POR_USUARIO = 3  # em uso + reservados, ao mesmo tempo


def agora():
    return datetime.now().replace(microsecond=0)


def texto(momento):
    """datetime -> '2026-11-10 17:30:00', o formato guardado no banco."""
    return momento.isoformat(sep=" ")


def expirar_reservas(conn):
    banco.expirar_reservas(conn, texto(agora()))


def exigir_funcionario(conn, codigo):
    funcionario = banco.buscar_funcionario_por_codigo(conn, codigo)
    if funcionario is None or not funcionario["ativo"]:
        raise ErroValidacao("codigo", "Código de funcionário inválido ou inativo.")
    return funcionario


def criar_reserva(conn, codigo_funcionario, usuario_id, livros_ids):
    """Reserva os livros para o usuário. Tudo numa transação: ou grava tudo, ou nada."""
    funcionario = exigir_funcionario(conn, codigo_funcionario)
    usuario = banco.obter_pessoa(conn, "usuario", usuario_id) if usuario_id else None
    if usuario is None or not usuario["ativo"]:
        raise ErroValidacao("usuario", "Escolha um usuário ativo.")
    if not livros_ids:
        raise ErroValidacao("livros", "Marque pelo menos um livro.")

    momento = agora()
    expirar_reservas(conn)
    with conn:
        ocupados = banco.livros_ocupados_do_usuario(conn, usuario_id)
        if ocupados + len(livros_ids) > LIMITE_LIVROS_POR_USUARIO:
            raise ErroValidacao(
                "livros",
                f"{usuario['nome']} já tem {ocupados} livro(s) em uso ou reservado(s). "
                f"O limite é {LIMITE_LIVROS_POR_USUARIO}.",
            )
        for livro_id in livros_ids:
            livro = banco.obter_livro(conn, livro_id)
            if banco.usuario_ja_tem_livro(conn, usuario_id, livro_id):
                raise ErroValidacao("livros", f'{usuario["nome"]} já está com "{livro["titulo"]}".')
            if livro["disponiveis"] < 1:
                raise ErroValidacao("livros", f'"{livro["titulo"]}" não tem exemplar disponível.')
        prazo = momento + timedelta(days=PRAZO_RESERVA_DIAS)
        reserva_id = banco.inserir_reserva(
            conn, usuario_id, funcionario["id"], texto(momento), texto(prazo), livros_ids
        )
    return reserva_id, prazo


def cancelar_reserva(conn, codigo_funcionario, reserva_id):
    exigir_funcionario(conn, codigo_funcionario)
    reserva = banco.obter_reserva(conn, reserva_id)
    if reserva is None or reserva["situacao"] != "ativa":
        raise ErroValidacao("lista", "Só reservas ativas podem ser canceladas.")
    banco.mudar_situacao_reserva(conn, reserva_id, "cancelada")
