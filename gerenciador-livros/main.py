import sys
from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator

from PySide6.QtWidgets import QApplication

import tema
from janela_principal import Janela_Livros


def main():
    app = QApplication(sys.argv)
        # Botões padrão do Qt (Sim, Não, OK, Cancelar) em português
    tradutor = QTranslator(app)
    pasta = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if tradutor.load(QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil), "qtbase", "_", pasta):
        app.installTranslator(tradutor)
    tema.aplicar_tema(tema.tema_salvo())
    janela_principal = Janela_Livros()
    janela_principal.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())