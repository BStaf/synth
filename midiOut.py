import sys
import atexit
import signal
import mido
import time
import logging
from midiInFS import midiInFS

SoundFontFile = "/home/pi/soundfonts/DanceTrance.sf2"

def onExit():
    logging.debug('Exiting')
    midiOut.close()

def sigHandler(signo, frame):
    sys.exit(0)

def playNote(midiOut, note, hold):
    msg = mido.Message('note_on', note=note)
    midiOut.send(msg)
    time.sleep(hold)
    msg = mido.Message('note_off', note=note)
    midiOut.send(msg)
 
atexit.register(onExit)
signal.signal(signal.SIGTERM, sigHandler)

midiIn = midiInFS()
#midiIn.testFunc()
midiIn.stopFluidSynth()
time.sleep(1)
midiIn.initFluidSynth(SoundFontFile)
print("waiting for FluidSynth port")
fsPort = []
timeout = time.time() + 30
while time.time() < timeout:
    fsPort = [fs for fs in mido.get_output_names() if "FLUID" in fs]
    if fsPort == []:
        time.sleep(0.2)
        continue
    else:
        break
else:
    logging.error("Failed to link to FluidSynth")

midiOut = mido.open_output(fsPort[0])
print (fsPort)

while True:
    hold = 0.15
    playNote(midiOut, 60, hold)
    playNote(midiOut, 62, hold)
    playNote(midiOut, 64, hold)
    playNote(midiOut, 62, hold)
    playNote(midiOut, 65, hold)
    playNote(midiOut, 67, hold)
    playNote(midiOut, 65, hold)
    playNote(midiOut, 69, hold)
print ("Last Line..........")
