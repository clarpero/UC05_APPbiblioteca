"""Cadastro de usuários e funcionários. A mesma tela serve para os dois."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

import banco
from validacao import (
    ErroValidacao,
    formatar_data,
    gerar_codigo_funcionario,
    mascarar_cpf,
    validar_pessoa,
)

# O que muda entre as duas telas fica aqui; o resto do código é o mesmo.
TIPOS = {
    "usuario": {
        "titulo": "Usuários",
        "obrigatorios": set(),
        "coluna_id": ("ID", "id"),
    },
    "funcionario": {
        "titulo": "Funcionários",
        "obrigatorios": {"endereco", "data_nascimento"},
        "coluna_id": ("Código", "codigo"),
    },
}


class DialogoPessoas(QDialog):
    def __init__(self, conn, tipo, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.tipo = tipo
        self.config = TIPOS[tipo]
        self.selecionado = None  # pessoa clicada na tabela (ou None)
        self.setWindowTitle(self.config["titulo"])
        self.resize(860, 540)

        layout = QHBoxLayout(self)
        layout.addLayout(self.montar_formulario(), 1)
        layout.addLayout(self.montar_lista(), 2)
        self.conectar_eventos()
        self.atualizar_lista()

    # ---------- montagem ----------

    def montar_formulario(self):
        obrigatorios = self.config["obrigatorios"]
        self.campos = {
            "nome": QLineEdit(),
            "cpf": QLineEdit(),
            "email": QLineEdit(),
            "endereco": QLineEdit(),
            "data_nascimento": QLineEdit(),
        }
        self.campos["cpf"].setMaxLength(14)
        self.campos["cpf"].setPlaceholderText("Somente números")
        self.campos["email"].setPlaceholderText("nome@dominio.com")
        self.campos["data_nascimento"].setMaxLength(10)
        self.campos["data_nascimento"].setPlaceholderText("dd/mm/aaaa")

        def rotulo(texto, campo):
            return texto + (" *" if campo in obrigatorios else "")

        formulario = QFormLayout()
        formulario.addRow("Nome *", self.campos["nome"])
        formulario.addRow("CPF *", self.campos["cpf"])
        formulario.addRow("E-mail *", self.campos["email"])
        formulario.addRow(rotulo("Endereço", "endereco"), self.campos["endereco"])
        formulario.addRow(rotulo("Nascimento", "data_nascimento"), self.campos["data_nascimento"])

        self.botao_cadastrar = QPushButton("Cadastrar")
        self.botao_cadastrar.setProperty("variante", "primario")
        self.botao_atualizar = QPushButton("Atualizar")
        self.botao_ativo = QPushButton("Desativar")
        self.botao_limpar = QPushButton("Limpar")
        self.botao_atualizar.setEnabled(False)
        self.botao_ativo.setEnabled(False)

        botoes = QHBoxLayout()
        for botao in (self.botao_cadastrar, self.botao_atualizar, self.botao_ativo):
            botoes.addWidget(botao)
        botoes.addStretch()
        botoes.addWidget(self.botao_limpar)

        titulo = QLabel(f"Cadastro de {self.config['titulo'].lower()}")
        titulo.setObjectName("titulo_pagina")
        coluna = QVBoxLayout()
        coluna.addWidget(titulo)
        coluna.addLayout(formulario)
        coluna.addLayout(botoes)
        coluna.addWidget(QLabel("* campo obrigatório"))
        coluna.addStretch()
        return coluna

    def montar_lista(self):
        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText("Pesquisar por nome ou CPF")

        rotulo_id, _ = self.config["coluna_id"]
        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels([rotulo_id, "Nome", "CPF", "E-mail", "Situação"])
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setAlternatingRowColors(True)
        cabecalho = self.tabela.horizontalHeader()
        cabecalho.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        cabecalho.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        cabecalho.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        coluna = QVBoxLayout()
        coluna.addWidget(self.campo_pesquisa)
        coluna.addWidget(self.tabela)
        return coluna

    def conectar_eventos(self):
        self.botao_cadastrar.clicked.connect(self.cadastrar)
        self.botao_atualizar.clicked.connect(self.atualizar)
        self.botao_ativo.clicked.connect(self.alternar_ativo)
        self.botao_limpar.clicked.connect(self.limpar)
        self.campo_pesquisa.textChanged.connect(self.atualizar_lista)
        self.tabela.itemSelectionChanged.connect(self.selecionar)

    # ---------- lista ----------

    def atualizar_lista(self):
        _, chave_id = self.config["coluna_id"]
        pessoas = banco.listar_pessoas(self.conn, self.tipo, self.campo_pesquisa.text())
        self.tabela.setRowCount(len(pessoas))
        for linha, pessoa in enumerate(pessoas):
            valores = [
                pessoa[chave_id], pessoa["nome"], mascarar_cpf(pessoa["cpf"]),
                pessoa["email"], "Ativo" if pessoa["ativo"] else "Inativo",
            ]
            for coluna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setData(Qt.ItemDataRole.UserRole, pessoa["id"])  # id escondido na célula
                self.tabela.setItem(linha, coluna, item)
        self.tabela.clearSelection()

    def selecionar(self):
        linhas = self.tabela.selectionModel().selectedRows()
        if not linhas:
            self.limpar()
            return
        pessoa_id = self.tabela.item(linhas[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        pessoa = banco.obter_pessoa(self.conn, self.tipo, pessoa_id)
        self.selecionado = pessoa
        self.campos["nome"].setText(pessoa["nome"])
        self.campos["cpf"].setText(pessoa["cpf"])
        self.campos["email"].setText(pessoa["email"])
        self.campos["endereco"].setText(pessoa["endereco"] or "")
        self.campos["data_nascimento"].setText(formatar_data(pessoa["data_nascimento"]))
        self.botao_cadastrar.setEnabled(False)
        self.botao_atualizar.setEnabled(True)
        self.botao_ativo.setEnabled(True)
        self.botao_ativo.setText("Desativar" if pessoa["ativo"] else "Reativar")

    # ---------- ações ----------

    def ler_formulario(self):
        """Valida os campos. Devolve os dados prontos, ou None se algo estiver errado."""
        try:
            return validar_pessoa(
                self.campos["nome"].text(),
                self.campos["cpf"].text(),
                self.campos["email"].text(),
                self.campos["endereco"].text(),
                self.campos["data_nascimento"].text(),
                self.config["obrigatorios"],
            )
        except ErroValidacao as erro:
            QMessageBox.warning(self, self.config["titulo"], str(erro))
            self.campos[erro.campo].setFocus()
            return None

    def cadastrar(self):
        dados = self.ler_formulario()
        if dados is None:
            return
        if banco.cpf_em_uso(self.conn, self.tipo, dados["cpf"]):
            QMessageBox.warning(self, self.config["titulo"], "Já existe um cadastro com este CPF.")
            self.campos["cpf"].setFocus()
            return

        if self.tipo == "funcionario":
            base = gerar_codigo_funcionario(dados["nome"], dados["cpf"])
            codigo = banco.inserir_funcionario(self.conn, dados, base)
            QMessageBox.information(
                self, "Funcionários", f"Funcionário cadastrado.\nCódigo: {codigo}"
            )
        else:
            banco.inserir_usuario(self.conn, dados)
        self.limpar()
        self.atualizar_lista()

    def atualizar(self):
        pessoa = self.selecionado
        dados = self.ler_formulario()
        if pessoa is None or dados is None:
            return
        if banco.cpf_em_uso(self.conn, self.tipo, dados["cpf"], ignorar_id=pessoa["id"]):
            QMessageBox.warning(self, self.config["titulo"], "Já existe um cadastro com este CPF.")
            return
        banco.atualizar_pessoa(self.conn, self.tipo, pessoa["id"], dados)
        self.limpar()
        self.atualizar_lista()

    def alternar_ativo(self):
        pessoa = self.selecionado
        if pessoa is None:
            return
        banco.definir_ativo(self.conn, self.tipo, pessoa["id"], not pessoa["ativo"])
        self.limpar()
        self.atualizar_lista()

    def limpar(self):
        self.selecionado = None
        for campo in self.campos.values():
            campo.clear()
        self.botao_cadastrar.setEnabled(True)
        self.botao_atualizar.setEnabled(False)
        self.botao_ativo.setEnabled(False)
        self.botao_ativo.setText("Desativar")
        self.tabela.clearSelection()
        self.campos["nome"].setFocus()