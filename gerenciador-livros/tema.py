"""Temas da aplicação: as cores de cada tema, a paleta do Qt e a folha de estilo."""

from pathlib import Path
from string import Template

from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

PASTA_IMAGENS = Path(__file__).with_name("imagens")
TEMAS = {
    "claro": {
        "nome": "Claro",
        "fundo": "#f3f4f6",
        "superficie": "#ffffff",
        "zebra": "#f5f7fa",
        "texto": "#1f2328",
        "texto_suave": "#59636e",
        "borda": "#cfd6dd",
        "botao": "#e9edf1",
        "primaria": "#0b5ed7",
        "primaria_hover": "#0a4fb5",
        "primaria_texto": "#ffffff",
        "selecao": "#cfe2ff",
        "capa": "#2b4c7e",
        "capa_texto": "#ffffff",
        "sombra": "#d9dee4",
        "fita": "#c62828",
        "alerta": "#b3261e",         # texto de livro atrasado
    },
    "escuro": {
        "nome": "Escuro",
        "fundo": "#1b1f24",
        "superficie": "#24292f",
        "zebra": "#2b3138",
        "texto": "#e6edf3",
        "texto_suave": "#9da7b3",
        "borda": "#3d444d",
        "botao": "#32383f",
        "primaria": "#4493f8",
        "primaria_hover": "#6aa9fa",
        "primaria_texto": "#0d1117",
        "selecao": "#1f4a7a",
        "capa": "#0d1117",
        "capa_texto": "#e6edf3",
        "sombra": "#1a1f25",
        "fita": "#e0a526",
        "alerta": "#ff7b72",
    },
    "biblioteca": {
        "nome": "Biblioteca",
        "fundo": "#efe4d2",          # pergaminho
        "superficie": "#fbf6ee",     # papel
        "zebra": "#f5ecdf",
        "texto": "#3b2618",          # tinta marrom-escura
        "texto_suave": "#6e5340",
        "borda": "#c4a888",
        "botao": "#e6d5bd",
        "primaria": "#7b3f1d",       # couro de encadernação
        "primaria_hover": "#62311a",
        "primaria_texto": "#fbf6ee",
        "selecao": "#e3c9a6",
        "capa": "#5b2f18",           # couro escuro da capa
        "capa_texto": "#f6ead8",
        "sombra": "#d8c3a3",
        "textura": "papel.png",
        "fita": "#7d1f1f",      # imagem de fundo das páginas
        "alerta": "#9b1c1c",
    },
}

# Qual cor do tema pinta cada parte padrão dos componentes do Qt.
PAPEIS = [
    (QPalette.ColorRole.Window, "fundo"),
    (QPalette.ColorRole.WindowText, "texto"),
    (QPalette.ColorRole.Base, "superficie"),
    (QPalette.ColorRole.AlternateBase, "zebra"),
    (QPalette.ColorRole.Text, "texto"),
    (QPalette.ColorRole.Button, "botao"),
    (QPalette.ColorRole.ButtonText, "texto"),
    (QPalette.ColorRole.Highlight, "selecao"),
    (QPalette.ColorRole.HighlightedText, "texto"),
    (QPalette.ColorRole.PlaceholderText, "texto_suave"),
    (QPalette.ColorRole.ToolTipBase, "superficie"),
    (QPalette.ColorRole.ToolTipText, "texto"),
]

# Detalhes que a paleta não cobre: o livro (capa, páginas, lombada) e o botão principal.
FOLHA = Template("""
QFrame#capa {
    background-color: $capa;
    border-radius: 18px;
}
QLabel#titulo_janela {
    color: $capa_texto;
    font-size: 12pt;
    font-weight: bold;
}
QToolButton {
    color: $capa_texto;
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px 10px;
    font-weight: bold;
}
QToolButton:hover {
    background-color: rgba(255, 255, 255, 40);
}
QToolButton#fechar:hover {
    background-color: #c42b1c;
    color: #ffffff;
}
QToolButton::menu-indicator {
    image: none;
}
QStatusBar {
    color: $capa_texto;
}
QStatusBar::item {
    border: none;
}

QFrame#pagina_esquerda, QFrame#pagina_direita {
    background-color: $superficie;
    $imagem_pagina
    border: 1px solid $borda;
}
QFrame#pagina_esquerda {
    border-right: none;
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}
QFrame#pagina_direita {
    border-left: none;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}
QFrame#lombada {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 $superficie, stop:0.5 $sombra, stop:1 $superficie);
    border-top: 1px solid $borda;
    border-bottom: 1px solid $borda;
}
QLabel#titulo_pagina {
    color: $primaria;
    font-size: 13pt;
    font-weight: bold;
}
QLabel#citacao {
    color: $texto_suave;
    font-size: 10pt;
    padding: 12px 4px 4px 48px;
}
QLineEdit {
    background-color: $superficie;
    border: 1px solid $borda;
    border-radius: 6px;
    padding: 5px 8px;
}
QLineEdit:focus {
    border: 2px solid $primaria;
}
QPushButton[variante="primario"] {
    background-color: $primaria;
    color: $primaria_texto;
    border: 1px solid $primaria;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: bold;
}
QPushButton[variante="primario"]:hover {
    background-color: $primaria_hover;
}
QPushButton[variante="primario"]:disabled {
    background-color: $botao;
    color: $texto_suave;
    border-color: $borda;
}
QTableWidget {
    gridline-color: $borda;
}
QHeaderView::section {
    background-color: $botao;
    color: $texto;
    padding: 5px;
    border: none;
    border-bottom: 1px solid $borda;
    font-weight: bold;
}
""")


_atual = "claro"  # nome do tema em uso


def cores_atuais():
    return TEMAS[_atual]


def aplicar_tema(nome):
    global _atual
    _atual = nome
    cores = TEMAS[nome]
    paleta = QPalette()
    for papel, token in PAPEIS:
        paleta.setColor(papel, QColor(cores[token]))
    for papel in (QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText, QPalette.ColorRole.WindowText):
        paleta.setColor(QPalette.ColorGroup.Disabled, papel, QColor(cores["texto_suave"]))

    valores = dict(cores)
    if "textura" in cores:
        caminho = (PASTA_IMAGENS / cores["textura"]).as_posix()
        valores["imagem_pagina"] = f'background-image: url("{caminho}");'
    else:
        valores["imagem_pagina"] = ""

    app = QApplication.instance()
    app.setStyle("Fusion")
    app.setPalette(paleta)
    app.setStyleSheet(FOLHA.substitute(valores))


def _configuracoes():
    return QSettings("Senac-PI", "GerenciadorLivros")


def tema_salvo():
    nome = _configuracoes().value("tema", "claro")
    return nome if nome in TEMAS else "claro"


def salvar_tema(nome):
    _configuracoes().setValue("tema", nome)