"""Salas do jogo: dados, mapa de colisão, itens e portal."""

import math
from pathlib import Path

import pygame

from .config import (
    TILE, COLUNAS, LINHAS, LARGURA, ALTURA,
    ESPESSURA_BORDA_EO, ESPESSURA_BORDA_NS,
    COR_PAREDE, FRAMES_REPETICAO_PORTAL,
)
from .sprites import fatiar_spritesheet

# A troca de sala acontece só pelos portais. Todos começam desligados;
# F6 liga o portal da sala atual na frente do jogador.
# "itens": lista de (tipo, x, y) em pixels.


def dados_portal(destino, ativo=False):
    """Configuração padrão do portal, usada por todas as salas."""
    return {
        "spritesheet": "assets/images/portal.png",
        "colunas": 4,
        "linhas": 3,
        "pos": (LARGURA // 2, ALTURA // 2),
        "destino": destino,
        "ativo": ativo,
        # A folha tem frames de 384x341; 80x71 mantém essa proporção.
        "escala": (80, 71),
    }


DADOS_SALAS = {
    1: {
        "nome": "Sala 1 - Inicio",
        "piso": (70, 70, 95),
        # Portal no centro da tela. A espada fica alinhada com ele, 4 tiles
        # abaixo da parede norte (tile 7).
        "itens": [(
            "espada",
            LARGURA // 2,
            (ESPESSURA_BORDA_NS + 4) * TILE + TILE // 2,
        )],
        "fundo": "assets/images/mapa inicial.png",
        # Ativado ao pegar a espada.
        "portal": dados_portal(2),
    },
    2: {
        "nome": "Sala 2 - Tutorial",
        "piso": (70, 95, 70),
        "fundo": "assets/images/sala2.png",
        # Paredes internas: (coluna, linha) em tiles de 25px.
        # Esquerda: coluna 3 (linhas 5-14) e coluna 4 (linhas 8-13).
        # Direita: espelho nas colunas 28 e 27, mesmas linhas.
        "paredes": (
            [(3, linha) for linha in range(5, 15)]
            + [(4, linha) for linha in range(8, 14)]
            + [(28, linha) for linha in range(5, 15)]
            + [(27, linha) for linha in range(8, 14)]
        ),
        "portal": dados_portal(3),
    },
    3: {
        "nome": "Sala 3 - Chefe 1",
        "piso": (95, 70, 70),
        "portal": dados_portal(4),
    },
    4: {
        "nome": "Sala 4 - Chefe 2",
        "piso": (95, 85, 60),
        "portal": dados_portal(5),
    },
    5: {
        "nome": "Sala 5 - Chefe 3",
        "piso": (85, 60, 95),
        "portal": dados_portal(6),
    },
    6: {
        "nome": "Sala 6 - Princesa",
        "piso": (95, 75, 90),
        # Volta para a sala 1.
        "portal": dados_portal(1),
    },
}


def gerar_mapa():
    """Mapa em strings: '#' é parede, '.' é chão. Toda a borda é sólida."""
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
            linha_mapa += "#" if eh_borda else "."
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

            # O balanço usa pygame.time.get_ticks(), independente do FPS.
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
        ativo=False,
        escala=(80, 71),
        duracao_frame=0.12,
        frames_repeticao=FRAMES_REPETICAO_PORTAL,
        raiz_projeto=None,
    ):
        caminho = Path(spritesheet)
        if raiz_projeto and not caminho.is_absolute():
            caminho = Path(raiz_projeto) / caminho

        sheet = pygame.image.load(str(caminho)).convert_alpha()
        frames = fatiar_spritesheet(sheet, colunas, linhas)
        self.frames = [pygame.transform.scale(frame, escala) for frame in frames]
        # Depois de chegar ao fim, a animação volta ao primeiro dos frames
        # finais. Assim a "abertura" toca uma vez e o portal fica pulsando.
        self.inicio_repeticao = max(0, len(self.frames) - frames_repeticao)
        self.indice_frame = 0
        self.timer_animacao = 0.0
        self.duracao_frame = duracao_frame
        self.rect = self.frames[0].get_rect(center=pos)
        self.destino = destino
        self.ativo = ativo

    def atualizar(self, dt):
        if not self.ativo:
            return

        self.timer_animacao += dt
        # while compensa atrasos sem perder frames.
        while self.timer_animacao >= self.duracao_frame:
            self.timer_animacao -= self.duracao_frame
            self.indice_frame += 1
            if self.indice_frame >= len(self.frames):
                # Após a abertura, só os últimos frames se repetem.
                self.indice_frame = self.inicio_repeticao

    def desenhar(self, superficie):
        if not self.ativo:
            return
        superficie.blit(self.frames[self.indice_frame], self.rect)


class Sala:
    def __init__(self, id_sala, dados, raiz_projeto=None):
        self.id = id_sala
        self.nome = dados["nome"]
        self.piso = dados["piso"]
        self.itens = [Item(*i) for i in dados.get("itens", [])]

        # Paredes internas em pixels: colidem, mas não são desenhadas (F2 as mostra).
        self.paredes = [
            pygame.Rect(coluna * TILE, linha * TILE, TILE, TILE)
            for coluna, linha in dados.get("paredes", [])
        ]

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

        # O mapa é gerado uma vez: as bordas nunca mudam.
        self.mapa = gerar_mapa()

    def tiles_solidos_perto(self, rect):
        """Tiles sólidas em contato: vizinhança do Rect e paredes internas."""
        resultado = []
        for linha in range(rect.top // TILE, rect.bottom // TILE + 1):
            for coluna in range(rect.left // TILE, rect.right // TILE + 1):
                if 0 <= linha < LINHAS and 0 <= coluna < COLUNAS:
                    if self.mapa[linha][coluna] == "#":
                        resultado.append(pygame.Rect(coluna * TILE, linha * TILE, TILE, TILE))

        for parede in self.paredes:
            if parede.colliderect(rect):
                resultado.append(parede)
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

        if self.portal:
            self.portal.desenhar(superficie)

        for item in self.itens:
            item.desenhar(superficie)


def criar_salas(raiz_projeto=None):
    """Monta todas as salas uma vez, no início do jogo."""
    raiz = Path(raiz_projeto) if raiz_projeto else Path(__file__).resolve().parent.parent
    return {id_sala: Sala(id_sala, dados, raiz) for id_sala, dados in DADOS_SALAS.items()}
