import pygame

from config import TILE, LARGURA, ALTURA

# Mapeia teclas para uma direção cardinal.
# O valor é (x, y), onde y negativo aponta para cima na tela.
TECLAS_DIRECAO = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}
TECLAS_ATAQUE = (pygame.K_SPACE, pygame.K_j)


class Jogador:
    TAMANHO = 24
    VELOCIDADE = 400        # pixels por segundo
    DURACAO_ATAQUE = 0.25   # segundos

    def __init__(self, x, y):
        # rect é usado para colisão/desenho; posicao guarda movimento com float.
        self.rect = pygame.Rect(0, 0, self.TAMANHO, self.TAMANHO)
        self.posicao = pygame.Vector2(x, y)
        self.rect.topleft = (round(x), round(y))

        # Direção atual do olhar/ataque.
        self.virado = pygame.Vector2(0, 1)

        # Pilha de teclas de movimento para priorizar a última tecla pressionada.
        self.pilha_teclas = []
        self.tem_espada = False
        self.atacando = False
        self.timer_ataque = 0.0

    # --- Entrada ---
    def tratar_evento(self, evento):
        """Processa eventos pontuais, como pressionar tecla."""
        if evento.type != pygame.KEYDOWN:
            return

        if evento.key in TECLAS_DIRECAO:
            # A tecla mais recente fica no fim da pilha e ganha prioridade.
            self.pilha_teclas.append(evento.key)
        elif evento.key in TECLAS_ATAQUE:
            self.atacar()

    def atualizar_teclas(self, teclas):
        """Remove da pilha teclas que foram soltas."""
        self.pilha_teclas = [tecla for tecla in self.pilha_teclas if teclas[tecla]]

    def atacar(self):
        """Inicia o ataque se o jogador tiver espada e não estiver atacando."""
        if self.tem_espada and not self.atacando:
            self.atacando = True
            self.timer_ataque = self.DURACAO_ATAQUE

    # --- Lógica ---
    def atualizar(self, dt, sala):
        # Durante o ataque, o jogador fica parado até o timer acabar.
        if self.atacando:
            self.timer_ataque -= dt
            if self.timer_ataque <= 0:
                self.atacando = False
            return

        direcao = pygame.Vector2(0, 0)
        if self.pilha_teclas:
            # Usa a última tecla pressionada para evitar movimento diagonal.
            direcao = pygame.Vector2(TECLAS_DIRECAO[self.pilha_teclas[-1]])
            self.virado = direcao.copy()

        # Move no eixo X e resolve colisões antes de mover no eixo Y.
        # Isso evita que o jogador "grude" em cantos de forma estranha.
        self.posicao.x += direcao.x * self.VELOCIDADE * dt
        self.rect.x = round(self.posicao.x)
        for tile in sala.tiles_solidos_perto(self.rect):
            if self.rect.colliderect(tile):
                if direcao.x > 0:
                    self.rect.right = tile.left
                elif direcao.x < 0:
                    self.rect.left = tile.right
                self.posicao.x = self.rect.x

        # Depois repete o processo no eixo Y.
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
        elif lado == "centro":
            self.posicao.x = LARGURA // 2 - self.TAMANHO // 2
            self.posicao.y = ALTURA // 2 - self.TAMANHO // 2
        self.rect.topleft = (round(self.posicao.x), round(self.posicao.y))

    def hitbox_espada(self):
        """Área que a espada acerta (usada depois para dar dano nos inimigos)."""
        comprimento, largura = 26, 10
        if self.virado.x != 0:
            area = pygame.Rect(0, 0, comprimento, largura)
        else:
            area = pygame.Rect(0, 0, largura, comprimento)
        centro = pygame.Vector2(self.rect.center) + self.virado * (self.TAMANHO / 2 + comprimento / 2)
        area.center = (round(centro.x), round(centro.y))
        return area

    # --- Desenho ---
    def desenhar(self, superficie):
        pygame.draw.rect(superficie, (200, 50, 50), self.rect)
        # Quadradinho amarelo mostra para onde o personagem está virado
        marca = pygame.Vector2(self.rect.center) + self.virado * 10
        pygame.draw.rect(superficie, (255, 220, 0), (marca.x - 4, marca.y - 4, 8, 8))

        if self.atacando:
            area = self.hitbox_espada()
            pygame.draw.rect(superficie, (225, 230, 240), area)
            pygame.draw.rect(superficie, (130, 80, 40), area, 1)
