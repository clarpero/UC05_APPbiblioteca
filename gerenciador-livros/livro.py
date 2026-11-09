"""Partes do livro desenhadas à mão: sombra, fita marcadora e pilha de folhas."""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

import tema


class FundoLivro(QWidget):
    """Área transparente em volta da capa. Desenha a sombra e a fita."""

    def __init__(self, capa, lombada):
        super().__init__()
        self.capa = capa
        self.lombada = lombada
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 44)  # espaço para a sombra e a fita
        layout.addWidget(capa)

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.desenhar_sombra(pintor)
        self.desenhar_fita(pintor)
        pintor.end()

    def desenhar_sombra(self, pintor):
        area = QRectF(self.capa.geometry())
        pintor.setPen(Qt.PenStyle.NoPen)
        pintor.setBrush(QColor(0, 0, 0, 7))  # preto quase transparente
        for passo in range(14, 0, -2):
            # cada volta é um pouco maior; somadas, escurecem perto da capa
            pintor.drawRoundedRect(area.adjusted(-passo, -passo + 6, passo, passo + 6),
                                   18 + passo, 18 + passo)

    def desenhar_fita(self, pintor):
        capa = QRectF(self.capa.geometry())
        centro = self.lombada.mapTo(self, self.lombada.rect().center())
        x = centro.x() + 14          # sai logo à direita da lombada
        topo = capa.bottom() - 30    # começa escondida atrás da capa
        fim = capa.bottom() + 34     # pendura para fora do livro
        meia = 7                     # metade da largura da fita
        caminho = QPainterPath()
        caminho.moveTo(x - meia, topo)
        caminho.lineTo(x + meia, topo)
        caminho.lineTo(x + meia, fim)
        caminho.lineTo(x, fim - 8)   # corte em V na ponta
        caminho.lineTo(x - meia, fim)
        caminho.closeSubpath()
        pintor.setPen(Qt.PenStyle.NoPen)
        pintor.setBrush(QColor(tema.cores_atuais()["fita"]))
        pintor.drawPath(caminho)