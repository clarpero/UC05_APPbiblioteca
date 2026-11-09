"""Ícones dos botões: desenhos em SVG pintados com a cor do tema."""

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

# Molde de todos os ícones: quadro de 24 x 24, só traço, pontas arredondadas.
MOLDE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="{cor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    "{desenho}</svg>"
)

DESENHOS = {
    "cadastrar": '<path d="M12 5v14M5 12h14"/>',
    "atualizar": '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13 7l4 4"/>',
    "excluir": '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/>',
    "limpar": '<circle cx="12" cy="12" r="8"/><path d="M9 9l6 6M15 9l-6 6"/>',
    "pesquisar": '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    "mostrar_todos": '<path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/>',
}


def desenhar(nome, cor):
    svg = MOLDE.format(cor=cor, desenho=DESENHOS[nome])
    renderizador = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    imagem = QPixmap(48, 48)
    imagem.fill(Qt.GlobalColor.transparent)
    pintor = QPainter(imagem)
    renderizador.render(pintor)
    pintor.end()
    return imagem


def criar_icone(nome, cor, cor_desligado):
    icone = QIcon()
    icone.addPixmap(desenhar(nome, cor), QIcon.Mode.Normal)
    icone.addPixmap(desenhar(nome, cor_desligado), QIcon.Mode.Disabled)
    return icone