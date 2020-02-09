import os


class speaker:

    def play_sound(self, path_to_audio):
        os.system('mpg321 ' + path_to_audio + ' &')

    def say_hi(self):
        self.play_sound("/home/pi/develop/PiBot_v3/bot/assets/WALLE\\ 1.mp3")
