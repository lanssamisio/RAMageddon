import pygame

from config import LARGURA, ALTURA, BLOCOS, DURACAO_TRANSICAO


class Transicao:
    """Transição de sala com efeito de pixelização.

    Fluxo:
    1. "saindo": a imagem atual vai ficando cada vez mais pixelada.
    2. "trocar": no pico do efeito, o jogo troca de sala sem o jogador ver.
    3. "entrando": a nova sala começa pixelada e volta ao normal.
    """

    def __init__(self):
        self.estado = None   # None, "saindo" (pixelando) ou "entrando" (despixelando)
        self.timer = 0.0
        self.sala_destino = None
        self.lado_entrada = None

    @property
    def ativa(self):
        return self.estado is not None

    def iniciar(self, sala_destino, lado_entrada):
        self.estado = "saindo"
        self.timer = 0.0
        self.sala_destino = sala_destino
        self.lado_entrada = lado_entrada

    def atualizar(self, dt):
        """Avança a transição e sinaliza quando trocar de sala ou finalizar."""
        if not self.ativa:
            return None

        self.timer += dt
        if self.timer < DURACAO_TRANSICAO:
            return None

        # Cada etapa dura DURACAO_TRANSICAO.
        self.timer = 0.0
        if self.estado == "saindo":
            self.estado = "entrando"
            return "trocar"  # Momento seguro para trocar sala e reposicionar jogador.

        self.estado = None
        return "fim"

    def desenhar(self, origem, destino):
        """Desenha o canvas na tela, aplicando pixelização quando ativa."""
        if not self.ativa:
            destino.blit(origem, (0, 0))
            return

        # Progresso vai de 0.0 a quase 1.0 dentro da etapa atual.
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
