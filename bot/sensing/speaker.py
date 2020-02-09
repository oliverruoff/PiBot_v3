import os


class speaker:

    def play_sound(self, path_to_audio):
        os.system('mpg321 ' + path_to_audio + ' > /dev/null')

    def say_hi(self):
        self.play_sound("assets/WALLE\\ 1.mp3")

    def say_whoa(self):
        self.play_sound("assets/Whoa.mp3")
