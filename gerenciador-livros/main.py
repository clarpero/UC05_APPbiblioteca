import sys

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QApplication

import tema
from abertura import AberturaLivro
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

    abertura = AberturaLivro(tema.TEMAS[tema.tema_salvo()])
    abertura.terminou.connect(janela_principal.show)   # primeiro mostra a janela...
    abertura.terminou.connect(abertura.close)          # ...depois fecha a abertura
    abertura.iniciar()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())