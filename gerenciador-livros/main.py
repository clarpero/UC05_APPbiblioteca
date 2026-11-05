import sys 
from PySide6.QtWidgets import QApplication
from janela_principal import Janela_Livros

def main():
    app = QApplication(sys.argv)
    janela_principal = Janela_Livros()
    janela_principal.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())