"""Constantes gerais do jogo."""

TILE = 32
# A arte é desenhada em 16x16 e ampliada para o tamanho do tile (32 / 16 = 2x)
ESCALA = TILE // 16
COLUNAS, LINHAS = 25, 20
LARGURA, ALTURA = COLUNAS * TILE, LINHAS * TILE
FPS = 60

# Posição das aberturas nas paredes (em tiles)
ABERTURA_H = range(11, 14)  # colunas das portas norte/sul
ABERTURA_V = range(8, 12)   # linhas das portas oeste/leste

COR_PAREDE = (45, 45, 55)

OPOSTO = {"norte": "sul", "sul": "norte", "leste": "oeste", "oeste": "leste"}

# Efeito de pixelização: tamanho do "pixel" a cada etapa
BLOCOS = [1, 2, 4, 8, 16, 32, 64]
DURACAO_TRANSICAO = 0.45  # segundos para pixelar (e o mesmo para voltar)
