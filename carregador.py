"""Carregador de imagens (arquivo de código: fica ao lado do main.py).

Procura os arquivos PNG na PASTA "assets" (que guarda só imagens). Se a imagem
não existir, devolve None e o jogo usa um desenho provisório no lugar.
A arte é ampliada por ESCALA, sem borrar os pixels.
"""

import os

import pygame

from config import ESCALA

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_cache = {}


def carregar(nome):
    """Devolve a imagem assets/<nome>.png já ampliada, ou None se não existir."""
    if nome in _cache:
        return _cache[nome]

    imagem = None
    caminho = os.path.join(PASTA, nome + ".png")
    if os.path.exists(caminho):
        try:
            imagem = pygame.image.load(caminho)
            if pygame.display.get_surface() is not None:
                imagem = imagem.convert_alpha()
            imagem = pygame.transform.scale(
                imagem, (imagem.get_width() * ESCALA, imagem.get_height() * ESCALA)
            )
        except pygame.error as erro:
            print(f"Aviso: nao consegui carregar {caminho}: {erro}")
            imagem = None

    _cache[nome] = imagem
    return imagem


def relatorio():
    """Linhas de texto dizendo quais imagens o jogo encontrou (ajuda a achar erros de pasta ou nome)."""
    linhas = [f"Pasta de imagens: {PASTA}"]
    if not os.path.isdir(PASTA):
        linhas.append("  PROBLEMA: essa pasta nao existe! Crie a pasta 'assets' ao lado do main.py.")
        return linhas
    esperados = ["andar_baixo.png", "andar_baixo.txt"]
    for nome in esperados:
        achou = os.path.exists(os.path.join(PASTA, nome))
        linhas.append(f"  [{'ok' if achou else 'FALTA'}] {nome}")
    extras = sorted(set(os.listdir(PASTA)) - set(esperados))
    if extras:
        linhas.append("  Outros arquivos na pasta: " + ", ".join(extras))
    return linhas


# --- Folhas de sprites com arquivo de coordenadas ---------------------------

_cache_quadros = {}


def ler_coordenadas(caminho):
    """Lê o .txt com uma linha por quadro: nome,x,y,largura,altura.

    Devolve uma lista [(nome, x, y, largura, altura), ...] na ordem do arquivo.
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


def _tornar_fundo_transparente(imagem):
    """Se a folha tem fundo de cor sólida (ex.: branco), deixa esse fundo transparente.

    A cor do fundo é a do pixel do canto superior esquerdo da folha.
    Folhas que já têm fundo transparente ficam como estão.
    """
    canto = imagem.get_at((0, 0))
    if canto.a == 0:
        return
    cor_fundo = (canto.r, canto.g, canto.b)
    for x in range(imagem.get_width()):
        for y in range(imagem.get_height()):
            pixel = imagem.get_at((x, y))
            if (pixel.r, pixel.g, pixel.b) == cor_fundo and pixel.a > 0:
                imagem.set_at((x, y), (pixel.r, pixel.g, pixel.b, 0))


def carregar_quadros(nome):
    """Carrega assets/<nome>.png e corta os quadros pelo arquivo assets/<nome>.txt.

    Devolve uma lista de imagens já ampliadas, na ordem do .txt,
    ou None se os arquivos não existirem (ou estiverem com erro).
    """
    if nome in _cache_quadros:
        return _cache_quadros[nome]

    quadros = None
    caminho_png = os.path.join(PASTA, nome + ".png")
    caminho_txt = os.path.join(PASTA, nome + ".txt")
    if os.path.exists(caminho_png) and os.path.exists(caminho_txt):
        try:
            folha = pygame.image.load(caminho_png)
            if pygame.display.get_surface() is not None:
                folha = folha.convert_alpha()
            _tornar_fundo_transparente(folha)
            quadros = []
            for _, x, y, largura, altura in ler_coordenadas(caminho_txt):
                recorte = folha.subsurface(pygame.Rect(x, y, largura, altura)).copy()
                quadros.append(pygame.transform.scale(recorte, (largura * ESCALA, altura * ESCALA)))
        except (pygame.error, ValueError) as erro:
            print(f"Aviso: problema em {nome} (.png/.txt): {erro}")
            quadros = None

    _cache_quadros[nome] = quadros
    return quadros
