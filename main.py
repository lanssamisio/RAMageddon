"""Meu Zelda - ponto de entrada. Rode com: python main.py"""

import pygame

from src.carregador import relatorio
from src.config import LARGURA, ALTURA, FPS, TILE, OPOSTO
from src.debug import Debug
from src.jogador import Jogador, ANIMACOES
from src.salas import criar_salas, verificar_saida
from src.transicao import Transicao


def desenhar_texto(superficie, fonte, texto, centro_x, y, cor=(255, 255, 255)):
    """Desenha texto centralizado com uma sombra simples para legibilidade."""
    sombra = fonte.render(texto, True, (0, 0, 0))
    imagem = fonte.render(texto, True, cor)
    x = centro_x - imagem.get_width() // 2
    superficie.blit(sombra, (x + 2, y + 2))
    superficie.blit(imagem, (x, y))


def main():
    # Avisa no terminal se faltou algum arquivo de sprite (ajuda a achar erro).
    for linha in relatorio([anim["imagem"] for anim in ANIMACOES.values()]):
        print(linha)

    # --- Inicialização ---
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Meu Zelda")
    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 28)
    fonte_grande = pygame.font.Font(None, 36)

    # O jogo é desenhado no canvas; a transição decide como ele vai para a tela.
    canvas = pygame.Surface((LARGURA, ALTURA))

    salas = criar_salas()
    sala = salas[1]
    jogador = Jogador(12 * TILE, 15 * TILE)
    transicao = Transicao()
    debug = Debug()

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
                # F1..F5 são do debug; as outras teclas vão para o jogador.
                if not debug.tratar_tecla(evento.key):
                    jogador.tratar_evento(evento)

        # Limpa teclas de movimento que já foram soltas.
        jogador.atualizar_teclas(pygame.key.get_pressed())

        # --- 2. MOVIMENTO E REGRAS ---
        if not transicao.ativa:
            jogador.atualizar(dt, sala)

            # Coleta de itens por colisão com o jogador.
            for item in sala.itens:
                if not item.coletado and jogador.rect.colliderect(item.rect):
                    item.coletado = True
                    if item.tipo == "espada":
                        jogador.tem_espada = True
                        if sala.portal:
                            # Na sala 1, pegar a espada ativa o portal.
                            sala.portal.ativo = True
                            mensagem = "A espada abriu um portal!"
                        else:
                            mensagem = "Voce pegou a espada! Aperte ESPACO para atacar."
                        timer_mensagem = 4.0

            # Portais são objetos animados opcionais da sala.
            if sala.portal:
                sala.portal.atualizar(dt)
                if sala.portal.ativo and jogador.rect.colliderect(sala.portal.rect):
                    transicao.iniciar(sala.portal.destino, sala.portal.lado_entrada)

            # Se o jogador saiu por uma borda com saída aberta, inicia transição.
            # Consultamos as saídas uma vez para não refazer o dicionário duas vezes.
            lado = verificar_saida(jogador.rect)
            if lado and lado in sala.saidas:
                transicao.iniciar(sala.saidas[lado], OPOSTO[lado])
        else:
            # Durante a transição o gameplay pausa e só o efeito é atualizado.
            if transicao.atualizar(dt):
                # No pico da pixelização a troca de sala não é visível.
                sala = salas[transicao.sala_destino]
                jogador.posicionar_na_entrada(transicao.lado_entrada)

        if timer_mensagem > 0:
            timer_mensagem -= dt

        # --- 3. RENDERIZAÇÃO ---
        # A ordem importa: sala/fundo primeiro, depois jogador/HUD/mensagens.
        sala.desenhar(canvas)
        jogador.desenhar(canvas)
        debug.desenhar(canvas, fonte, jogador, sala, relogio, dt, transicao)
        canvas.blit(fonte.render(sala.nome, True, (255, 255, 255)), (10, 8))

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
