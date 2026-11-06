import banco
import tema
from validacao import ErroValidacao, validar_livro
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    )

class Janela_Livros(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Livros")
        self.resize (900,520)
        self.conn = banco.conectar()

        central = QWidget()
        self.layout_principal = QVBoxLayout(central)
        self.setCentralWidget(central)
        self.montar_menu()

        self.layout_principal.addLayout(self.montar_formulario())
        self.layout_principal.addLayout(self.montar_acoes())
        self.botao_cadastrar.setProperty("variante", "primario")
        self.layout_principal.addLayout(self.montar_pesquisa())
        self.layout_principal.addWidget(self.montar_tabela())
        self.statusBar().showMessage('Pronto. Cadastre o primeiro livro.')

        self.conectar_eventos()
        self.mostrar_na_tabela(banco.listar_livros(self.conn))

    def montar_menu(self):
        menu = self.menuBar().addMenu("&Tema")
        grupo = QActionGroup(self)
        grupo.triggered.connect(self.trocar_tema)
        for chave, cores in tema.TEMAS.items():
            acao = QAction(cores["nome"], self)
            acao.setCheckable(True)
            acao.setData(chave)
            acao.setChecked(chave == tema.tema_salvo())
            grupo.addAction(acao)
            menu.addAction(acao)

    def trocar_tema(self, acao):
        nome = acao.data()
        tema.aplicar_tema(nome)
        tema.salvar_tema(nome)
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

        grade = QGridLayout()
        grade.addWidget(QLabel('Título *'), 0, 0) 
        grade.addWidget(self.campo_titulo, 0, 1)
        grade.addWidget(QLabel('Autor *'), 0, 2)
        grade.addWidget(self.campo_autor, 0, 3)
        grade.addWidget(QLabel('Ano'), 1, 0)
        grade.addWidget(self.campo_ano, 1, 1)
        grade.addWidget(QLabel('ISBN'), 1, 2)
        grade.addWidget(self.campo_isbn, 1, 3)
        grade.setColumnStretch(1, 1)
        grade.setColumnStretch(3, 1)
        return grade

    def montar_acoes(self):
        self.botao_cadastrar = QPushButton("Cadastrar")
        self.botao_atualizar = QPushButton("Atualizar")
        self.botao_excluir = QPushButton("Excluir")
        self.botao_limpar = QPushButton("Limpar")

        # Atualizar e Excluir serão implementados numa etapa posterior.
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
        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Título", "Autor", "Ano", "ISBN"])
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
                self.conn.close()
                super().closeEvent(evento)

    def mostrar_na_tabela(self, livros):
        self.tabela.setRowCount(len(livros))
        for linha, livro in enumerate(livros):
            valores = [livro["id"], livro["titulo"], livro["autor"], livro["ano"], livro["isbn"]]
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
        }
        campos[nome_campo].setFocus()

    def cadastrar(self):
        try:
            livro = validar_livro(
                self.campo_titulo.text(),
                self.campo_autor.text(),
                self.campo_ano.text(),
                self.campo_isbn.text(),
            )
        except ErroValidacao as erro:
            self.avisar(str(erro), erro.campo)
            return

        novo_id = banco.inserir_livro(
            self.conn, livro["titulo"], livro["autor"], livro["ano"], livro["isbn"]
        )
        self.limpar_campos()
        self.mostrar_na_tabela(banco.listar_livros(self.conn))
        self.statusBar().showMessage(f'Livro "{livro["titulo"]}" cadastrado com o ID {novo_id}.', 5000)

    def limpar_campos(self):
        for campo in (self.campo_titulo, self.campo_autor, self.campo_ano, self.campo_isbn):
            campo.clear()
        self.tabela.clearSelection()
        self.campo_titulo.setFocus()

    def conectar_eventos(self):
        self.botao_cadastrar.clicked.connect(self.cadastrar)
        self.botao_limpar.clicked.connect(self.limpar_campos)
        self.botao_pesquisar.clicked.connect(self.pesquisar)
        self.campo_pesquisa.returnPressed.connect(self.pesquisar)
        self.botao_mostrar_todos.clicked.connect(self.mostrar_todos)
        self.tabela.itemSelectionChanged.connect(self.selecionar_livro)

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
            self.botao_cadastrar.setEnabled(True)
            self.limpar_campos()
            return

        livro_id = int(self.tabela.item(linhas[0].row(), 0).text())
        livro = banco.obter_livro(self.conn, livro_id)
        self.campo_titulo.setText(livro["titulo"])
        self.campo_autor.setText(livro["autor"])
        self.campo_ano.setText("" if livro["ano"] is None else str(livro["ano"]))
        self.campo_isbn.setText(livro["isbn"] or "")
        self.botao_cadastrar.setEnabled(False)
        self.statusBar().showMessage(
            f'Livro "{livro["titulo"]}" selecionado. Clique em Limpar para cadastrar outro.', 8000
        )
