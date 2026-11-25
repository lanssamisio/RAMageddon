"""Utilitário para dividir uma folha de sprites em quadros."""


import pygame


def fatiar_spritesheet(sheet, colunas, linhas):
    """Divide uma spritesheet em frames individuais.

    A spritesheet deve ter uma grade uniforme: todas as células com o mesmo
    tamanho. Os frames são lidos da esquerda para direita, de cima para baixo.
    """
    # Divisão inteira: a folha do portal é 1536x1024 (4 colunas x 3 linhas).
    largura_frame = sheet.get_width() // colunas
    altura_frame = sheet.get_height() // linhas
    frames = []

    for linha in range(linhas):
        for coluna in range(colunas):
            # Retângulo do frame atual dentro da imagem completa.
            retangulo = pygame.Rect(
                coluna * largura_frame,
                linha * altura_frame,
                largura_frame,
                altura_frame,
            )
            # copy() evita manter referência à surface inteira da spritesheet.
            frames.append(sheet.subsurface(retangulo).copy())

    return frames
