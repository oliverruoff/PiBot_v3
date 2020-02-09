import pygame


class speaker:

    def play_sound(self, path_to_audio):
        pygame.mixer.init()
        pygame.mixer.music.load(path_to_audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() is True:
            continue

    def say_hi(self):
        self.play_sound("/home/pi/develop/PiBot_v3/bot/assets/WALLE 1.mp3")
