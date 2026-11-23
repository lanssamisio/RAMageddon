# Tamanho base do grid: cada tile tem 32x32 pixels.
TILE = 32
COLUNAS, LINHAS = 25, 20
LARGURA, ALTURA = COLUNAS * TILE, LINHAS * TILE
FPS = 60

# Aberturas das portas na borda da sala, medidas em tiles.
# range usa fim exclusivo: range(12, 13) inclui só o tile 12.
ABERTURA_H = range(12, 13)  # colunas das portas norte/sul
ABERTURA_V = range(9, 11)   # linhas das portas oeste/leste

# Espessura da colisão da borda, em tiles.
# Aumentar aproxima a parede do centro; diminuir afasta para a borda da tela.
ESPESSURA_BORDA_EO = 4      # bordas leste/oeste
ESPESSURA_BORDA_NS = 3      # bordas norte/sul

COR_PAREDE = (45, 45, 55)

# Usado na transição: entrar por um lado significa vir do lado oposto.
OPOSTO = {"norte": "sul", "sul": "norte", "leste": "oeste", "oeste": "leste"}

# Efeito de pixelização da transição.
# Valores maiores deixam blocos maiores; 1 = imagem normal.
BLOCOS = [1, 2, 4, 8, 16, 32, 64]
DURACAO_TRANSICAO = 0.45  # segundos para pixelar e para voltar ao normal

# Mostra as tiles sólidas por cima do mapa para ajustar colisões.
DEBUG_COLISAO = True
