from pathlib import Path

import pygame

# Na a pasta raiz do projeto deve voltar duas pastas a partir deste arquivo
ROOT_DIR = Path(__file__).resolve().parent.parent

# Caminho até a pasta
AUDIO_DIR = ROOT_DIR / "assets" / "audio"


def musica(volume=0.5):
    """Carrega e toca a música de fundo em loop infinito."""
    pygame.mixer.init()

    # caminho até a música
    caminho = AUDIO_DIR / "1_come_to.mp3"

    # Carrega a música na memória do mixer
    pygame.mixer.music.load(caminho)

    # Ajusta o volume (vai de 0.0 mudo até 1.0 máximo)
    pygame.mixer.music.set_volume(volume)

    # Tocar música, loops=-1 faz ela repetir para sempre
    pygame.mixer.music.play(loops=-1)
