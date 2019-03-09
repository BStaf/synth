import subprocess
import time

class midiInFS:
    SoundFontFile = "/home/pi/soundfonts/Timbres.sf2"
    
    def testFunc():
        print("test func called")
        
    def initFluidSynth(soundFont):
        #start fluidsynth in the backround
        subprocess.Popen(["fluidsynth",
            "-is",
            "--audio-driver=alsa",
            "--gain=3",
            soundFont])

    def stopFluidSynth():
        subprocess.Popen(["sudo",
            "pkill",
            "fluidsynth"])

    def connectMidiToSynth(inputChannel, outputChannel):
        try:
            out = subprocess.check_output(["aconnect",
                inputChannel+":0",
                outputChannel+":0"])
           # if out.contains("Connection Faild"):
            #    return false
        except:
            return False
        return True

    def disconnectMidiSynth():
        subprocess.Popen(["aconnect",
            "-x"]);

    def startAndAttachSynth():
        stopFluidSynth()
        time.sleep(1)
        print("Start FluidSynth")
        initFluidSynth(SoundFontFile)
        time.sleep(7)
        print("Attach Midi Device")
        if connectMidiToSynth("20","128"):
            print("connection ok")
        else:
            print("connection failed")
            disconnectMidiSynth()
            stopFluidSynth()
        print("Done")
