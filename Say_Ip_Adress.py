import sys
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')
import socket
import pyttsx3

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()

engine = pyttsx3.init()  # object creation

""" RATE"""
rate = engine.getProperty('rate')   # getting details of current speaking rate
print(rate)  # printing current voice rate
engine.setProperty('rate', 125)     # setting up new voice rate


"""VOLUME"""
volume = engine.getProperty(
    'volume')  # getting to know current volume level (min=0 and max=1)
print(volume)  # printing current volume level
engine.setProperty('volume', 1.0)    # setting up volume level  between 0 and 1

"""VOICE"""
voices = engine.getProperty('voices')  # getting details of current voice
# engine.setProperty('voice', voices[0].id)
# changing index, changes voices. o for male
# changing index, changes voices. 1 for female
engine.setProperty('voice', voices[8].id)

# for idx, voice in enumerate(voices):
#       print(idx, voice.id)


ip = ip.replace('', ' ').replace('.', 'Punkt')
print(ip)

engine.say('Guten Tag.')
engine.say('Meine IP Adresse ist ' + ip)
engine.runAndWait()
engine.stop()
