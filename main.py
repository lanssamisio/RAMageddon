from pathlib import Path
import sys

import pygame

# Garante que a pasta src esteja no caminho de importação.
RAIZ_PROJETO = Path(__file__).resolve().parent
SRC_DIR = RAIZ_PROJETO / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import LARGURA, ALTURA, FPS, TILE, OPOSTO
from jogador import Jogador
from salas import criar_salas, verificar_saida
from transicao import Transicao


def desenhar_texto(superficie, fonte, texto, centro_x, y, cor=(255, 255, 255)):
    """Desenha texto centralizado com uma sombra simples para legibilidade."""
    sombra = fonte.render(texto, True, (0, 0, 0))
    imagem = fonte.render(texto, True, cor)
    x = centro_x - imagem.get_width() // 2
    superficie.blit(sombra, (x + 2, y + 2))
    superficie.blit(imagem, (x, y))


def main():
    # Inicialização do pygame, janela e objetos principais do jogo.
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Meu Zelda")
    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 28)
    fonte_grande = pygame.font.Font(None, 36)

    # O jogo é desenhado no canvas; a transição decide como ele vai para a tela.
    canvas = pygame.Surface((LARGURA, ALTURA))

    salas = criar_salas(RAIZ_PROJETO)
    sala = salas[1]
    jogador = Jogador(12 * TILE, 15 * TILE)
    transicao = Transicao()

    mensagem = ""
    timer_mensagem = 0.0

    rodando = True
    while rodando:
        # dt é o tempo do frame em segundos; usar dt deixa o movimento consistente.
        dt = relogio.tick(FPS) / 1000

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            else:
                jogador.tratar_evento(evento)

        # Limpa teclas de movimento que já foram soltas.
        jogador.atualizar_teclas(pygame.key.get_pressed())

        if not transicao.ativa:
            jogador.atualizar(dt, sala)

            # Verifica coleta de itens por colisão com o jogador.
            for item in sala.itens:
                if not item.coletado and jogador.rect.colliderect(item.rect):
                    item.coletado = True
                    if item.tipo == "espada":
                        jogador.tem_espada = True
                        if sala.portal:
                            # Na sala 1, pegar a espada ativa o portal em vez de abrir porta.
                            sala.portal.ativo = True
                            mensagem = "A espada abriu um portal!"
                        else:
                            sala.desbloquear("leste")
                            mensagem = "Voce pegou a espada! Aperte ESPACO para atacar."
                        timer_mensagem = 4.0

            # Portais são objetos animados opcionais da sala.
            if sala.portal:
                sala.portal.atualizar(dt)
                if sala.portal.ativo and jogador.rect.colliderect(sala.portal.rect):
                    transicao.iniciar(sala.portal.destino, sala.portal.lado_entrada)

            # Se o jogador saiu por uma borda com saída aberta, inicia transição.
            lado = verificar_saida(jogador.rect)
            if lado and lado in sala.saidas_abertas():
                transicao.iniciar(sala.saidas_abertas()[lado], OPOSTO[lado])
        else:
            # Durante a transição, o gameplay pausa e só o efeito é atualizado.
            resultado = transicao.atualizar(dt)
            if resultado == "trocar":
                # No pico do efeito, a troca de sala não é visível.
                sala = salas[transicao.sala_destino]
                jogador.posicionar_na_entrada(transicao.lado_entrada)

        if timer_mensagem > 0:
            timer_mensagem -= dt

        # --- Desenho ---
        # A ordem importa: sala/fundo primeiro, depois portal/itens/jogador/HUD.
        sala.desenhar(canvas)
        jogador.desenhar(canvas)
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
