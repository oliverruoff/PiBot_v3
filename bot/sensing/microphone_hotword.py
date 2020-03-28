import snowboydecoder

class microphone:

    def __init__(self, model_path):
        self.model = model_path

    def hotword_callback(self):
        print('Heard you! :)')

    def start_listening(self):
        detector = snowboydecoder.HotwordDetector(self.model, sensitivity=0.5)
        print('Listening... Press Ctrl+C to exit')

        detector.start(detected_callback=self.hotword_callback,
                    sleep_time=0.03)

        detector.terminate()