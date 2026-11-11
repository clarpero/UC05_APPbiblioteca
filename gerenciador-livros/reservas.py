"""Tela de reservas: funcionário + usuário (nome ou CPF) + livros marcados."""

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

import banco
import servicos
from validacao import ErroValidacao, mascarar_cpf


def data_hora(texto):
    """'2026-11-12 17:30:00' -> '12/11/2026 17:30'"""
    return datetime.fromisoformat(texto).strftime("%d/%m/%Y %H:%M")


class DialogoReservas(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Reservas")
        self.resize(1000, 580)

        layout = QHBoxLayout(self)
        layout.addLayout(self.montar_formulario(), 1)
        layout.addLayout(self.montar_lista(), 1)
        self.conectar_eventos()

        servicos.expirar_reservas(conn)
        self.carregar_livros()
        self.atualizar_lista()

    # ---------- montagem ----------

    def montar_formulario(self):
        self.campo_codigo = QLineEdit()
        self.campo_codigo.setPlaceholderText("Ex.: CAPR30")
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Digite o nome ou o CPF")
        self.combo_usuario = QComboBox()
        self.combo_usuario.addItem("Nenhum usuário encontrado", None)
        self.campo_livro = QLineEdit()
        self.campo_livro.setPlaceholderText("Filtrar por título ou autor")
        self.lista_livros = QListWidget()
        self.botao_reservar = QPushButton("Reservar")
        self.botao_reservar.setProperty("variante", "primario")

        formulario = QFormLayout()
        formulario.addRow("Funcionário *", self.campo_codigo)
        formulario.addRow("Usuário *", self.campo_usuario)
        formulario.addRow("", self.combo_usuario)

        titulo = QLabel("Nova reserva")
        titulo.setObjectName("titulo_pagina")
        coluna = QVBoxLayout()
        coluna.addWidget(titulo)
        coluna.addLayout(formulario)
        coluna.addWidget(QLabel(
            f"Livros disponíveis (até {servicos.LIMITE_LIVROS_POR_USUARIO} por usuário):"
        ))
        coluna.addWidget(self.campo_livro)
        coluna.addWidget(self.lista_livros)
        coluna.addWidget(self.botao_reservar)
        return coluna

    def montar_lista(self):
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItem("Somente ativas", True)
        self.combo_filtro.addItem("Todas", False)

        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(["Nº", "Usuário", "Livros", "Retirar até", "Situação"])
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setAlternatingRowColors(True)
        cabecalho = self.tabela.horizontalHeader()
        cabecalho.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        cabecalho.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.botao_retirar = QPushButton("Retirar reserva selecionada")
        self.botao_retirar.setProperty("variante", "primario")
        self.botao_cancelar = QPushButton("Cancelar reserva selecionada")

        titulo = QLabel("Reservas")
        titulo.setObjectName("titulo_pagina")
        coluna = QVBoxLayout()
        coluna.addWidget(titulo)
        coluna.addWidget(self.combo_filtro)
        coluna.addWidget(self.tabela)
        coluna.addWidget(self.botao_retirar)
        coluna.addWidget(self.botao_cancelar)
        return coluna

    def conectar_eventos(self):
        self.campo_usuario.textChanged.connect(self.buscar_usuarios)
        self.campo_livro.textChanged.connect(self.filtrar_livros)
        self.botao_reservar.clicked.connect(self.reservar)
        self.combo_filtro.currentIndexChanged.connect(self.atualizar_lista)
        self.botao_retirar.clicked.connect(self.retirar)
        self.botao_cancelar.clicked.connect(self.cancelar)

    # ---------- formulário ----------

    def buscar_usuarios(self):
        termo = self.campo_usuario.text().strip()
        self.combo_usuario.clear()
        encontrados = [
            u for u in banco.listar_pessoas(self.conn, "usuario", termo) if u["ativo"]
        ] if termo else []
        if not encontrados:
            self.combo_usuario.addItem("Nenhum usuário encontrado", None)
        for usuario in encontrados:
            self.combo_usuario.addItem(
                f"{usuario['nome']} (CPF {mascarar_cpf(usuario['cpf'])})", usuario["id"]
            )

    def carregar_livros(self):
        self.lista_livros.clear()
        for livro in banco.listar_livros(self.conn):
            if livro["disponiveis"] < 1:
                continue  # livro esgotado não aparece para reservar
            item = QListWidgetItem(
                f"{livro['titulo']} — {livro['autor']} ({livro['disponiveis']} disponível(is))"
            )
            item.setData(Qt.ItemDataRole.UserRole, livro["id"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lista_livros.addItem(item)
        self.filtrar_livros()

    def filtrar_livros(self):
        termo = self.campo_livro.text().strip().lower()
        for i in range(self.lista_livros.count()):
            item = self.lista_livros.item(i)
            item.setHidden(termo not in item.text().lower())

    def livros_marcados(self):
        marcados = []
        for i in range(self.lista_livros.count()):
            item = self.lista_livros.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                marcados.append(item.data(Qt.ItemDataRole.UserRole))
        return marcados

    def avisar(self, erro):
        QMessageBox.warning(self, "Reservas", str(erro))
        campos = {
            "codigo": self.campo_codigo,
            "usuario": self.campo_usuario,
            "livros": self.lista_livros,
            "lista": self.tabela,
        }
        campos[erro.campo].setFocus()

    def reservar(self):
        try:
            reserva_id, prazo = servicos.criar_reserva(
                self.conn,
                self.campo_codigo.text(),
                self.combo_usuario.currentData(),
                self.livros_marcados(),
            )
        except ErroValidacao as erro:
            self.avisar(erro)
            return
        QMessageBox.information(
            self, "Reservas",
            f"Reserva nº {reserva_id} criada.\nRetirar até {prazo.strftime('%d/%m/%Y %H:%M')}.",
        )
        self.campo_usuario.clear()  # o código do funcionário fica, para a próxima reserva
        self.campo_livro.clear()
        self.carregar_livros()
        self.atualizar_lista()

    # ---------- lista ----------

    def atualizar_lista(self):
        reservas = banco.listar_reservas(self.conn, self.combo_filtro.currentData())
        self.tabela.setRowCount(len(reservas))
        for linha, reserva in enumerate(reservas):
            valores = [reserva["id"], reserva["usuario"], reserva["livros"],
                       data_hora(reserva["retirar_ate"]), reserva["situacao"]]
            for coluna, valor in enumerate(valores):
                self.tabela.setItem(linha, coluna, QTableWidgetItem(str(valor)))
        self.tabela.clearSelection()

    def reserva_selecionada(self):
        """Devolve o número da reserva marcada na tabela, ou None."""
        linhas = self.tabela.selectionModel().selectedRows()
        if not linhas:
            QMessageBox.information(self, "Reservas", "Selecione uma reserva na lista.")
            return None
        return int(self.tabela.item(linhas[0].row(), 0).text())

    def retirar(self):
        reserva_id = self.reserva_selecionada()
        if reserva_id is None:
            return
        try:
            prazo = servicos.retirar_reserva(self.conn, self.campo_codigo.text(), reserva_id)
        except ErroValidacao as erro:
            self.avisar(erro)
            return
        QMessageBox.information(
            self, "Reservas",
            f"Reserva nº {reserva_id} retirada.\nDevolver até {prazo.strftime('%d/%m/%Y')}.",
        )
        self.carregar_livros()
        self.atualizar_lista()

    def cancelar(self):
        reserva_id = self.reserva_selecionada()
        if reserva_id is None:
            return
        try:
            servicos.cancelar_reserva(self.conn, self.campo_codigo.text(), reserva_id)
        except ErroValidacao as erro:
            self.avisar(erro)
            return
        QMessageBox.information(self, "Reservas", f"Reserva nº {reserva_id} cancelada.")
        self.carregar_livros()
        self.atualizar_lista()
