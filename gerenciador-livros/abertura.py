"""Tela de abertura: um livro que se abre antes da janela principal aparecer."""

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QTimer, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget


class AberturaLivro(QWidget):
    terminou = Signal()  # avisa o main.py que a abertura acabou

    def __init__(self, cores):
        super().__init__()
        self.cores = cores          # as cores do tema escolhido
        self.progresso = 0.0        # 0 = livro fechado, 1 = livro aberto
        self.terminado = False

        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(480, 320)
        self.setToolTip("Clique para pular")
        tela = QApplication.primaryScreen().availableGeometry()
        self.move(tela.center() - self.rect().center())

        self.animacao = QVariantAnimation(self)
        self.animacao.setStartValue(0.0)
        self.animacao.setEndValue(1.0)
        self.animacao.setDuration(1600)
        self.animacao.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animacao.valueChanged.connect(self.avancar)
        self.animacao.finished.connect(lambda: QTimer.singleShot(400, self.concluir))

    def iniciar(self):
        self.show()
        QTimer.singleShot(400, self.animacao.start)  # mostra o livro fechado por um instante

    def avancar(self, valor):
        self.progresso = valor
        self.update()  # pede ao Qt para redesenhar (chama o paintEvent)

    def concluir(self):
        if self.terminado:
            return
        self.terminado = True
        self.animacao.stop()
        self.terminou.emit()

    def mousePressEvent(self, evento):
        self.concluir()

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)

        # fundo com cantos arredondados
        pintor.setPen(Qt.PenStyle.NoPen)
        pintor.setBrush(QColor(self.cores["fundo"]))
        pintor.drawRoundedRect(QRectF(self.rect()), 16, 16)

        largura_pagina = 150
        altura = 190
        lombada = self.width() / 2
        topo = 40

        # página direita: fica embaixo da capa e aparece quando ela abre
        self.desenhar_pagina(pintor, QRectF(lombada, topo, largura_pagina, altura))

        if self.progresso < 0.5:
            # primeira metade: a capa gira e fica cada vez mais estreita
            largura_capa = largura_pagina * (1 - 2 * self.progresso)
            self.desenhar_capa(pintor, QRectF(lombada, topo, largura_capa, altura))
        else:
            # segunda metade: a página esquerda vai surgindo
            largura_esquerda = largura_pagina * (2 * self.progresso - 1)
            area = QRectF(lombada - largura_esquerda, topo, largura_esquerda, altura)
            self.desenhar_pagina(pintor, area)

        # lombada no meio
        pintor.setPen(Qt.PenStyle.NoPen)
        pintor.setBrush(QColor(self.cores["borda"]))
        pintor.drawRect(QRectF(lombada - 2, topo, 4, altura))

        # nome do programa e dica
        fonte = pintor.font()
        fonte.setPointSize(14)
        fonte.setBold(True)
        pintor.setFont(fonte)
        pintor.setPen(QColor(self.cores["texto"]))
        pintor.drawText(QRectF(0, topo + altura + 14, self.width(), 28),
                        Qt.AlignmentFlag.AlignCenter, "Gerenciador de Livros")
        fonte.setPointSize(9)
        fonte.setBold(False)
        pintor.setFont(fonte)
        pintor.setPen(QColor(self.cores["texto_suave"]))
        pintor.drawText(QRectF(0, topo + altura + 44, self.width(), 20),
                        Qt.AlignmentFlag.AlignCenter, "clique para pular")
        pintor.end()

    def desenhar_capa(self, pintor, area):
        pintor.setPen(Qt.PenStyle.NoPen)
        pintor.setBrush(QColor(self.cores["primaria"]))
        pintor.drawRoundedRect(area, 4, 4)
        if area.width() > 24:
            # filete decorativo da capa
            pintor.setPen(QPen(QColor(self.cores["primaria_texto"]), 1))
            pintor.setBrush(Qt.BrushStyle.NoBrush)
            pintor.drawRect(area.adjusted(8, 8, -8, -8))

    def desenhar_pagina(self, pintor, area):
        pintor.setPen(QPen(QColor(self.cores["borda"]), 1))
        pintor.setBrush(QColor(self.cores["superficie"]))
        pintor.drawRect(area)
        if area.width() > 40:
            # linhas que imitam o texto da página
            pintor.setPen(QPen(QColor(self.cores["texto_suave"]), 1))
            y = area.top() + 24
            while y < area.bottom() - 16:
                pintor.drawLine(QPointF(area.left() + 14, y), QPointF(area.right() - 14, y))
                y += 14