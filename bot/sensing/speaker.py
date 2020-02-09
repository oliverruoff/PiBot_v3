from subprocess import DEVNULL, STDOUT, check_call


class speaker:

    def play_sound(self, path_to_audio):
        check_call(['mpg321', path_to_audio],
                   stdout=DEVNULL, stderr=STDOUT)
        # os.system('mpg321 ' + path_to_audio + ' > /dev/null')

    def say_hi(self):
        self.play_sound("assets/WALLE\\ 1.mp3")
