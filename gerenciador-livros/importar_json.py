"""Importa pessoas de um arquivo JSON (gerador de pessoas do 4devs) para o banco.

Uso, na pasta do projeto:
    python importar_json.py pessoas.json               -> cadastra como usuários
    python importar_json.py pessoas.json funcionario   -> cadastra como funcionários
"""

import json
import sys

import banco
from validacao import ErroValidacao, gerar_codigo_funcionario, validar_pessoa

OBRIGATORIOS = {"usuario": set(), "funcionario": {"endereco", "data_nascimento"}}


def montar_endereco(pessoa):
    """Junta rua, número, bairro, cidade e estado num texto só."""
    rua = f"{pessoa.get('endereco', '')}, {pessoa.get('numero', '')}".strip(", ")
    cidade = f"{pessoa.get('cidade', '')}/{pessoa.get('estado', '')}".strip("/")
    partes = [rua, pessoa.get("bairro", ""), cidade]
    return " - ".join(parte for parte in partes if parte)


def importar(caminho, tipo):
    with open(caminho, encoding="utf-8") as arquivo:
        pessoas = json.load(arquivo)
    if isinstance(pessoas, dict):
        pessoas = [pessoas]  # o 4devs gera um objeto só quando a quantidade é 1

    conn = banco.conectar()
    gravados = 0
    for pessoa in pessoas:
        nome = pessoa.get("nome", "")
        try:
            dados = validar_pessoa(
                nome,
                pessoa.get("cpf", ""),
                pessoa.get("email", ""),
                montar_endereco(pessoa),
                pessoa.get("data_nasc", ""),
                OBRIGATORIOS[tipo],
            )
        except ErroValidacao as erro:
            print(f"PULADO  {nome}: {erro}")
            continue
        if banco.cpf_em_uso(conn, tipo, dados["cpf"]):
            print(f"PULADO  {nome}: CPF já cadastrado.")
            continue

        if tipo == "funcionario":
            base = gerar_codigo_funcionario(dados["nome"], dados["cpf"])
            codigo = banco.inserir_funcionario(conn, dados, base)
            print(f"OK      {dados['nome']} (código {codigo})")
        else:
            banco.inserir_usuario(conn, dados)
            print(f"OK      {dados['nome']}")
        gravados += 1

    conn.close()
    print(f"\n{gravados} de {len(pessoas)} pessoa(s) importada(s) como {tipo}.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tipo = sys.argv[2] if len(sys.argv) > 2 else "usuario"
    if tipo not in OBRIGATORIOS:
        sys.exit('O tipo deve ser "usuario" ou "funcionario".')
    importar(sys.argv[1], tipo)