# -*- coding: utf-8 -*-
"""Desenha o ícone do programa: um cupom fiscal com a borda serrilhada."""
import os

from PIL import Image, ImageDraw

FUNDO = (14, 16, 14, 255)
PAPEL = (53, 168, 122, 255)
LINHA = (14, 16, 14, 255)


def desenha(lado: int) -> Image.Image:
    e = 8  # desenha grande e reduz, para as bordas saírem limpas
    L = lado * e
    img = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    raio = int(L * 0.20)
    d.rounded_rectangle([0, 0, L - 1, L - 1], radius=raio, fill=FUNDO)

    # corpo do cupom
    m = int(L * 0.22)
    topo = int(L * 0.16)
    base = int(L * 0.74)
    d.rectangle([m, topo, L - m, base], fill=PAPEL)

    # serrilha de baixo, como papel rasgado
    dentes = 5
    larg = (L - 2 * m) / dentes
    alt = int(L * 0.09)
    for i in range(dentes):
        x0 = m + i * larg
        d.polygon([(x0, base), (x0 + larg / 2, base + alt), (x0 + larg, base)], fill=PAPEL)

    # linhas de texto
    lx0 = m + int(L * 0.07)
    lx1 = L - m - int(L * 0.07)
    esp = int(L * 0.028)
    for k, largura in enumerate([1.0, 1.0, 0.62]):
        y = topo + int(L * 0.13) + k * int(L * 0.135)
        d.rounded_rectangle(
            [lx0, y, lx0 + (lx1 - lx0) * largura, y + esp],
            radius=esp // 2, fill=LINHA)

    return img.resize((lado, lado), Image.LANCZOS)


def main():
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "recursos", "slt.ico")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    tamanhos = [16, 24, 32, 48, 64, 128, 256]
    imagens = [desenha(t) for t in tamanhos]
    imagens[-1].save(destino, format="ICO",
                     sizes=[(t, t) for t in tamanhos], append_images=imagens[:-1])
    print("ícone gerado:", destino, os.path.getsize(destino), "bytes")


if __name__ == "__main__":
    main()
