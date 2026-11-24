import math

import pygame

from carregador import carregar
from config import (
    TILE, COLUNAS, LINHAS, LARGURA, ALTURA,
    ABERTURA_H, ABERTURA_V, COR_PAREDE,
)
from layouts import LAYOUTS

# Símbolos em que o jogador não pode passar
SOLIDOS = {"#", "P", "F"}

# O "mapa do mundo". Cada sala diz para onde cada saída leva.
#
#   [6] <- [5] <- [4]
#                  ^
#   [1] -> [2] -> [3]
#
# "layout":     desenho opcional do interior (ver layouts.py)
# "bloqueadas": saídas fechadas até algo acontecer (ex.: pegar a arma)
# "itens":      lista de (tipo, x, y) em pixels
DADOS_SALAS = {
    1: {
        "nome": "Sala 1 - Inicio",
        "piso": (70, 70, 95),
        "saidas": {"leste": 2},
        "bloqueadas": ["leste"],
        "layout": LAYOUTS[1],
        "itens": [("arma", 12 * TILE + TILE // 2, 6 * TILE + TILE // 2)],
    },
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


def gerar_mapa(saidas, layout=None):
    """Paredes na borda com uma abertura em cada saída; o interior vem do layout."""
    mapa = []
    for l in range(LINHAS):
        linha = ""
        for c in range(COLUNAS):
            borda = l in (0, LINHAS - 1) or c in (0, COLUNAS - 1)
            if borda:
                aberto = (
                    ("norte" in saidas and l == 0 and c in ABERTURA_H)
                    or ("sul" in saidas and l == LINHAS - 1 and c in ABERTURA_H)
                    or ("oeste" in saidas and c == 0 and l in ABERTURA_V)
                    or ("leste" in saidas and c == COLUNAS - 1 and l in ABERTURA_V)
                )
                linha += "." if aberto else "#"
            else:
                linha += layout[l][c] if layout else "."
        mapa.append(linha)
    return mapa


# --- Desenho provisório dos tiles (usado quando não existe PNG em assets/) ---

def _tile_parede(superficie, x, y):
    img = carregar("parede")
    if img:
        superficie.blit(img, (x, y))
        return
    pygame.draw.rect(superficie, COR_PAREDE, (x, y, TILE, TILE))
    pygame.draw.line(superficie, (70, 70, 85), (x, y), (x + TILE - 1, y))            # luz em cima
    pygame.draw.line(superficie, (28, 28, 36), (x, y + TILE - 1), (x + TILE - 1, y + TILE - 1))


def _tile_tapete(superficie, x, y, esquerda_tem, direita_tem):
    img = carregar("tapete")
    if img:
        superficie.blit(img, (x, y))
        return
    pygame.draw.rect(superficie, (140, 32, 48), (x, y, TILE, TILE))
    pygame.draw.rect(superficie, (165, 45, 62), (x + 4, y, TILE - 8, TILE))
    if not esquerda_tem:
        pygame.draw.rect(superficie, (220, 180, 70), (x, y, 3, TILE))
    if not direita_tem:
        pygame.draw.rect(superficie, (220, 180, 70), (x + TILE - 3, y, 3, TILE))


def _tile_pilar(superficie, x, y):
    img = carregar("pilar")
    if img:
        superficie.blit(img, (x, y))
        return
    pygame.draw.rect(superficie, (40, 40, 52), (x + 5, y + TILE - 8, TILE - 10, 6))   # sombra
    pygame.draw.rect(superficie, (135, 135, 150), (x + 6, y + 4, TILE - 12, TILE - 8))
    pygame.draw.rect(superficie, (175, 175, 190), (x + 6, y + 4, 4, TILE - 8))        # brilho
    pygame.draw.rect(superficie, (100, 100, 115), (x + 3, y + 2, TILE - 6, 5))        # topo
    pygame.draw.rect(superficie, (100, 100, 115), (x + 3, y + TILE - 8, TILE - 6, 5)) # base


def _tile_braseiro(superficie, x, y):
    img = carregar("braseiro")
    if img:
        superficie.blit(img, (x, y))
        return
    pygame.draw.rect(superficie, (85, 85, 98), (x + 7, y + 16, TILE - 14, 10))        # bacia
    pygame.draw.rect(superficie, (55, 55, 66), (x + 7, y + 16, TILE - 14, 10), 2)
    pygame.draw.rect(superficie, (70, 70, 82), (x + 12, y + 24, TILE - 24, 6))        # haste


def _chama(superficie, x, y):
    """Chama animada do braseiro (só quando não há PNG; com PNG a imagem já tem fogo)."""
    t = pygame.time.get_ticks() / 110 + x
    altura = 10 + round(3 * math.sin(t))
    cx = x + TILE // 2
    topo = y + 16
    pygame.draw.polygon(superficie, (235, 110, 30),
                        [(cx - 7, topo), (cx, topo - altura - 3), (cx + 7, topo)])
    pygame.draw.polygon(superficie, (255, 210, 70),
                        [(cx - 4, topo), (cx, topo - altura + 2), (cx + 4, topo)])


class Item:
    """Um item no chão que o jogador pega ao encostar."""

    def __init__(self, tipo, x, y, tamanho=22):
        self.tipo = tipo
        self.rect = pygame.Rect(0, 0, tamanho, tamanho)
        self.rect.center = (x, y)
        self.coletado = False

    def desenhar(self, superficie):
        if self.coletado:
            return
        cx, cy = self.rect.center
        if self.tipo == "arma":
            balanco = round(2 * math.sin(pygame.time.get_ticks() / 250))  # flutua um pouco

            pedestal = carregar("pedestal")
            if pedestal:
                superficie.blit(pedestal, pedestal.get_rect(midbottom=(cx, cy + 22)))
            else:
                pygame.draw.rect(superficie, (110, 110, 120), (cx - 18, cy + 4, 36, 18))
                pygame.draw.rect(superficie, (80, 80, 90), (cx - 18, cy + 4, 36, 18), 2)

            arma_img = carregar("arma")
            if arma_img:
                superficie.blit(arma_img, arma_img.get_rect(center=(cx, cy - 8 - balanco)))
            else:
                y = cy - 6 - balanco
                pygame.draw.rect(superficie, (220, 225, 235), (cx - 3, y - 14, 6, 18))  # lâmina
                pygame.draw.rect(superficie, (230, 190, 60), (cx - 8, y + 4, 16, 4))    # guarda
                pygame.draw.rect(superficie, (130, 80, 40), (cx - 2, y + 8, 4, 8))      # cabo
        else:
            pygame.draw.rect(superficie, (255, 0, 255), self.rect)  # item desconhecido


class Sala:
    def __init__(self, id_sala, dados):
        self.id = id_sala
        self.nome = dados["nome"]
        self.piso = dados["piso"]
        self.saidas = dados["saidas"]
        self.layout = dados.get("layout")
        self.bloqueadas = set(dados.get("bloqueadas", []))
        self.itens = [Item(*i) for i in dados.get("itens", [])]
        self.mapa = []
        self.fundo = None
        self.braseiros = []
        self.atualizar_mapa()

    def saidas_abertas(self):
        return {lado: destino for lado, destino in self.saidas.items()
                if lado not in self.bloqueadas}

    def atualizar_mapa(self):
        self.mapa = gerar_mapa(self.saidas_abertas(), self.layout)
        self._montar_fundo()

    def _montar_fundo(self):
        """Desenha o cenário parado uma vez só (o que se mexe é desenhado a cada quadro)."""
        self.fundo = pygame.Surface((LARGURA, ALTURA))
        self.fundo.fill(self.piso)
        piso = carregar("piso")
        self.braseiros = []

        for l, linha in enumerate(self.mapa):
            for c, simbolo in enumerate(linha):
                x, y = c * TILE, l * TILE
                if piso:
                    self.fundo.blit(piso, (x, y))
                if simbolo == "#":
                    _tile_parede(self.fundo, x, y)
                elif simbolo == "C":
                    _tile_tapete(self.fundo, x, y,
                                 linha[c - 1] == "C", linha[c + 1] == "C")
                elif simbolo == "P":
                    _tile_pilar(self.fundo, x, y)
                elif simbolo == "F":
                    _tile_braseiro(self.fundo, x, y)
                    if carregar("braseiro") is None:
                        self.braseiros.append((x, y))

    def desbloquear(self, lado):
        self.bloqueadas.discard(lado)
        self.atualizar_mapa()

    def tiles_solidos_perto(self, rect):
        resultado = []
        for linha in range(rect.top // TILE, rect.bottom // TILE + 1):
            for coluna in range(rect.left // TILE, rect.right // TILE + 1):
                if 0 <= linha < LINHAS and 0 <= coluna < COLUNAS:
                    if self.mapa[linha][coluna] in SOLIDOS:
                        resultado.append(pygame.Rect(coluna * TILE, linha * TILE, TILE, TILE))
        return resultado

    def desenhar(self, superficie):
        superficie.blit(self.fundo, (0, 0))
        for x, y in self.braseiros:
            _chama(superficie, x, y)
        for item in self.itens:
            item.desenhar(superficie)


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