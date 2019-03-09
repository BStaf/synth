import sys
import atexit
import signal
import mido
import time

def onExit():
    print("Exiting.........")
    midiOut.close()

def sigHandler(signo, frame):
    sys.exit(0)

atexit.register(onExit)
signal.signal(signal.SIGTERM, sigHandler)

midiOut = mido.open_input('Virtual Port', virtual=True)
while True:
    #midiOut.sen
    #print ("tick")
    time.sleep(0.01)
print ("Last Line..........")
