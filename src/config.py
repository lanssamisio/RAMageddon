"""Constantes gerais do jogo.

A tela tem tamanho fixo, como no Pong. Todo o resto (grid, portas, sprites)
é derivado daqui, para não haver números mágicos espalhados pelo código.
"""

# --- Tela ---
# LARGURA e ALTURA são a fonte da verdade: a janela nunca muda de tamanho.
LARGURA, ALTURA = 800, 600
FPS = 60

# --- Grid ---
# Cada tile tem 25x25 pixels. 800/25 = 32 colunas e 600/25 = 24 linhas,
# então o mapa preenche a tela exatamente, sem sobras e sem distorção.
TILE = 25
COLUNAS, LINHAS = LARGURA // TILE, ALTURA // TILE

# A arte do personagem é desenhada em 16x16 e ampliada para 32x32.
# ESCALA fica separada de TILE: se o grid mudar, o sprite não encolhe.
ESCALA = 2

# --- Portas ---
# range() tem fim exclusivo. Abrimos 3 colunas nas portas norte/sul e
# 4 linhas nas portas leste/oeste para o jogador de 24px passar com folga.
ABERTURA_H = range(11, 14)  # colunas das portas norte/sul (75px)
ABERTURA_V = range(8, 12)   # linhas das portas oeste/leste (100px)

# Espessura da colisão da borda, em tiles.
# Aumentar aproxima a parede do centro; diminuir afasta para a borda da tela.
ESPESSURA_BORDA_EO = 4      # bordas leste/oeste (100px)
ESPESSURA_BORDA_NS = 3      # bordas norte/sul (75px)

COR_PAREDE = (45, 45, 55)

# Usado na transição: entrar por um lado significa vir do lado oposto.
OPOSTO = {"norte": "sul", "sul": "norte", "leste": "oeste", "oeste": "leste"}

# Efeito de pixelização da transição.
# Valores maiores deixam blocos maiores; 1 = imagem normal.
BLOCOS = [1, 2, 4, 8, 16, 32, 64]
DURACAO_TRANSICAO = 0.45  # segundos para pixelar e para voltar ao normal

# --- Debug ---
# As opções ficam em src/debug.py. Durante o jogo, use:
# F1 = ligar/desligar tudo; F2 = colisão; F3 = grade; F4 = entidades; F5 = info.
