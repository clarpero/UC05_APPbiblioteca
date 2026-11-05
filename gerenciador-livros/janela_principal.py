from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow, 
    QPushButton,
    QVBoxLayout, 
    QWidget
    )

class Janela_Livros(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Livros")
        self.resize (900,520)

        central = QWidget()
        self.layout_principal = QVBoxLayout(central)
        self.setCentralWidget(central)
        self.layout_principal.addLayout(self.montar_formulario())
        self.layout_principal.addLayout(self.montar_acoes())

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