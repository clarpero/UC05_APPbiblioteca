import sys

from PySide6.QtWidgets import QApplication

import tema
from janela_principal import Janela_Livros


def main():
    app = QApplication(sys.argv)
    tema.aplicar_tema(tema.tema_salvo())
    janela_principal = Janela_Livros()
    janela_principal.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())