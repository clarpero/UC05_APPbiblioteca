"""Virada de página: a animação que troca de tela dentro do livro."""

import math

from PySide6.QtCore import QEasingCurve, QRectF, QVariantAnimation
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

DURACAO_MS = 450


class ViradaPagina(QWidget):
    """Fica por cima das duas páginas e desenha a folha virando.

    Trabalha com duas "fotos" das páginas: a tela de antes e a de depois.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.hide()
        self.progresso = 0.0  # 0 = tela de antes, 1 = tela de depois
        self.animacao = QVariantAnimation(self)
        self.animacao.setStartValue(0.0)
        self.animacao.setEndValue(1.0)
        self.animacao.setDuration(DURACAO_MS)
        self.animacao.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animacao.valueChanged.connect(self.avancar)
        self.animacao.finished.connect(self.hide)

    def iniciar(self, area, antes, depois, meio, para_frente):
        """area: onde ficam as páginas; meio: posição da lombada dentro da área."""
        self.antes = antes
        self.depois = depois
        self.meio = meio
        self.para_frente = para_frente
        self.progresso = 0.0
        self.setGeometry(area)
        self.raise_()  # por cima das páginas
        self.show()
        self.animacao.start()

    def parar(self):
        self.animacao.stop()
        self.hide()

    def avancar(self, valor):
        self.progresso = valor
        self.update()

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        largura = self.width()
        meio = self.meio
        primeira_metade = self.progresso < 0.5
        # A folha vai estreitando até a lombada (1 -> 0) e depois alarga do outro lado (0 -> 1).
        abertura = abs(math.cos(self.progresso * math.pi))

        if self.para_frente:
            # A página direita vira para a esquerda, como ao avançar num livro.
            self.desenhar(pintor, self.antes, 0, meio, 0, meio)
            self.desenhar(pintor, self.depois, meio, largura, meio, largura)
            if primeira_metade:
                folha = (self.antes, meio, largura, meio, meio + (largura - meio) * abertura)
            else:
                folha = (self.depois, 0, meio, meio - meio * abertura, meio)
        else:
            # A página esquerda vira para a direita, como ao voltar.
            self.desenhar(pintor, self.depois, 0, meio, 0, meio)
            self.desenhar(pintor, self.antes, meio, largura, meio, largura)
            if primeira_metade:
                folha = (self.antes, 0, meio, meio - meio * abertura, meio)
            else:
                folha = (self.depois, meio, largura, meio, meio + (largura - meio) * abertura)

        imagem, origem_de, origem_ate, destino_de, destino_ate = folha
        self.desenhar(pintor, imagem, origem_de, origem_ate, destino_de, destino_ate)
        # Quanto mais "em pé" a folha, mais escura: dá a sensação de profundidade.
        sombra = QColor(0, 0, 0, int(110 * (1 - abertura)))
        pintor.fillRect(QRectF(destino_de, 0, destino_ate - destino_de, self.height()), sombra)
        pintor.end()

    def desenhar(self, pintor, imagem, origem_de, origem_ate, destino_de, destino_ate):
        """Copia uma faixa vertical da foto para uma faixa da tela (pode ser mais estreita)."""
        escala = imagem.devicePixelRatio()  # telas com zoom têm mais pixels por ponto
        origem = QRectF(origem_de * escala, 0,
                        (origem_ate - origem_de) * escala, imagem.height())
        destino = QRectF(destino_de, 0, destino_ate - destino_de, self.height())
        pintor.drawPixmap(destino, imagem, origem)
