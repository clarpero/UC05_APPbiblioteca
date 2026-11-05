from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

class Janela_Livros(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Livros")
        self.resize (900,520)

        central = QWidget()
        self.layout_principal = QVBoxLayout(central)
        self.setCentralWidget(central)
        