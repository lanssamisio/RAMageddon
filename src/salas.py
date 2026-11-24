"""Salas do jogo: dados, mapa de colisão, itens e portal."""

import math
from pathlib import Path

import pygame

from .config import (
    TILE, COLUNAS, LINHAS, LARGURA, ALTURA,
    ABERTURA_H, ABERTURA_V, ESPESSURA_BORDA_EO, ESPESSURA_BORDA_NS,
    COR_PAREDE, DEBUG_COLISAO,
)
from .sprites import fatiar_spritesheet

# O "mapa do mundo". Cada sala diz para onde cada saída leva.
#
#   [6] <- [5] <- [4]
#                  ^
#   [1] -> [2] -> [3]
#
# "itens": lista de (tipo, x, y) em pixels.
DADOS_SALAS = {
    1: {
        "nome": "Sala 1 - Inicio",
        "piso": (70, 70, 95),
        "saidas": {},
        "itens": [("espada", 12 * TILE + TILE // 2, 6 * TILE + TILE // 2)],
        "fundo": "assets/images/mapa inicial.png",
        "portal": {
            "spritesheet": "assets/images/portal.png",
            "colunas": 4,
            "linhas": 3,
            "pos": (12 * TILE + TILE // 2, 10 * TILE + TILE // 2),
            "destino": 2,
            "lado_entrada": "centro",
            "ativo": False,
            # A folha tem frames de 384x341; 80x71 mantém essa proporção.
            "escala": (80, 71),
        },
    },
    2: {
        "nome": "Sala 2 - Tutorial",
        "piso": (70, 95, 70),
        "saidas": {"leste": 3},
    },
    3: {
        "nome": "Sala 3 - Chefe 1",
        "piso": (95, 70, 70),
        "saidas": {"oeste": 2, "norte": 4},
    },
    4: {
        "nome": "Sala 4 - Chefe 2",
        "piso": (95, 85, 60),
        "saidas": {"sul": 3, "oeste": 5},
    },
    5: {
        "nome": "Sala 5 - Chefe 3",
        "piso": (85, 60, 95),
        "saidas": {"leste": 4, "oeste": 6},
    },
    6: {
        "nome": "Sala 6 - Princesa",
        "piso": (95, 75, 90),
        "saidas": {"leste": 5},
    },
}


def gerar_mapa(saidas):
    """Sala vazia: paredes na borda e uma abertura em cada saída.

    O mapa é uma lista de strings: '#' é parede e '.' é chão. Assim a colisão
    vira uma simples consulta por linha/coluna.
    """
    mapa = []

    for linha in range(LINHAS):
        linha_mapa = ""
        for coluna in range(COLUNAS):
            eh_borda = (
                linha < ESPESSURA_BORDA_NS
                or linha >= LINHAS - ESPESSURA_BORDA_NS
                or coluna < ESPESSURA_BORDA_EO
                or coluna >= COLUNAS - ESPESSURA_BORDA_EO
            )
            eh_abertura = (
                ("norte" in saidas and linha < ESPESSURA_BORDA_NS and coluna in ABERTURA_H)
                or ("sul" in saidas and linha >= LINHAS - ESPESSURA_BORDA_NS and coluna in ABERTURA_H)
                or ("oeste" in saidas and coluna < ESPESSURA_BORDA_EO and linha in ABERTURA_V)
                or ("leste" in saidas and coluna >= COLUNAS - ESPESSURA_BORDA_EO and linha in ABERTURA_V)
            )
            linha_mapa += "#" if eh_borda and not eh_abertura else "."
        mapa.append(linha_mapa)

    return mapa


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
        centro_x, centro_y = self.rect.center
        if self.tipo == "espada":
            # Pedestal de pedra
            pygame.draw.rect(superficie, (110, 110, 120), (centro_x - 18, centro_y + 4, 36, 18))
            pygame.draw.rect(superficie, (80, 80, 90), (centro_x - 18, centro_y + 4, 36, 18), 2)

            # A espada sobe e desce. O tempo vem do relógio do pygame (não de um
            # contador de frames), então o balanço não muda com o FPS.
            balanco = round(2 * math.cos(math.radians(pygame.time.get_ticks() / 4)))
            centro_y -= 6 + balanco
            pygame.draw.rect(superficie, (220, 225, 235), (centro_x - 3, centro_y - 14, 6, 18))   # lâmina
            pygame.draw.rect(superficie, (230, 190, 60), (centro_x - 8, centro_y + 4, 16, 4))     # guarda
            pygame.draw.rect(superficie, (130, 80, 40), (centro_x - 2, centro_y + 8, 4, 8))       # cabo
        else:
            pygame.draw.rect(superficie, (255, 0, 255), self.rect)  # item desconhecido


class Portal:
    """Portal animado que leva o jogador para outra sala."""

    def __init__(
        self,
        spritesheet,
        colunas,
        linhas,
        pos,
        destino,
        lado_entrada,
        ativo=False,
        escala=(80, 71),
        duracao_frame=0.12,
        raiz_projeto=None,
    ):
        caminho = Path(spritesheet)
        if raiz_projeto and not caminho.is_absolute():
            caminho = Path(raiz_projeto) / caminho

        sheet = pygame.image.load(str(caminho)).convert_alpha()
        frames = fatiar_spritesheet(sheet, colunas, linhas)
        self.frames = [pygame.transform.scale(frame, escala) for frame in frames]
        self.indice_frame = 0
        self.timer_animacao = 0.0
        self.duracao_frame = duracao_frame
        self.rect = self.frames[0].get_rect(center=pos)
        self.destino = destino
        self.lado_entrada = lado_entrada
        self.ativo = ativo

    def atualizar(self, dt):
        if not self.ativo:
            return

        self.timer_animacao += dt
        # while (e não if) para não perder frames se o jogo travar por um momento.
        while self.timer_animacao >= self.duracao_frame:
            self.timer_animacao -= self.duracao_frame
            self.indice_frame = (self.indice_frame + 1) % len(self.frames)

    def desenhar(self, superficie):
        if not self.ativo:
            return
        superficie.blit(self.frames[self.indice_frame], self.rect)


class Sala:
    def __init__(self, id_sala, dados, raiz_projeto=None):
        self.id = id_sala
        self.nome = dados["nome"]
        self.piso = dados["piso"]
        self.saidas = dados["saidas"]
        self.itens = [Item(*i) for i in dados.get("itens", [])]

        self.portal = None
        dados_portal = dados.get("portal")
        if dados_portal:
            self.portal = Portal(**dados_portal, raiz_projeto=raiz_projeto)

        self.fundo = None
        caminho_fundo = dados.get("fundo")
        if caminho_fundo:
            caminho = Path(caminho_fundo)
            if raiz_projeto and not caminho.is_absolute():
                caminho = Path(raiz_projeto) / caminho
            imagem = pygame.image.load(str(caminho)).convert()
            self.fundo = pygame.transform.scale(imagem, (LARGURA, ALTURA))

        # O mapa é gerado uma vez: as saídas de uma sala nunca mudam.
        self.mapa = gerar_mapa(self.saidas)

    def tiles_solidos_perto(self, rect):
        """Devolve só as tiles sólidas que encostam no retângulo.

        Procurar no mapa inteiro a cada frame seria desperdício; olhamos apenas
        as linhas/colunas que o retângulo ocupa (mais uma de margem).
        """
        resultado = []
        for linha in range(rect.top // TILE, rect.bottom // TILE + 1):
            for coluna in range(rect.left // TILE, rect.right // TILE + 1):
                if 0 <= linha < LINHAS and 0 <= coluna < COLUNAS:
                    if self.mapa[linha][coluna] == "#":
                        resultado.append(pygame.Rect(coluna * TILE, linha * TILE, TILE, TILE))
        return resultado

    def desenhar(self, superficie):
        if self.fundo:
            superficie.blit(self.fundo, (0, 0))
        else:
            superficie.fill(self.piso)
            for indice_linha, linha in enumerate(self.mapa):
                for indice_coluna, simbolo in enumerate(linha):
                    if simbolo == "#":
                        pygame.draw.rect(
                            superficie,
                            COR_PAREDE,
                            (indice_coluna * TILE, indice_linha * TILE, TILE, TILE),
                        )

        # Modo de ajuste: desenha um vermelho translúcido sobre as tiles sólidas.
        if DEBUG_COLISAO:
            overlay = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 90))
            for indice_linha, linha in enumerate(self.mapa):
                for indice_coluna, simbolo in enumerate(linha):
                    if simbolo == "#":
                        superficie.blit(overlay, (indice_coluna * TILE, indice_linha * TILE))

        if self.portal:
            self.portal.desenhar(superficie)

        for item in self.itens:
            item.desenhar(superficie)


def criar_salas(raiz_projeto=None):
    """Monta todas as salas uma vez, no início do jogo."""
    raiz = Path(raiz_projeto) if raiz_projeto else Path(__file__).resolve().parent.parent
    return {id_sala: Sala(id_sala, dados, raiz) for id_sala, dados in DADOS_SALAS.items()}


def verificar_saida(rect):
    """Se o jogador passou do centro da borda da tela, diz por qual lado."""
    if rect.centerx < 0:
        return "oeste"
    if rect.centerx > LARGURA:
        return "leste"
    if rect.centery < 0:
        return "norte"
    if rect.centery > ALTURA:
        return "sul"
    return None
