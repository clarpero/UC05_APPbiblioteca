"""Gera a textura de papel do tema Biblioteca (imagens/papel.png).

A imagem é feita por código, então não depende de imagem de terceiros.
Rode uma vez, na pasta do projeto:
    python gerar_textura.py
"""

import random
from pathlib import Path

from PySide6.QtGui import QColor, QImage

TAMANHO = 256                 # a imagem se repete lado a lado no fundo da página
BASE = QColor("#fbf6ee")      # cor de papel do tema Biblioteca


def limitar(valor):
    return max(0, min(255, valor))


def gerar():
    sorteio = random.Random(42)  # semente fixa: sempre gera a mesma textura
    imagem = QImage(TAMANHO, TAMANHO, QImage.Format.Format_RGB32)
    for y in range(TAMANHO):
        for x in range(TAMANHO):
            variacao = sorteio.randint(-14, 5)       # grão fino do papel
            if sorteio.random() < 0.01:
                variacao -= sorteio.randint(15, 30)  # pontinhos de fibra
            cor = QColor(
                limitar(BASE.red() + variacao),
                limitar(BASE.green() + variacao),
                limitar(BASE.blue() + variacao - 3),
            )
            imagem.setPixelColor(x, y, cor)

    pasta = Path(__file__).with_name("imagens")
    pasta.mkdir(exist_ok=True)
    destino = pasta / "papel.png"
    imagem.save(str(destino))
    print(f"Textura salva em {destino}")


if __name__ == "__main__":
    gerar()