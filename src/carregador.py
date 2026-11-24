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

# Cache: a mesma imagem é pedida 60 vezes por segundo, mas só precisa ser lida uma.
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

                # scale() (e não smoothscale) mantém os pixels nítidos.
                quadro = pygame.transform.scale(
                    quadro, (largura * ESCALA, altura * ESCALA)
                )

                # O fundo branco da arte vira transparência. O PNG também tem
                # alpha real nas bordas; o colorkey só remove o branco do desenho.
                quadro.set_colorkey((255, 255, 255))

                quadros.append(quadro)
        except (pygame.error, ValueError, IndexError) as erro:
            print(f"Aviso: problema em {nome} (.png/.txt): {erro}")
            quadros = None

    # Guardamos até o resultado None: assim não tentamos de novo a cada frame.
    _cache_quadros[nome] = quadros
    return quadros


def relatorio(nomes):
    """Linhas de texto dizendo quais arquivos o jogo encontrou.

    Ajuda a achar erro de pasta ou de nome antes de culpar a animação.
    """
    linhas = [f"Pasta de imagens: {PASTA}"]
    if not PASTA.is_dir():
        linhas.append("  PROBLEMA: essa pasta nao existe!")
        return linhas

    for nome in nomes:
        for extensao in (".png", ".txt"):
            arquivo = PASTA / f"{nome}{extensao}"
            status = "ok" if arquivo.exists() else "FALTA"
            linhas.append(f"  [{status}] {arquivo.name}")
    return linhas
