import os
from threading import Thread


class speaker:

    def play_sound(self, path_to_audio):
        os.system('mpg321 ' + path_to_audio + ' > /dev/null')

    def say_hi(self):
        thread = Thread(target=self.play_sound, args=(
            "assets/WALLE\\ 1.mp3", )).start()
        thread.start()
        # self.play_sound("assets/WALLE\\ 1.mp3")

    def say_whoa(self):
        thread = Thread(target=self.play_sound, args=(
            "assets/Whoa.mp3", )).start()
        thread.start()
        # self.play_sound("assets/Whoa.mp3")
