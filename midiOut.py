import sys
import atexit
import signal
import mido
import time
import logging
import RPi.GPIO as GPIO
from midiInFS import midiInFS

SoundFontFile = "/home/pi/soundfonts/FluidR3_GM.sf2"

PIN_DATA = 14
PIN_LATCH = 15
PIN_CLOCK = 18

KeyboardDict = {}
#KeyboardRow = [20,16,12,7,8,25,24,23]
KeyboardRow = [23,24,25,8,7,12,16,20]

def onExit():
    logging.info('Exiting')
    midiOut.close()

def sigHandler(signo, frame):
    sys.exit(0)

def shiftOut(byte):
    GPIO.output(PIN_LATCH, 0)
    for x in range(8):
        GPIO.output(PIN_DATA, (byte >> x) & 1)
        GPIO.output(PIN_CLOCK, 1)
        GPIO.output(PIN_CLOCK, 0)
    GPIO.output(PIN_LATCH, 1)

def changeInstrument(inst):
    msg = mido.Message('program_change', program =inst)
    midiOut.send(msg)

def playNote(note, on):
    if on:
        msg = mido.Message('note_on', note=note)
        midiOut.send(msg)
       # print (note," is on" )
    else:
        msg = mido.Message('note_off', note=note)
        midiOut.send(msg)
        #print (note," is off" )

def handleKeyPress(channel):
    if channel == In1:
        playNote(60, not GPIO.input(channel))
    if channel == In2:
        playNote(62, not GPIO.input(channel))
    if channel == In3:
        playNote(64, not GPIO.input(channel))
    if channel == In4:
        playNote(65, not GPIO.input(channel))

atexit.register(onExit)
signal.signal(signal.SIGTERM, sigHandler)

logging.info('Starting FluidSynth')
midiIn = midiInFS()
midiIn.stopFluidSynth()
time.sleep(1)
midiIn.initFluidSynth(SoundFontFile)

logging.info('Connecting to FluidSynth port')
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

midiIn.setVolume()
global midiOut
midiOut = mido.open_output(fsPort[0])

changeInstrument(76)
#changeInstrument(44) strings
#changeInstrument(76)flutes
print ("Connected")

incInst = 0
baseMidiNote = 48
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for i in range(8):
    GPIO.setup(KeyboardRow[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(PIN_DATA, GPIO.OUT)
GPIO.setup(PIN_LATCH, GPIO.OUT)
GPIO.setup(PIN_CLOCK, GPIO.OUT)

while True:
    for i in range(8):
        shiftOut(1 << i)
        for j in range(8):
            note = baseMidiNote+(8*i)+j
            if not note in KeyboardDict:
                KeyboardDict[note] = 2
            if GPIO.input(KeyboardRow[j]) == 1 and KeyboardDict[note] != 1:
                playNote(note, 1)
                KeyboardDict[note] = 1
            elif GPIO.input(KeyboardRow[j]) == 0 and KeyboardDict[note] == 1:
                playNote(note, 0)
                KeyboardDict[note] = 0
print ("Last Line..........")
