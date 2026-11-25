"""Transição de sala com efeito de pixelização."""

import pygame

from .config import LARGURA, ALTURA, BLOCOS, DURACAO_TRANSICAO


class Transicao:
    """Fluxo:
    1. "saindo": a imagem atual vai ficando cada vez mais pixelada.
    2. No pico do efeito, avisamos o main para trocar de sala.
    3. "entrando": a nova sala começa pixelada e volta ao normal.
    """

    def __init__(self):
        self.estado = None   # None, "saindo" ou "entrando"
        self.timer = 0.0
        self.sala_destino = None

    @property
    def ativa(self):
        return self.estado is not None

    def iniciar(self, sala_destino):
        self.estado = "saindo"
        self.timer = 0.0
        self.sala_destino = sala_destino

    def atualizar(self, dt):
        """Avança o efeito. Devolve True só no instante em que a sala deve mudar."""
        if not self.ativa:
            return False

        self.timer += dt
        if self.timer < DURACAO_TRANSICAO:
            return False

        # Cada etapa dura DURACAO_TRANSICAO; zeramos o timer para a próxima.
        self.timer = 0.0
        if self.estado == "saindo":
            self.estado = "entrando"
            return True   # a tela está bem pixelada: escondemos a troca aqui

        self.estado = None
        return False

    def desenhar(self, origem, destino):
        """Desenha o canvas na tela, aplicando pixelização quando ativa."""
        if not self.ativa:
            destino.blit(origem, (0, 0))
            return

        # Progresso de 0.0 a quase 1.0 dentro da etapa atual.
        progresso = min(self.timer / DURACAO_TRANSICAO, 0.999)
        etapa = int(progresso * len(BLOCOS))

        # Na entrada, inverte a sequência para desfazer a pixelização.
        if self.estado == "entrando":
            etapa = len(BLOCOS) - 1 - etapa

        bloco = BLOCOS[etapa]
        if bloco == 1:
            destino.blit(origem, (0, 0))
            return

        # Reduz a imagem e amplia de volta com scale para criar blocos visíveis.
        pequena = pygame.transform.smoothscale(
            origem, (max(1, LARGURA // bloco), max(1, ALTURA // bloco))
        )
        destino.blit(pygame.transform.scale(pequena, (LARGURA, ALTURA)), (0, 0))
