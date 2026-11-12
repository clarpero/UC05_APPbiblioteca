"""Virada de página: a animação que troca de tela dentro do livro.

A folha é desenhada em tiras verticais finas. Cada tira tem a sua inclinação,
e é isso que faz a folha parecer curva, como papel de verdade.
"""

import math

from PySide6.QtCore import QEasingCurve, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import QWidget

DURACAO_MS = 650     # tempo da virada
TIRAS = 60           # em quantas tiras a folha é dividida (mais tiras = curva mais lisa)
CURVATURA = 0.9      # quanto a folha enverga no meio da virada (0 = folha dura)
PERSPECTIVA = 0.045  # quanto a parte levantada da folha "cresce" na direção de quem olha
MARGEM = 24          # sobra acima e abaixo das páginas, para a folha levantada caber


class ViradaPagina(QWidget):
    """Fica por cima das duas páginas e desenha a folha virando.

    Trabalha com duas "fotos" das páginas: a tela de antes e a de depois.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.hide()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
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
        self.setGeometry(area.adjusted(0, -MARGEM, 0, MARGEM))
        self.raise_()  # por cima das páginas
        self.show()
        self.animacao.start()

    def parar(self):
        self.animacao.stop()
        self.hide()

    def avancar(self, valor):
        self.progresso = valor
        self.update()

    # ---------- desenho ----------

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        largura = self.width()
        meio = self.meio

        # 1. As páginas paradas: de um lado a tela antiga, do outro a nova (que vai aparecendo).
        if self.para_frente:
            self.copiar(pintor, self.antes, 0, meio, 0, meio)
            self.copiar(pintor, self.depois, meio, largura, meio, largura)
        else:
            self.copiar(pintor, self.depois, 0, meio, 0, meio)
            self.copiar(pintor, self.antes, meio, largura, meio, largura)

        # 2. A folha que vira, por cima.
        self.desenhar_folha(pintor)
        pintor.end()

    def desenhar_folha(self, pintor):
        largura = self.width()
        meio = self.meio
        lado = 1 if self.para_frente else -1  # 1: a folha sai da direita; -1: sai da esquerda
        largura_saida = (largura - meio) if self.para_frente else meio
        largura_chegada = meio if self.para_frente else (largura - meio)

        # Ângulo da ponta solta da folha: 0 = deitada no lado de saída, pi = deitada na chegada.
        angulo = self.progresso * math.pi
        # A folha enverga mais no meio do caminho e fica reta no começo e no fim.
        envergadura = CURVATURA * math.sin(angulo)
        # As duas páginas têm larguras diferentes: a folha se ajusta aos poucos.
        comprimento = largura_saida + (largura_chegada - largura_saida) * self.progresso
        passo = comprimento / TIRAS

        distancia = 0.0  # quanto a tira se afastou da lombada, na horizontal
        altura = 0.0     # quanto a tira está levantada do livro
        for i in range(TIRAS):
            parte = (i + 0.5) / TIRAS  # 0 = junto da lombada, 1 = ponta solta
            # Perto da lombada a folha vem atrasada; a ponta vai na frente.
            inclinacao = angulo - envergadura * (1 - parte)
            nova_distancia = distancia + passo * math.cos(inclinacao)
            nova_altura = altura + passo * math.sin(inclinacao)

            # Passou de 90 graus: o que se vê é o verso da folha, com a tela nova.
            verso = inclinacao > math.pi / 2
            if verso:
                imagem, largura_pagina, sentido = self.depois, largura_chegada, -lado
            else:
                imagem, largura_pagina, sentido = self.antes, largura_saida, lado
            origem_a = meio + sentido * largura_pagina * i / TIRAS
            origem_b = meio + sentido * largura_pagina * (i + 1) / TIRAS

            destino_a = meio + lado * distancia
            destino_b = meio + lado * nova_distancia
            # Quanto mais levantada, maior a tira parece: as bordas de cima e de baixo fazem a curva.
            aumento = 1 + PERSPECTIVA * (altura + nova_altura) / 2 / max(largura_saida, 1)
            self.copiar(pintor, imagem, origem_a, origem_b, destino_a, destino_b, aumento)

            # Sombra na própria folha: tira "em pé" recebe menos luz. O verso fica um pouco mais escuro.
            forca = math.sin(inclinacao) * (85 if verso else 60)
            self.pintar(pintor, destino_a, destino_b, aumento, QColor(0, 0, 0, int(max(forca, 0))))

            distancia, altura = nova_distancia, nova_altura

        self.desenhar_sombra_no_livro(pintor, meio + lado * distancia, altura, lado)

    def desenhar_sombra_no_livro(self, pintor, x_ponta, altura, lado):
        """Sombra que a ponta da folha projeta na página de baixo."""
        tamanho = altura * 0.18  # folha mais alta = sombra mais comprida
        if tamanho < 1:
            return
        sentido = lado if x_ponta >= self.meio else -lado
        if not self.para_frente:
            sentido = -sentido
        degrade = QLinearGradient(x_ponta, 0, x_ponta + sentido * tamanho, 0)
        degrade.setColorAt(0, QColor(0, 0, 0, 55))
        degrade.setColorAt(1, QColor(0, 0, 0, 0))
        esquerda = min(x_ponta, x_ponta + sentido * tamanho)
        pintor.fillRect(QRectF(esquerda, MARGEM, tamanho, self.height() - 2 * MARGEM), degrade)

    def faixa(self, x_a, x_b, aumento):
        """Retângulo de uma tira na tela, entre x_a e x_b, já com o aumento da perspectiva."""
        esquerda, direita = min(x_a, x_b), max(x_a, x_b)
        altura_pagina = self.height() - 2 * MARGEM
        altura = altura_pagina * aumento
        topo = MARGEM - (altura - altura_pagina) / 2
        return QRectF(esquerda - 0.3, topo, direita - esquerda + 0.6, altura)  # 0.6: sem frestas

    def copiar(self, pintor, imagem, origem_a, origem_b, destino_a, destino_b, aumento=1.0):
        """Copia uma faixa vertical da foto para uma faixa da tela (pode ser mais estreita)."""
        escala = imagem.devicePixelRatio()  # telas com zoom têm mais pixels por ponto
        esquerda, direita = min(origem_a, origem_b), max(origem_a, origem_b)
        origem = QRectF(esquerda * escala, 0, (direita - esquerda) * escala, imagem.height())
        pintor.drawPixmap(self.faixa(destino_a, destino_b, aumento), imagem, origem)

    def pintar(self, pintor, x_a, x_b, aumento, cor):
        pintor.fillRect(self.faixa(x_a, x_b, aumento), cor)
