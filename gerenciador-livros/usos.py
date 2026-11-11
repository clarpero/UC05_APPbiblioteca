"""Tela de livros em uso: entregar (ler no local ou retirar) e devolver."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
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
    QWidget,
)

import banco
import servicos
import tema
from reservas import data_hora
from validacao import ErroValidacao, mascarar_cpf

NOMES_TIPO = {"local": "No local", "retirada": "Retirada"}


class PaginasUsos(QWidget):
    """Este widget é a página esquerda (formulário); pagina_direita é a lista."""

    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn

        self.setLayout(self.montar_formulario())
        self.pagina_direita = QWidget()
        self.pagina_direita.setLayout(self.montar_lista())
        for layout in (self.layout(), self.pagina_direita.layout()):
            layout.setContentsMargins(0, 0, 0, 0)  # a margem já é a da página do livro
        self.conectar_eventos()
        self.ao_mostrar()

    def ao_mostrar(self):
        """Chamado quando o livro vira para esta tela."""
        servicos.expirar_reservas(self.conn)
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
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Ler no local", "local")
        self.combo_tipo.addItem(
            f"Retirar (devolver em {servicos.PRAZO_RETIRADA_DIAS} dias)", "retirada"
        )
        self.campo_livro = QLineEdit()
        self.campo_livro.setPlaceholderText("Filtrar por título ou autor")
        self.lista_livros = QListWidget()
        self.botao_entregar = QPushButton("Entregar")
        self.botao_entregar.setProperty("variante", "primario")

        formulario = QFormLayout()
        formulario.addRow("Funcionário *", self.campo_codigo)
        formulario.addRow("Usuário *", self.campo_usuario)
        formulario.addRow("", self.combo_usuario)
        formulario.addRow("Tipo *", self.combo_tipo)

        titulo = QLabel("Entregar livro")
        titulo.setObjectName("titulo_pagina")
        coluna = QVBoxLayout()
        coluna.addWidget(titulo)
        coluna.addLayout(formulario)
        coluna.addWidget(QLabel(
            f"Livros disponíveis (até {servicos.LIMITE_LIVROS_POR_USUARIO} por usuário):"
        ))
        coluna.addWidget(self.campo_livro)
        coluna.addWidget(self.lista_livros)
        coluna.addWidget(self.botao_entregar)
        return coluna

    def montar_lista(self):
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItem("Somente em uso", True)
        self.combo_filtro.addItem("Todos (com devolvidos)", False)

        self.tabela = QTableWidget(0, 6)
        self.tabela.setHorizontalHeaderLabels(
            ["Nº", "Usuário", "Livro", "Tipo", "Devolver até", "Situação"]
        )
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setAlternatingRowColors(True)
        cabecalho = self.tabela.horizontalHeader()
        cabecalho.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        cabecalho.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.botao_devolver = QPushButton("Devolver livro selecionado")

        titulo = QLabel("Livros em uso")
        titulo.setObjectName("titulo_pagina")
        coluna = QVBoxLayout()
        coluna.addWidget(titulo)
        coluna.addWidget(self.combo_filtro)
        coluna.addWidget(self.tabela)
        coluna.addWidget(self.botao_devolver)
        return coluna

    def conectar_eventos(self):
        self.campo_usuario.textChanged.connect(self.buscar_usuarios)
        self.campo_livro.textChanged.connect(self.filtrar_livros)
        self.botao_entregar.clicked.connect(self.entregar)
        self.combo_filtro.currentIndexChanged.connect(self.atualizar_lista)
        self.botao_devolver.clicked.connect(self.devolver)

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
                continue  # sem exemplar livre: não dá para entregar
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
        QMessageBox.warning(self, "Livros em uso", str(erro))
        campos = {
            "codigo": self.campo_codigo,
            "usuario": self.campo_usuario,
            "livros": self.lista_livros,
            "lista": self.tabela,
        }
        campos[erro.campo].setFocus()

    def entregar(self):
        marcados = self.livros_marcados()
        try:
            prazo = servicos.registrar_uso(
                self.conn,
                self.campo_codigo.text(),
                self.combo_usuario.currentData(),
                marcados,
                self.combo_tipo.currentData(),
            )
        except ErroValidacao as erro:
            self.avisar(erro)
            return
        if prazo is None:
            mensagem = f"{len(marcados)} livro(s) entregue(s) para leitura no local."
        else:
            mensagem = (f"{len(marcados)} livro(s) retirado(s).\n"
                        f"Devolver até {prazo.strftime('%d/%m/%Y')}.")
        QMessageBox.information(self, "Livros em uso", mensagem)
        self.campo_usuario.clear()  # o código do funcionário fica, para o próximo
        self.campo_livro.clear()
        self.carregar_livros()
        self.atualizar_lista()

    # ---------- lista ----------

    def atualizar_lista(self):
        usos = banco.listar_usos(self.conn, self.combo_filtro.currentData())
        self.tabela.setRowCount(len(usos))
        for linha, uso in enumerate(usos):
            prazo = data_hora(uso["devolver_ate"]) if uso["devolver_ate"] else "—"
            situacao = servicos.situacao_do_uso(uso)
            valores = [uso["id"], uso["usuario"], uso["livro"], NOMES_TIPO[uso["tipo"]],
                       prazo, situacao]
            for coluna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                if situacao == "atrasado":
                    self.destacar(item)
                self.tabela.setItem(linha, coluna, item)
        self.tabela.clearSelection()

    def destacar(self, item):
        """Livro atrasado: linha em negrito, na cor de alerta do tema."""
        item.setForeground(QColor(tema.cores_atuais()["alerta"]))
        fonte = item.font()
        fonte.setBold(True)
        item.setFont(fonte)

    def devolver(self):
        linhas = self.tabela.selectionModel().selectedRows()
        if not linhas:
            QMessageBox.information(self, "Livros em uso", "Selecione um livro na lista.")
            return
        uso_id = int(self.tabela.item(linhas[0].row(), 0).text())
        try:
            servicos.devolver(self.conn, self.campo_codigo.text(), uso_id)
        except ErroValidacao as erro:
            self.avisar(erro)
            return
        QMessageBox.information(self, "Livros em uso", "Devolução registrada.")
        self.carregar_livros()
        self.atualizar_lista()
