import sqlite3
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QIntValidator
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QSpinBox,
    QStackedWidget,
)

import banco
import icones
import tema
import servicos
from abertura import AberturaLivro
from livro import CapaLivro, FundoLivro
from pessoas import PaginasPessoas
from reservas import PaginasReservas
from usos import PaginasUsos
from validacao import ErroValidacao, validar_livro
from virada import ViradaPagina


class Janela_Livros(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Livros")
        self.resize(1100, 670)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)          # sem a moldura do Windows
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # cantos transparentes
        self.conn = banco.conectar()
        self.livro_selecionado = None  # livro clicado na tabela (ou None)
        self.pode_fechar = False       # vira True depois da animação de fechar

        capa = self.capa = CapaLivro()
        layout_capa = QVBoxLayout(capa)
        layout_capa.setContentsMargins(18, 12, 18, 8)
        self.barra_mensagens = QStatusBar()

        # Cada página do livro guarda uma pilha de conteúdos: um por tela.
        self.pilha_esquerda = QStackedWidget()
        self.pilha_direita = QStackedWidget()
        self.pagina_esquerda = self.montar_pagina("pagina_esquerda", self.pilha_esquerda)
        self.lombada = self.montar_lombada()
        self.pagina_direita = self.montar_pagina("pagina_direita", self.pilha_direita)
        capa.paginas = [(self.pagina_esquerda, "esquerda"), (self.pagina_direita, "direita")]
        self.montar_telas()
        self.virada = ViradaPagina(capa)

        paginas = QHBoxLayout()
        paginas.setSpacing(0)
        paginas.addWidget(self.pagina_esquerda, 2)
        paginas.addWidget(self.lombada)
        paginas.addWidget(self.pagina_direita, 3)

        layout_capa.addLayout(self.montar_barra_titulo())
        layout_capa.addLayout(paginas)
        layout_capa.addSpacing(8)  # espaço para a pilha de folhas aparecer
        layout_capa.addWidget(self.barra_mensagens)
        self.setCentralWidget(FundoLivro(capa, self.lombada))

        self.statusBar().showMessage("Pronto. Cadastre o primeiro livro.")

        self.conectar_eventos()
        self.aplicar_icones()
        servicos.expirar_reservas(self.conn)
        self.mostrar_na_tabela(banco.listar_livros(self.conn))

    def statusBar(self):
        # O rodapé agora mora dentro da capa; as mensagens continuam iguais.
        return self.barra_mensagens

    def mousePressEvent(self, evento):
        # Sem a barra do Windows, arrastar a capa move a janela.
        if evento.button() == Qt.MouseButton.LeftButton:
            self.windowHandle().startSystemMove()

    def montar_barra_titulo(self):
        titulo = QLabel("Gerenciador de Livros")
        titulo.setObjectName("titulo_janela")

        botao_minimizar = QToolButton()
        botao_minimizar.setText("–")
        botao_minimizar.setToolTip("Minimizar")
        botao_minimizar.clicked.connect(self.showMinimized)

        botao_fechar = QToolButton()
        botao_fechar.setText("✕")
        botao_fechar.setObjectName("fechar")
        botao_fechar.setToolTip("Fechar")
        botao_fechar.clicked.connect(self.close)

        barra = QHBoxLayout()
        barra.addWidget(titulo)
        barra.addStretch()
        self.abas = QButtonGroup(self)  # só uma aba fica marcada por vez
        for indice, (nome, _, _, _) in enumerate(self.telas):
            aba = QToolButton()
            aba.setText(nome)
            aba.setCheckable(True)
            aba.setChecked(indice == 0)
            aba.clicked.connect(lambda _, i=indice: self.trocar_tela(i))
            self.abas.addButton(aba, indice)
            barra.addWidget(aba)
        barra.addWidget(self.montar_menu())
        barra.addWidget(botao_minimizar)
        barra.addWidget(botao_fechar)
        return barra

    def montar_menu(self):
        self.botao_tema = QToolButton()
        self.botao_tema.setText("&Tema")
        self.botao_tema.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self.botao_tema)
        self.botao_tema.setMenu(menu)

        grupo = QActionGroup(self)
        grupo.triggered.connect(self.trocar_tema)
        for chave, cores in tema.TEMAS.items():
            acao = QAction(cores["nome"], self)
            acao.setCheckable(True)
            acao.setData(chave)
            acao.setChecked(chave == tema.tema_salvo())
            grupo.addAction(acao)
            menu.addAction(acao)
        return self.botao_tema

    def trocar_tema(self, acao):
        nome = acao.data()
        tema.aplicar_tema(nome)
        tema.salvar_tema(nome)
        self.aplicar_icones()
        self.update()  # redesenha sombra, fita e folhas com as cores novas
        self.statusBar().showMessage(f"Tema {acao.text()} aplicado.", 3000)

    def montar_formulario(self):
        self.campo_titulo = QLineEdit()
        self.campo_autor = QLineEdit()
        self.campo_ano = QLineEdit()
        self.campo_ano.setValidator(QIntValidator(0, 2100))
        self.campo_ano.setMaxLength(4)
        self.campo_ano.setPlaceholderText("Ex.: 2016")
        self.campo_isbn = QLineEdit()
        self.campo_isbn.setPlaceholderText('13 dígitos, com ou sem hífen')
        self.campo_quantidade = QSpinBox()
        self.campo_quantidade.setRange(1, 999)
        self.campo_quantidade.setValue(1)

        formulario = QFormLayout()
        formulario.addRow("Título *", self.campo_titulo)
        formulario.addRow("Autor *", self.campo_autor)
        formulario.addRow("Ano", self.campo_ano)
        formulario.addRow("ISBN", self.campo_isbn)
        formulario.addRow("Exemplares *", self.campo_quantidade)
        return formulario

    def montar_acoes(self):
        self.botao_cadastrar = QPushButton("Cadastrar")
        self.botao_cadastrar.setProperty("variante", "primario")
        self.botao_atualizar = QPushButton("Atualizar")
        self.botao_excluir = QPushButton("Excluir")
        self.botao_limpar = QPushButton("Limpar")

        # Atualizar e Excluir começam desligados: só funcionam com um livro selecionado.
        self.botao_atualizar.setEnabled(False)
        self.botao_excluir.setEnabled(False)

        linha = QHBoxLayout()
        linha.addWidget(self.botao_cadastrar)
        linha.addWidget(self.botao_atualizar)
        linha.addWidget(self.botao_excluir)
        linha.addStretch()
        linha.addWidget(self.botao_limpar)
        return linha

    def montar_pesquisa(self):
        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText("Digite parte do título ou do autor")
        self.botao_pesquisar = QPushButton("Pesquisar")
        self.botao_mostrar_todos = QPushButton("Mostrar todos")

        linha = QHBoxLayout()
        linha.addWidget(QLabel("Pesquisar"))
        linha.addWidget(self.campo_pesquisa, 1)
        linha.addWidget(self.botao_pesquisar)
        linha.addWidget(self.botao_mostrar_todos)
        return linha
    
    def montar_tabela(self):
        self.tabela = QTableWidget(0, 7)
        self.tabela.setHorizontalHeaderLabels(["ID", "Título", "Autor", "Ano", "ISBN", "Exemplares", "Disponíveis"])
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setAlternatingRowColors(True)

        cabecalho = self.tabela.horizontalHeader()
        cabecalho.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        cabecalho.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        cabecalho.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        return self.tabela

    def closeEvent(self, evento):
        if not self.pode_fechar:
            evento.ignore()  # ainda não: primeiro o livro se fecha
            centro = self.geometry().center()
            self.hide()
            self.fechamento = AberturaLivro(tema.cores_atuais(), fechando=True, centro=centro)
            self.fechamento.terminou.connect(self.fechar_de_vez)
            self.fechamento.iniciar()
            return
        self.conn.close()
        super().closeEvent(evento)

    def fechar_de_vez(self):
        self.pode_fechar = True
        self.close()
        self.fechamento.close()

    def mostrar_na_tabela(self, livros):
        self.tabela.setRowCount(len(livros))
        for linha, livro in enumerate(livros):
            valores = [livro["id"], livro["titulo"], livro["autor"], livro["ano"], livro["isbn"],
                       livro["quantidade"], livro["disponiveis"]]
            for coluna, valor in enumerate(valores):
                texto = "" if valor is None else str(valor)
                self.tabela.setItem(linha, coluna, QTableWidgetItem(texto))
        self.tabela.clearSelection()

    def avisar(self, texto, nome_campo):
        QMessageBox.warning(self, "Gerenciador de Livros", texto)
        campos = {
            "titulo": self.campo_titulo,
            "autor": self.campo_autor,
            "ano": self.campo_ano,
            "isbn": self.campo_isbn,
            "quantidade": self.campo_quantidade,
        }
        campos[nome_campo].setFocus()

    def cadastrar(self):
        try:
            livro = validar_livro(
                self.campo_titulo.text(),
                self.campo_autor.text(),
                self.campo_ano.text(),
                self.campo_isbn.text(),
                self.campo_quantidade.value(),
            )
        except ErroValidacao as erro:
            self.avisar(str(erro), erro.campo)
            return

        funcionario = self.pedir_funcionario(f'Cadastrar o livro "{livro["titulo"]}".')
        if funcionario is None:
            return

        novo_id = banco.inserir_livro(
            self.conn, livro["titulo"], livro["autor"], livro["ano"], livro["isbn"],
            livro["quantidade"],
        )
        self.limpar_campos()
        self.mostrar_na_tabela(banco.listar_livros(self.conn))
        self.statusBar().showMessage(
            f'Livro "{livro["titulo"]}" cadastrado com o ID {novo_id} por {funcionario["codigo"]}.', 5000
        )

    def limpar_campos(self):
        for campo in (self.campo_titulo, self.campo_autor, self.campo_ano, self.campo_isbn):
            campo.clear()
        self.campo_quantidade.setValue(1)
        self.tabela.clearSelection()
        self.campo_titulo.setFocus()

    def conectar_eventos(self):
        self.botao_cadastrar.clicked.connect(self.cadastrar)
        self.botao_limpar.clicked.connect(self.limpar_campos)
        self.botao_pesquisar.clicked.connect(self.pesquisar)
        self.campo_pesquisa.returnPressed.connect(self.pesquisar)
        self.botao_mostrar_todos.clicked.connect(self.mostrar_todos)
        self.tabela.itemSelectionChanged.connect(self.selecionar_livro)
        self.botao_excluir.clicked.connect(self.excluir)
        self.botao_atualizar.clicked.connect(self.atualizar)

    def pesquisar(self):
        termo = self.campo_pesquisa.text().strip()
        if not termo:
            self.statusBar().showMessage("Digite parte do título ou do autor para pesquisar.", 5000)
            self.campo_pesquisa.setFocus()
            return
        encontrados = banco.pesquisar_livros(self.conn, termo)
        self.mostrar_na_tabela(encontrados)
        self.statusBar().showMessage(f'{len(encontrados)} livro(s) encontrado(s) para "{termo}".', 5000)

    def mostrar_todos(self):
        self.campo_pesquisa.clear()
        livros = banco.listar_livros(self.conn)
        self.mostrar_na_tabela(livros)
        self.statusBar().showMessage(f"{len(livros)} livro(s) cadastrado(s).", 5000)

    def selecionar_livro(self):
        linhas = self.tabela.selectionModel().selectedRows()
        if not linhas:
            self.livro_selecionado = None
            self.botao_cadastrar.setEnabled(True)
            self.botao_atualizar.setEnabled(False)
            self.botao_excluir.setEnabled(False)
            self.limpar_campos()
            return

        livro_id = int(self.tabela.item(linhas[0].row(), 0).text())
        livro = banco.obter_livro(self.conn, livro_id)
        self.livro_selecionado = livro
        self.campo_titulo.setText(livro["titulo"])
        self.campo_autor.setText(livro["autor"])
        self.campo_ano.setText("" if livro["ano"] is None else str(livro["ano"]))
        self.campo_isbn.setText(livro["isbn"] or "")
        self.campo_quantidade.setValue(livro["quantidade"])
        self.botao_cadastrar.setEnabled(False)
        self.botao_atualizar.setEnabled(True)
        self.botao_excluir.setEnabled(True)
        self.statusBar().showMessage(
            f'Livro "{livro["titulo"]}" selecionado. Altere os campos e clique em Atualizar, '
            "ou clique em Limpar para cadastrar outro.", 8000
        )

    def montar_coluna_cadastro(self):
        titulo = QLabel("Cadastro do livro")
        titulo.setObjectName("titulo_pagina")
        coluna = QVBoxLayout()
        coluna.addWidget(titulo)
        coluna.addLayout(self.montar_formulario())
        coluna.addLayout(self.montar_acoes())
        coluna.addStretch()
        coluna.addWidget(self.montar_citacao())
        return self.montar_conteudo(coluna)

    def montar_coluna_livros(self):
        titulo = QLabel("Livros cadastrados")
        titulo.setObjectName("titulo_pagina")
        coluna = QVBoxLayout()
        coluna.addWidget(titulo)
        coluna.addLayout(self.montar_pesquisa())
        coluna.addWidget(self.montar_tabela())
        return self.montar_conteudo(coluna)

    def montar_lombada(self):
        lombada = QFrame()
        lombada.setObjectName("lombada")
        lombada.setFixedWidth(16)
        return lombada

    def excluir(self):
        livro = self.livro_selecionado
        if livro is None:
            self.statusBar().showMessage("Selecione um livro na tabela para excluir.", 5000)
            return

        funcionario = self.pedir_funcionario(
            f'Excluir o livro "{livro["titulo"]}" (ID {livro["id"]}).\n'
            "Essa ação não pode ser desfeita."
        )
        if funcionario is None:
            return

        try:
            banco.excluir_livro(self.conn, livro["id"])
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self, "Excluir livro",
                "Este livro tem reservas ou usos registrados e não pode ser excluído.",
            )
            return
        self.limpar_campos()
        self.campo_pesquisa.clear()
        self.mostrar_na_tabela(banco.listar_livros(self.conn))
        self.statusBar().showMessage(
            f'Livro "{livro["titulo"]}" excluído por {funcionario["codigo"]}.', 5000
        )

    def atualizar(self):
        livro = self.livro_selecionado
        if livro is None:
            self.statusBar().showMessage("Selecione um livro na tabela para atualizar.", 5000)
            return

        try:
            novo = validar_livro(
                self.campo_titulo.text(),
                self.campo_autor.text(),
                self.campo_ano.text(),
                self.campo_isbn.text(),
                self.campo_quantidade.value(),
            )
        except ErroValidacao as erro:
            self.avisar(str(erro), erro.campo)
            return

        antes = (livro["titulo"], livro["autor"], livro["ano"], livro["isbn"], livro["quantidade"])
        depois = (novo["titulo"], novo["autor"], novo["ano"], novo["isbn"], novo["quantidade"])
        if antes == depois:
            self.statusBar().showMessage("Nada mudou. Altere algum campo antes de atualizar.", 5000)
            return

        ocupados = livro["quantidade"] - livro["disponiveis"]  # em uso ou reservados
        if novo["quantidade"] < ocupados:
            self.avisar(
                f"Há {ocupados} exemplar(es) em uso ou reservado(s). "
                "A quantidade não pode ficar abaixo disso.",
                "quantidade",
            )
            return

        funcionario = self.pedir_funcionario(f'Salvar as alterações no livro ID {livro["id"]}.')
        if funcionario is None:
            return

        banco.atualizar_livro(
            self.conn, livro["id"], novo["titulo"], novo["autor"], novo["ano"], novo["isbn"],
            novo["quantidade"],
        )
        self.limpar_campos()
        self.campo_pesquisa.clear()
        self.mostrar_na_tabela(banco.listar_livros(self.conn))
        self.statusBar().showMessage(
            f'Livro ID {livro["id"]} atualizado por {funcionario["codigo"]}.', 5000
        )

    def aplicar_icones(self):
        cores = tema.cores_atuais()
        self.botao_cadastrar.setIcon(
            icones.criar_icone("cadastrar", cores["primaria_texto"], cores["texto_suave"])
        )
        for botao, nome in (
            (self.botao_atualizar, "atualizar"),
            (self.botao_excluir, "excluir"),
            (self.botao_limpar, "limpar"),
            (self.botao_pesquisar, "pesquisar"),
            (self.botao_mostrar_todos, "mostrar_todos"),
        ):
            botao.setIcon(icones.criar_icone(nome, cores["texto"], cores["texto_suave"]))

    def montar_citacao(self):
        citacao = QLabel(
            "“Se a educação sozinha não transforma a sociedade, "
            "sem ela tampouco a sociedade muda.”\n"
            "(Freire, 2000, p. 67)"
        )
        citacao.setObjectName("citacao")
        citacao.setWordWrap(True)
        citacao.setAlignment(Qt.AlignmentFlag.AlignRight)
        return citacao

    # ---------- telas do livro ----------

    def montar_conteudo(self, layout):
        """Embrulha um layout num widget, para caber na pilha de uma página."""
        layout.setContentsMargins(0, 0, 0, 0)  # a margem já é a da página
        conteudo = QWidget()
        conteudo.setLayout(layout)
        return conteudo

    def montar_pagina(self, nome, pilha):
        """Uma folha do livro. O conteúdo dela muda conforme a tela escolhida."""
        pagina = QFrame()
        pagina.setObjectName(nome)
        layout = QVBoxLayout(pagina)
        layout.addWidget(pilha)
        return pagina

    def montar_telas(self):
        """Cada tela: (nome da aba, conteúdo esquerdo, conteúdo direito, o que fazer ao mostrar)."""
        usuarios = PaginasPessoas(self.conn, "usuario")
        funcionarios = PaginasPessoas(self.conn, "funcionario")
        reservas = PaginasReservas(self.conn)
        usos = PaginasUsos(self.conn)
        self.telas = [
            ("&Livros", self.montar_coluna_cadastro(), self.montar_coluna_livros(),
             self.mostrar_todos),
            ("&Usuários", usuarios, usuarios.pagina_direita, usuarios.ao_mostrar),
            ("&Funcionários", funcionarios, funcionarios.pagina_direita, funcionarios.ao_mostrar),
            ("&Reservas", reservas, reservas.pagina_direita, reservas.ao_mostrar),
            ("&Em uso", usos, usos.pagina_direita, usos.ao_mostrar),
        ]
        for _, esquerda, direita, _ in self.telas:
            self.pilha_esquerda.addWidget(esquerda)
            self.pilha_direita.addWidget(direita)
        self.tela_atual = 0

    def trocar_tela(self, indice):
        """Vira a página até a tela escolhida."""
        if indice == self.tela_atual:
            return
        self.virada.parar()  # se ainda estava virando, termina na hora
        area = self.pagina_esquerda.geometry().united(self.pagina_direita.geometry())
        antes = self.capa.grab(area)  # "foto" das páginas como estão

        self.pilha_esquerda.setCurrentIndex(indice)
        self.pilha_direita.setCurrentIndex(indice)
        self.telas[indice][3]()  # atualiza os dados da tela que vai aparecer
        depois = self.capa.grab(area)  # "foto" das páginas novas

        meio = self.lombada.geometry().center().x() - area.x()
        self.virada.iniciar(area, antes, depois, meio, para_frente=indice > self.tela_atual)
        self.tela_atual = indice

    def pedir_funcionario(self, acao):
        """Pede o código do funcionário. Devolve o funcionário, ou None se cancelar ou errar."""
        codigo, confirmou = QInputDialog.getText(
            self, "Código do funcionário", f"{acao}\n\nInforme seu código de funcionário:"
        )
        if not confirmou:
            self.statusBar().showMessage("Operação cancelada.", 3000)
            return None
        funcionario = banco.buscar_funcionario_por_codigo(self.conn, codigo)
        if funcionario is None or not funcionario["ativo"]:
            QMessageBox.warning(
                self, "Código do funcionário",
                "Código inválido ou funcionário inativo. Nada foi alterado.",
            )
            return None
        return funcionario
