"""Salas do jogo: dados, geração do mapa e desenho."""

import pygame

from config import (
    TILE, COLUNAS, LINHAS, LARGURA, ALTURA,
    ABERTURA_H, ABERTURA_V, COR_PAREDE,
)

# O "mapa do mundo". Cada sala diz para onde cada saída leva.
#
#   [6] <- [5] <- [4]
#                  ^
#   [1] -> [2] -> [3]
#
DADOS_SALAS = {
    1: {"nome": "Sala 1 - Inicio", "piso": (70, 70, 95),
        "saidas": {"leste": 2}},
    2: {"nome": "Sala 2 - Tutorial", "piso": (70, 95, 70),
        "saidas": {"oeste": 1, "leste": 3}},
    3: {"nome": "Sala 3 - Chefe 1", "piso": (95, 70, 70),
        "saidas": {"oeste": 2, "norte": 4}},
    4: {"nome": "Sala 4 - Chefe 2", "piso": (95, 85, 60),
        "saidas": {"sul": 3, "oeste": 5}},
    5: {"nome": "Sala 5 - Chefe 3", "piso": (85, 60, 95),
        "saidas": {"leste": 4, "oeste": 6}},
    6: {"nome": "Sala 6 - Princesa", "piso": (95, 75, 90),
        "saidas": {"leste": 5}},
}


def gerar_mapa(saidas):
    """Sala vazia: paredes na borda e uma abertura em cada saída."""
    mapa = []
    for l in range(LINHAS):
        linha = ""
        for c in range(COLUNAS):
            borda = l in (0, LINHAS - 1) or c in (0, COLUNAS - 1)
            aberto = (
                ("norte" in saidas and l == 0 and c in ABERTURA_H)
                or ("sul" in saidas and l == LINHAS - 1 and c in ABERTURA_H)
                or ("oeste" in saidas and c == 0 and l in ABERTURA_V)
                or ("leste" in saidas and c == COLUNAS - 1 and l in ABERTURA_V)
            )
            linha += "#" if borda and not aberto else "."
        mapa.append(linha)
    return mapa


class Sala:
    def __init__(self, id_sala, dados):
        self.id = id_sala
        self.nome = dados["nome"]
        self.piso = dados["piso"]
        self.saidas = dados["saidas"]
        self.mapa = gerar_mapa(self.saidas)

    def tiles_solidos_perto(self, rect):
        resultado = []
        for linha in range(rect.top // TILE, rect.bottom // TILE + 1):
            for coluna in range(rect.left // TILE, rect.right // TILE + 1):
                if 0 <= linha < LINHAS and 0 <= coluna < COLUNAS:
                    if self.mapa[linha][coluna] == "#":
                        resultado.append(pygame.Rect(coluna * TILE, linha * TILE, TILE, TILE))
        return resultado

    def desenhar(self, superficie):
        superficie.fill(self.piso)
        for l, linha in enumerate(self.mapa):
            for c, simbolo in enumerate(linha):
                if simbolo == "#":
                    pygame.draw.rect(superficie, COR_PAREDE, (c * TILE, l * TILE, TILE, TILE))


def criar_salas():
    return {id_sala: Sala(id_sala, dados) for id_sala, dados in DADOS_SALAS.items()}


def verificar_saida(rect):
    """Se o jogador passou da borda da tela, diz por qual lado."""
    if rect.centerx < 0:
        return "oeste"
    if rect.centerx > LARGURA:
        return "leste"
    if rect.centery < 0:
        return "norte"
    if rect.centery > ALTURA:
        return "sul"
    return None
