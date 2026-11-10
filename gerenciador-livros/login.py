"""Tela de login: pede usuário e senha antes de abrir o programa."""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

import banco
from seguranca import conferir_senha

MAXIMO_TENTATIVAS = 5


class DialogoLogin(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Entrar")
        self.setMinimumWidth(340)
        self.tentativas = 0
        self.login = None  # preenchido quando o login dá certo

        titulo = QLabel("Gerenciador de Livros")
        titulo.setObjectName("titulo_pagina")
        self.campo_login = QLineEdit()
        self.campo_senha = QLineEdit()
        self.campo_senha.setEchoMode(QLineEdit.EchoMode.Password)  # mostra ••••
        self.mensagem = QLabel("Informe seu usuário e senha.")

        formulario = QFormLayout()
        formulario.addRow("&Usuário:", self.campo_login)
        formulario.addRow("&Senha:", self.campo_senha)

        botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botoes.button(QDialogButtonBox.StandardButton.Ok).setText("Entrar")
        botoes.accepted.connect(self.entrar)
        botoes.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addLayout(formulario)
        layout.addWidget(self.mensagem)
        layout.addWidget(botoes)

    def entrar(self):
        login = self.campo_login.text().strip()
        senha = self.campo_senha.text()
        if not login or not senha:
            self.mensagem.setText("Preencha o usuário e a senha.")
            return

        conn = banco.conectar()
        try:
            conta = banco.buscar_acesso(conn, login)
        finally:
            conn.close()

        if conta is None or not conferir_senha(senha, conta["senha_hash"], conta["sal"]):
            self.tentativas += 1
            if self.tentativas >= MAXIMO_TENTATIVAS:
                self.reject()  # muitas tentativas: o programa não abre
                return
            restantes = MAXIMO_TENTATIVAS - self.tentativas
            self.mensagem.setText(f"Usuário ou senha incorretos. Tentativas restantes: {restantes}.")
            self.campo_senha.clear()
            self.campo_senha.setFocus()
            return

        self.login = login
        self.accept()