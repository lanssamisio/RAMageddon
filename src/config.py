"""Constantes de tela, grid, bordas, portal e transição."""

# --- Tela ---
# Tamanho fixo da janela, em pixels.
LARGURA, ALTURA = 800, 600
FPS = 60

# --- Grid ---
# Cada tile tem 25x25 pixels: 32 colunas e 24 linhas preenchem a tela.
TILE = 25
COLUNAS, LINHAS = LARGURA // TILE, ALTURA // TILE

# Arte de 16x16 ampliada para 48x48. ESCALA não depende de TILE.
ESCALA = 3

# --- Bordas ---
# Bordas sólidas: a troca de sala acontece só pelo portal.
# Espessura em tiles; aumentar aproxima a parede do centro.
ESPESSURA_BORDA_EO = 3      # leste/oeste (75 px)
ESPESSURA_BORDA_NS = 3      # norte/sul (75 px)

COR_PAREDE = (45, 45, 55)

# Portal: a spritesheet tem 12 quadros (4 colunas x 3 linhas). Depois de
# mostrar a abertura completa, os últimos quadros ficam em loop.
FRAMES_REPETICAO_PORTAL = 4

# Efeito de pixelização da transição.
# Valores maiores deixam blocos maiores; 1 = imagem normal.
BLOCOS = [1, 2, 4, 8, 16, 32, 64]
DURACAO_TRANSICAO = 0.45  # segundos para pixelar e para voltar ao normal

# --- Debug ---
# Teclas implementadas em src/debug.py:
# F1 liga/desliga; F2 colisão; F3 grade; F4 entidades; F5 info;
# F6 invoca o portal na frente do jogador.
