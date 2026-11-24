import pygame

from carregador import relatorio
from config import LARGURA, ALTURA, FPS, TILE, OPOSTO
from jogador import Jogador
from salas import criar_salas, verificar_saida
from transicao import Transicao


def main():
    for linha in relatorio():  # mostra no terminal quais imagens foram encontradas
        print(linha)

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Meu Zelda")
    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 28)
    canvas = pygame.Surface((LARGURA, ALTURA))  # o jogo é desenhado aqui, depois vai para a tela

    salas = criar_salas()
    sala = salas[1]
    jogador = Jogador(12 * TILE, 10 * TILE)
    transicao = Transicao()

    rodando = True
    while rodando:
        dt = relogio.tick(FPS) / 1000

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            else:
                jogador.tratar_evento(evento)

        jogador.atualizar_teclas(pygame.key.get_pressed())

        if not transicao.ativa:
            jogador.atualizar(dt, sala)

            # Saiu pela abertura? Começa a transição
            lado = verificar_saida(jogador.rect)
            if lado and lado in sala.saidas:
                transicao.iniciar(sala.saidas[lado], OPOSTO[lado])
        else:
            resultado = transicao.atualizar(dt)
            if resultado == "trocar":
                # Tela toda pixelada: trocamos de sala sem o jogador ver
                sala = salas[transicao.sala_destino]
                jogador.posicionar_na_entrada(transicao.lado_entrada)

        # --- Desenho ---
        sala.desenhar(canvas)
        jogador.desenhar(canvas)
        canvas.blit(fonte.render(sala.nome, True, (255, 255, 255)), (10, 8))

        transicao.desenhar(canvas, tela)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()