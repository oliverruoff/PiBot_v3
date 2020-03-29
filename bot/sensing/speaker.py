import os
from threading import Thread
import pygame


class speaker:

    def __init__(self):
        pygame.mixer.init()

    def play_sound(self, path_to_audio):
        pygame.mixer.music.load(path_to_audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() is True:
            continue

    def play_file(self, file, asyncr=True):
        relative_path = 'assets/' + file
        if asyncr:
            Thread(target=self.play_sound, args=(
                os.path.abspath(relative_path), )).start()
        else:
            pygame.mixer.music.load(relative_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() is True:
                continue
