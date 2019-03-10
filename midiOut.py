import sys
import atexit
import signal
import mido
import time
from midiInFS import midiInFS

SoundFontFile = "/home/pi/soundfonts/Piano1.sf2"

def onExit():
    print("Exiting.........")
    midiOut.close()

def sigHandler(signo, frame):
    sys.exit(0)

atexit.register(onExit)
signal.signal(signal.SIGTERM, sigHandler)

midiIn = midiInFS()
#midiIn.testFunc()
midiIn.initFluidSynth(SoundFontFile)
time.sleep(7)
print(mido.get_output_names())
'''
midiOut = mido.open_output('Virtual Port', virtual=True)

#midiIn.startAndAttachSynth()

while True:
    #midiOut.sen
    #print ("tick")
    time.sleep(1.0)
    msg = mido.Message('note_on', note=45)
    midiOut.send(msg)
    time.sleep(0.5)
    msg = mido.Message('note_off', note=45)
    midiOut.send(msg)
print ("Last Line..........")
'''
