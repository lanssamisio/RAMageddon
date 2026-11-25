"""Carregador das imagens do jogo.

As sprites ficam em assets/images. Cada animação tem um .png (a folha com
todos os quadros) e um .txt com as coordenadas de cada quadro da folha.
Se algum arquivo faltar, devolvemos None e o jogador usa um desenho provisório.
"""

from pathlib import Path

import pygame

from .config import ESCALA

# __file__ está dentro de src/, então parent.parent é a raiz do projeto.
RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "assets" / "images"

# Cache: cada imagem é lida uma vez e reaproveitada nos frames seguintes.
_cache_quadros = {}


def ler_coordenadas(caminho):
    """Lê o .txt com uma linha por quadro: nome,x,y,largura,altura.

    A ordem das linhas é a ordem dos quadros: a primeira é o número 0.
    """
    quadros = []
    with open(caminho, encoding="utf-8-sig") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha:
                continue
            nome, x, y, largura, altura = linha.rsplit(",", 4)
            quadros.append((nome.strip(), int(x), int(y), int(largura), int(altura)))
    return quadros


def carregar_quadros(nome):
    """Devolve os quadros de assets/images/<nome>.png já ampliados, ou None."""
    if nome in _cache_quadros:
        return _cache_quadros[nome]

    quadros = None
    caminho_png = PASTA / f"{nome}.png"
    caminho_txt = PASTA / f"{nome}.txt"

    if caminho_png.exists() and caminho_txt.exists():
        try:
            folha = pygame.image.load(str(caminho_png))
            # convert_alpha() exige que a janela já exista.
            if pygame.display.get_surface() is not None:
                folha = folha.convert_alpha()

            quadros = []
            for _, x, y, largura, altura in ler_coordenadas(caminho_txt):
                # copy() solta a referência à folha inteira.
                quadro = folha.subsurface(pygame.Rect(x, y, largura, altura)).copy()

                # scale() mantém os pixels nítidos.
                quadro = pygame.transform.scale(
                    quadro, (largura * ESCALA, altura * ESCALA)
                )

                # Colorkey transforma o fundo branco da arte em transparência.
                quadro.set_colorkey((255, 255, 255))

                quadros.append(quadro)
        except (pygame.error, ValueError, IndexError) as erro:
            print(f"Aviso: problema em {nome} (.png/.txt): {erro}")
            quadros = None

    # O resultado None também é guardado, para não tentar de novo depois.
    _cache_quadros[nome] = quadros
    return quadros
