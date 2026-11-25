"""RAMargedom - ponto de entrada. Rode com: python main.py"""

import pygame

from src.carregador import PASTA
from src.config import LARGURA, ALTURA, FPS, TILE
from src.debug import Debug
from src.jogador import Jogador
from src.salas import criar_salas
from src.transicao import Transicao


def desenhar_texto(superficie, fonte, texto, centro_x, y, cor=(255, 255, 255)):
    """Desenha texto centralizado com uma sombra simples para legibilidade."""
    sombra = fonte.render(texto, True, (0, 0, 0))
    imagem = fonte.render(texto, True, cor)
    x = centro_x - imagem.get_width() // 2
    superficie.blit(sombra, (x + 2, y + 2))
    superficie.blit(imagem, (x, y))

# Hud dos colecion
def desenhar_coletaveis(superficie, fonte, salas):
    itens = [item for sala in salas.values() for item in sala.itens]
    texto = fonte.render(
        f"Coletaveis: {sum(item.coletado for item in itens)}/{len(itens)}",
        True, (255, 255, 255),
    )
    posicao = texto.get_rect(bottomleft=(10, ALTURA - 10))
    superficie.blit(texto, posicao)


def desenhar_vidas(superficie, coracao, coracao_perdido, vidas):
    x_inicial = int(superficie.get_width() * 0.9) - 50
    for indice in range(3):
        imagem = coracao if indice < vidas else coracao_perdido
        superficie.blit(imagem, (x_inicial + 40 * indice, 75))


def main():
    # --- Inicialização ---
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("RAMargedom")
    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 28)
    fonte_grande = pygame.font.Font(None, 36)
    tamanho_coracao = (30, 27)
    coracao = pygame.transform.scale(
        pygame.image.load(str(PASTA / "coracao.png")).convert_alpha(),
        tamanho_coracao,
    )
    coracao_perdido = pygame.transform.scale(
        pygame.image.load(str(PASTA / "coracao_perdido.png")).convert_alpha(),
        tamanho_coracao,
    )

    # O jogo é desenhado no canvas; a transição decide como ele vai para a tela.
    canvas = pygame.Surface((LARGURA, ALTURA))

    salas = criar_salas()
    sala = salas[1]
    jogador = Jogador(12 * TILE, 15 * TILE)
    transicao = Transicao()
    debug = Debug()
    vidas = 3

    mensagem = ""
    timer_mensagem = 0.0

    rodando = True
    while rodando:
        # dt é o tempo do frame em segundos; usar dt deixa o movimento
        # e a animação consistentes mesmo se o FPS variar.
        dt = relogio.tick(FPS) / 1000

        # --- 1. EVENTOS ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                # F1..F6 são do debug; as outras teclas vão para o jogador.
                if not debug.tratar_tecla(evento.key, sala, jogador):
                    jogador.tratar_evento(evento)

        # Limpa teclas de movimento que já foram soltas.
        jogador.atualizar_teclas(pygame.key.get_pressed())

        # --- 2. MOVIMENTO E REGRAS ---
        # O portal continua animado durante a transição; o resto fica pausado.
        if sala.portal:
            sala.portal.atualizar(dt)

        if not transicao.ativa:
            jogador.atualizar(dt, sala)

            # Coleta de itens por colisão com o jogador.
            for item in sala.itens:
                if not item.coletado and jogador.rect.colliderect(item.rect):
                    item.coletado = True
                    if item.tipo == "espada":
                        # Na sala 1, pegar a espada ativa o portal.
                        jogador.tem_espada = True
                        sala.portal.ativo = True
                        mensagem = "A espada abriu um portal!"
                        timer_mensagem = 4.0

            # Única forma de trocar de sala: entrar no portal ativo.
            if sala.portal and sala.portal.ativo and jogador.rect.colliderect(sala.portal.rect):
                transicao.iniciar(sala.portal.destino)
        else:
            # Durante a transição o gameplay pausa e só o efeito é atualizado.
            if transicao.atualizar(dt):
                # No pico da pixelização a troca de sala não é visível.
                sala = salas[transicao.sala_destino]
                jogador.posicionar_na_entrada()

        if timer_mensagem > 0:
            timer_mensagem -= dt

        # --- 3. RENDERIZAÇÃO ---
        # Desenha sala, jogador, debug e HUD nessa ordem.
        sala.desenhar(canvas)
        jogador.desenhar(canvas)
        debug.desenhar(canvas, fonte, jogador, sala, relogio, dt, transicao)
        desenhar_coletaveis(canvas, fonte, salas)
        canvas.blit(fonte.render(sala.nome, True, (255, 255, 255)), (10, 8))
        desenhar_vidas(canvas, coracao, coracao_perdido, vidas)

        if sala.id == 1 and not jogador.tem_espada:
            desenhar_texto(canvas, fonte_grande, "Pegue a espada no pedestal", LARGURA // 2, ALTURA - 90)
        if timer_mensagem > 0:
            desenhar_texto(canvas, fonte_grande, mensagem, LARGURA // 2, ALTURA - 90, (255, 235, 120))

        # A transição faz o blit final do canvas na tela.
        transicao.desenhar(canvas, tela)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
