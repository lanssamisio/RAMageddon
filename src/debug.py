"""Camadas de depuração ligadas por teclas de função.

Tudo é desenhado depois do jogo, então nada aqui mexe na física.

  F1  liga/desliga o debug inteiro
  F2  colisão: tiles sólidas, tiles encostando no jogador e aberturas
  F3  grade de tiles
  F4  entidades: hitbox do jogador, espada, itens e portal
  F5  informações: FPS, posição, direção, estado da transição
"""

import pygame

from .config import (
    TILE, COLUNAS, LINHAS, LARGURA, ALTURA,
    ABERTURA_H, ABERTURA_V, ESPESSURA_BORDA_EO, ESPESSURA_BORDA_NS,
)

# Tecla -> nome da camada. "ativo" é o interruptor geral.
TECLAS = {
    pygame.K_F1: "ativo",
    pygame.K_F2: "colisao",
    pygame.K_F3: "grade",
    pygame.K_F4: "entidades",
    pygame.K_F5: "info",
}

NOMES_CAMADAS = {
    "colisao": "colisao",
    "grade": "grade",
    "entidades": "entidades",
    "info": "info",
}


class Debug:
    def __init__(self):
        self.ativo = False

        # Camadas ligadas por padrão quando o debug é ativado com F1.
        # A grade fica desligada porque deixa a imagem de fundo ruidosa.
        self.camadas = {
            "colisao": True,
            "grade": False,
            "entidades": True,
            "info": True,
        }

    def tratar_tecla(self, tecla):
        """Consome F1..F5. Devolve True se a tecla era de debug."""
        if tecla not in TECLAS:
            return False

        chave = TECLAS[tecla]
        if chave == "ativo":
            self.ativo = not self.ativo
        else:
            self.camadas[chave] = not self.camadas[chave]
        return True

    def desenhar(self, superficie, fonte, jogador, sala, relogio, dt, transicao):
        """Desenha só as camadas ligadas, por cima de tudo menos do HUD."""
        if not self.ativo:
            return

        if self.camadas["colisao"]:
            self._desenhar_colisao(superficie, sala, jogador)
        if self.camadas["grade"]:
            self._desenhar_grade(superficie)
        if self.camadas["entidades"]:
            self._desenhar_entidades(superficie, jogador, sala)
        if self.camadas["info"]:
            self._desenhar_info(superficie, fonte, jogador, sala, relogio, dt, transicao)

    def _desenhar_colisao(self, superficie, sala, jogador):
        """Vermelho = parede, laranja = contato atual, verde = saída aberta."""
        parede = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        parede.fill((255, 0, 0, 80))

        for indice_linha, linha in enumerate(sala.mapa):
            for indice_coluna, simbolo in enumerate(linha):
                if simbolo == "#":
                    superficie.blit(parede, (indice_coluna * TILE, indice_linha * TILE))

        # As tiles que o jogador está tocando ganham contorno laranja.
        for tile in sala.tiles_solidos_perto(jogador.rect):
            if jogador.rect.colliderect(tile):
                pygame.draw.rect(superficie, (255, 170, 0), tile, 2)

        # As aberturas das saídas em verde, para conferir se estão alinhadas.
        abertura = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        abertura.fill((0, 255, 120, 45))

        for coluna in ABERTURA_H:
            for linha in range(ESPESSURA_BORDA_NS):
                if "norte" in sala.saidas:
                    superficie.blit(abertura, (coluna * TILE, linha * TILE))
                if "sul" in sala.saidas:
                    superficie.blit(abertura, (coluna * TILE, (LINHAS - 1 - linha) * TILE))

        for linha in ABERTURA_V:
            for coluna in range(ESPESSURA_BORDA_EO):
                if "oeste" in sala.saidas:
                    superficie.blit(abertura, (coluna * TILE, linha * TILE))
                if "leste" in sala.saidas:
                    superficie.blit(abertura, ((COLUNAS - 1 - coluna) * TILE, linha * TILE))

    def _desenhar_grade(self, superficie):
        """Linhas finas a cada TILE, em uma camada transparente."""
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for x in range(0, LARGURA + 1, TILE):
            pygame.draw.line(camada, (120, 200, 255, 70), (x, 0), (x, ALTURA))
        for y in range(0, ALTURA + 1, TILE):
            pygame.draw.line(camada, (120, 200, 255, 70), (0, y), (LARGURA, y))
        superficie.blit(camada, (0, 0))

    def _desenhar_entidades(self, superficie, jogador, sala):
        """Mostra retângulos que normalmente ficam invisíveis."""
        pygame.draw.rect(superficie, (0, 255, 120), jogador.rect, 2)

        area_espada = jogador.hitbox_espada()
        cor_espada = (255, 120, 0) if jogador.atacando else (255, 220, 0)
        pygame.draw.rect(superficie, cor_espada, area_espada, 2)

        # Setinha na direção para onde o personagem está virado.
        centro = pygame.Vector2(jogador.rect.center)
        ponta = centro + jogador.virado * 30
        pygame.draw.line(
            superficie, (255, 255, 0),
            (round(centro.x), round(centro.y)),
            (round(ponta.x), round(ponta.y)), 2,
        )

        for item in sala.itens:
            cor = (90, 90, 90) if item.coletado else (0, 200, 255)
            pygame.draw.rect(superficie, cor, item.rect, 2)

        if sala.portal:
            pygame.draw.rect(superficie, (255, 0, 220), sala.portal.rect, 2)

    def _desenhar_info(self, superficie, fonte, jogador, sala, relogio, dt, transicao):
        """Painel de texto com o estado do jogo no frame atual."""
        ligadas = ", ".join(
            NOMES_CAMADAS[nome]
            for nome, ligado in self.camadas.items()
            if ligado
        ) or "nenhuma"

        portal = "--"
        if sala.portal:
            portal = "ativo" if sala.portal.ativo else "inativo"

        direcao = (round(jogador.virado.x), round(jogador.virado.y))
        coletados = sum(1 for item in sala.itens if item.coletado)

        linhas = [
            "DEBUG  F1 geral | F2 colisao | F3 grade | F4 entidades | F5 info",
            f"camadas: {ligadas}",
            f"FPS {relogio.get_fps():.0f}    dt {dt * 1000:.1f} ms",
            f"sala {sala.id}    transicao {transicao.estado or '--'}",
            f"pos ({jogador.rect.x}, {jogador.rect.y})    dir {direcao}",
            (f"andando {jogador.andando}    atacando {jogador.atacando}"
             f"    espada {jogador.tem_espada}"),
            (f"anim {jogador.tempo_anim:.2f}s    itens {coletados}/{len(sala.itens)}"
             f"    portal {portal}"),
        ]

        # O fundo do painel acompanha o tamanho do maior texto.
        largura = max(fonte.size(linha)[0] for linha in linhas) + 12
        altura = len(linhas) * 18 + 12
        painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 170))
        superficie.blit(painel, (8, 34))

        for indice, linha in enumerate(linhas):
            imagem = fonte.render(linha, True, (215, 240, 255))
            superficie.blit(imagem, (14, 38 + indice * 18))
