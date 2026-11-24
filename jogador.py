"""O personagem: movimento em 4 direções (sem diagonal) e animação de andar."""

import pygame

from carregador import carregar_quadros
from config import TILE, LARGURA, ALTURA

# --- Animações feitas por você, uma direção de cada vez -----------------------
# Chave: direção (x, y) -> (0, 1) baixo | (0, -1) cima | (-1, 0) esquerda | (1, 0) direita
#   "imagem": nome dos arquivos em assets, sem extensão (precisa de <nome>.png e <nome>.txt)
#   "parado": número do quadro quando o personagem está parado
#   "ordem":  sequência de quadros ao andar
# Os quadros são numerados pela ORDEM DAS LINHAS do .txt, começando em 0
# (a primeira linha do .txt é o quadro 0, a segunda é o 1, e assim por diante).
ANIMACOES = {
    (0, 1): {"imagem": "andar_baixo", "parado": 0, "ordem": [2, 0, 4, 0]},
    # Quando tiver as outras direções, descomente e ajuste:
    (0, -1): {"imagem": "andar_cima",   "parado": 0, "ordem": [2, 0, 4, 0]},
    # (-1, 0): {"imagem": "andar_esquerda", "parado": 0, "ordem": [2, 0, 4, 0]},
    # (1, 0):  {"imagem": "andar_direita",  "parado": 0, "ordem": [2, 0, 4, 0]},
}
# Enquanto uma direção não tiver animação própria, o jogo usa a animação desta direção
DIRECAO_PADRAO = (0, 1)
QUADROS_POR_SEGUNDO = 8

# Cada tecla -> direção (x, y)
TECLAS_DIRECAO = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}


class Jogador:
    TAMANHO = 24
    VELOCIDADE = 160        # pixels por segundo

    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, self.TAMANHO, self.TAMANHO)
        self.posicao = pygame.Vector2(x, y)  # posição exata (com decimais)
        self.rect.topleft = (round(x), round(y))
        self.virado = pygame.Vector2(0, 1)   # começa olhando para baixo
        self.pilha_teclas = []               # teclas seguradas, na ordem em que foram apertadas
        self.andando = False
        self.tempo_anim = 0.0

    # --- Entrada ---
    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in TECLAS_DIRECAO:
            self.pilha_teclas.append(evento.key)

    def atualizar_teclas(self, teclas):
        """Mantém só as teclas que ainda estão realmente pressionadas."""
        self.pilha_teclas = [k for k in self.pilha_teclas if teclas[k]]

    # --- Lógica ---
    def atualizar(self, dt, sala):
        direcao = pygame.Vector2(0, 0)
        if self.pilha_teclas:
            # A última tecla apertada manda: nunca anda na diagonal
            direcao = pygame.Vector2(TECLAS_DIRECAO[self.pilha_teclas[-1]])
            self.virado = direcao.copy()

        # Animação: só "anda" enquanto há tecla de direção apertada
        self.andando = direcao.length() > 0
        self.tempo_anim = self.tempo_anim + dt if self.andando else 0.0

        # Move em X e resolve colisão
        self.posicao.x += direcao.x * self.VELOCIDADE * dt
        self.rect.x = round(self.posicao.x)
        for tile in sala.tiles_solidos_perto(self.rect):
            if self.rect.colliderect(tile):
                if direcao.x > 0:
                    self.rect.right = tile.left
                elif direcao.x < 0:
                    self.rect.left = tile.right
                self.posicao.x = self.rect.x

        # Move em Y e resolve colisão
        self.posicao.y += direcao.y * self.VELOCIDADE * dt
        self.rect.y = round(self.posicao.y)
        for tile in sala.tiles_solidos_perto(self.rect):
            if self.rect.colliderect(tile):
                if direcao.y > 0:
                    self.rect.bottom = tile.top
                elif direcao.y < 0:
                    self.rect.top = tile.bottom
                self.posicao.y = self.rect.y

    def posicionar_na_entrada(self, lado):
        """Coloca o jogador logo dentro da sala, do lado por onde entrou."""
        if lado == "oeste":
            self.posicao.x = TILE
        elif lado == "leste":
            self.posicao.x = LARGURA - TILE - self.TAMANHO
        elif lado == "norte":
            self.posicao.y = TILE
        elif lado == "sul":
            self.posicao.y = ALTURA - TILE - self.TAMANHO
        self.rect.topleft = (round(self.posicao.x), round(self.posicao.y))

    # --- Desenho ---
    def _chave(self):
        return (round(self.virado.x), round(self.virado.y))

    def _quadro_atual(self):
        """Escolhe a imagem: animação da direção atual ou, se não houver, a padrão."""
        for direcao in (self._chave(), DIRECAO_PADRAO):
            animacao = ANIMACOES.get(direcao)
            if not animacao:
                continue
            quadros = carregar_quadros(animacao["imagem"])
            if not quadros:
                continue
            if self.andando:
                ordem = animacao["ordem"]
                indice = ordem[int(self.tempo_anim * QUADROS_POR_SEGUNDO) % len(ordem)]
            else:
                indice = animacao["parado"]
            return quadros[indice]
        return None

    def desenhar(self, superficie):
        quadro = self._quadro_atual()
        if quadro:
            # O sprite é maior que a hitbox: os pés ficam na base dela
            posicao = quadro.get_rect(midbottom=(self.rect.centerx, self.rect.bottom + 4))
            superficie.blit(quadro, posicao)
        else:
            # Sem imagem: quadrado vermelho e um quadradinho amarelo mostrando a direção
            pygame.draw.rect(superficie, (200, 50, 50), self.rect)
            marca = pygame.Vector2(self.rect.center) + self.virado * 10
            pygame.draw.rect(superficie, (255, 220, 0), (marca.x - 4, marca.y - 4, 8, 8))
