import sys
import atexit
import signal
import mido
import time
import logging
import RPi.GPIO as GPIO
from midiInFS import midiInFS
from subprocess import call

SoundFontFile = "/home/pi/soundfonts/FluidR3_GM.sf2"
#SoundFontFile = "/home/pi/soundfonts/Timbres.sf2"

PIN_LATCH_POWER = 14
PIN_POWER_STAT = 15

PIN_DATA = 2 #14
PIN_LATCH = 3 #15
PIN_CLOCK = 4 #18

KeyboardDict = {}
inputMDict = {}
#KeyboardRow = [20,16,12,7,8,25,24,23]
KeyboardRow = [23,24,25,8,7,12,16,20]
#CntrlRow = [4,17,27,22,5,6,13,19]
CntrlRow = [17,27,22,5,6,13,19,21]
finalMatrixOut = 26
baseMidiNote = 36 #48
instrumentIndex = 1
volumeIndex = 90
currentChannel = 0

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

def inputMatrixHandler():
    for i in range(2,7):
        shiftOut(1 << i)
        for j in range(8):
            processCntrlInput(i,j)
            processKeyInput(i-2, j, midiOut)

def processCntrlInput(i, j):
    if i < 0:
        return
    inCalc = (8*i)+j
    if not inCalc in inputMDict:
        inputMDict[inCalc] = 2
    if GPIO.input(CntrlRow[j]) == 1 and inputMDict[inCalc] != 1:
        inputMDict[inCalc] = 1
        handleInput(inCalc, 1)
    elif GPIO.input(CntrlRow[j]) == 0 and inputMDict[inCalc] == 1:
        inputMDict[inCalc] = 0
        handleInput(inCalc, 0)

def handleInput(btnInput, stat):
    handleDrumInput(btnInput, stat)
    if not stat:
        return
    if btnInput == 37:
        incVolume()
    if btnInput == 36:
        decVolume()
    if btnInput == 39:
        incInstrument()
    elif btnInput == 38:    
        decInstrument()
    elif btnInput == 47:    
        changeInstrument(1)
    elif btnInput == 46:    
        changeInstrument(19)
    elif btnInput == 45:    
        changeInstrument(105)
    elif btnInput == 44:    
        changeInstrument(80)
    elif btnInput == 43:    
        changeInstrument(56)
    elif btnInput == 42:    
        changeInstrument(25)
    elif btnInput == 41:    
        changeInstrument(40)
    elif btnInput == 40:    
        changeInstrument(76)
    else:
        print ("I "+str(btnInput)+" - "+str(stat))

def handleDrumInput(btnInput, stat):
    if btnInput == 55:
        playNote(36, stat, 9, midiOut)
    if btnInput == 54:
        playNote(38, stat, 9, midiOut)
    if btnInput == 53:
        playNote(42, stat, 9, midiOut)
    if btnInput == 52:
        playNote(49, stat, 9, midiOut)

def changeInstrument(inst):
    global instrumentIndex
    instrumentIndex = inst
    msg = mido.Message('program_change', program =inst)
    midiOut.send(msg)

def incVolume():
    global volumeIndex
    volumeIndex += 3
    if volumeIndex > 97:
        volumeIndex = 100
    midiIn.setVolume(str(volumeIndex))

def decVolume():
    global volumeIndex
    volumeIndex -= 3
    if volumeIndex < 70:
        volumeIndex = 70
    midiIn.setVolume(str(volumeIndex))

def incInstrument():
    global instrumentIndex
    instrumentIndex += 1
    if instrumentIndex > 114:
        instrumentIndex = 1
    changeInstrument(instrumentIndex)
    print (str(instrumentIndex))

def decInstrument():
    global instrumentIndex
    instrumentIndex -= 1
    if instrumentIndex < 1:
        instrumentIndex = 114
    changeInstrument(instrumentIndex)
    print (str(instrumentIndex))

def playNote(note, on, channel, midiObj):
    if on:
        msg = mido.Message('note_on', note=note, channel=channel)
        midiObj.send(msg)
        #print (note," is on" )
    else:
        msg = mido.Message('note_off', note=note, channel=channel)
        midiObj.send(msg)
        #print (note," is off" )


def processKeyInput(i, j, midiObj):
    if i < 0:
        return
    inCalc = (8*i)+j
    note = baseMidiNote+inCalc
    if not note in KeyboardDict:

        KeyboardDict[note] = 2
    if GPIO.input(KeyboardRow[j]) == 1 and KeyboardDict[note] != 1:
        playNote(note, 1, currentChannel, midiObj)
        KeyboardDict[note] = 1
    elif GPIO.input(KeyboardRow[j]) == 0 and KeyboardDict[note] == 1:
        playNote(note, 0, currentChannel, midiObj)
        KeyboardDict[note] = 0

def handleShutdown(channel):
    if GPIO.input(channel) == 0:
        print ("shutdwon called")
        call("sudo shutdown -h now", shell=True)
#def processKeyInputDrums(i, j, midiObj):
#    note = 
#    if not note in DrumsDict:
#        DrumsDict[note] = 2
#    if GPIO.input(KeyboardRow[j]) == 1 and DrumsDict[note] != 1:
#        playNote(note, 1, midiObj)
#        DrumsDict[note] = 1
#    elif GPIO.input(KeyboardRow[j]) == 0 and DrumsDict[note] == 1:
#        playNote(note, 0, midiObj)
#        DrumsDict[note] = 0

        
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

global midiOut
midiOut = mido.open_output(fsPort[0])
midiDrums = mido.open_output(fsPort[0])
midiIn.setVolume(str(volumeIndex))

changeInstrument(instrumentIndex)
#changeInstrument(44) strings
#changeInstrument(76)flutes
print ("Connected")

incInst = 0
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for i in range(8):
    GPIO.setup(KeyboardRow[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(CntrlRow[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    #GPIO.setup(CntrlRow[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(PIN_DATA, GPIO.OUT)
GPIO.setup(PIN_LATCH, GPIO.OUT)
GPIO.setup(PIN_CLOCK, GPIO.OUT)
GPIO.setup(PIN_LATCH_POWER, GPIO.OUT)
GPIO.setup(finalMatrixOut, GPIO.OUT)


GPIO.setup(PIN_POWER_STAT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(PIN_POWER_STAT, GPIO.BOTH, callback=handleShutdown)
GPIO.output(PIN_LATCH_POWER, 1)
while True:
    inputMatrixHandler()
#    for i in range(8):
#        shiftOut(1 << i)
#        for j in range(8):
#            inCalc = (8*i)+j
            #if inCalc < 4:
            #else:    
#            processKeyInput(i, j, midiOut)
print ("Last Line..........")
