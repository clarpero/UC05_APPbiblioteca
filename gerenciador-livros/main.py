import sys

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QApplication, QDialog

import tema
from abertura import AberturaLivro
from janela_principal import Janela_Livros
from login import DialogoLogin


def main():
    app = QApplication(sys.argv)

    # Botões padrão do Qt (Sim, Não, OK, Cancelar) em português
    tradutor = QTranslator(app)
    pasta = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if tradutor.load(QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil), "qtbase", "_", pasta):
        app.installTranslator(tradutor)

    tema.aplicar_tema(tema.tema_salvo())
    
    login = DialogoLogin()
    if login.exec() != QDialog.DialogCode.Accepted:
        return 0  # cancelou ou errou demais: o programa não abre
    
    janela_principal = Janela_Livros()

    abertura = AberturaLivro(tema.TEMAS[tema.tema_salvo()])
    abertura.terminou.connect(janela_principal.show)   # primeiro mostra a janela...
    abertura.terminou.connect(abertura.close)          # ...depois fecha a abertura
    abertura.iniciar()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())