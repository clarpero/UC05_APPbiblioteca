"""Senhas guardadas com segurança: só o resumo (hash) com sal, nunca a senha."""

import hashlib
import hmac
import secrets

ITERACOES = 200_000  # quanto mais voltas, mais lento fica para quem tenta adivinhar


def resumir(senha, sal):
    resumo = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(sal), ITERACOES)
    return resumo.hex()


def gerar_hash(senha):
    sal = secrets.token_hex(16)  # 16 bytes aleatórios, diferentes para cada senha
    return resumir(senha, sal), sal


def conferir_senha(senha, senha_hash, sal):
    return hmac.compare_digest(resumir(senha, sal), senha_hash)