import subprocess
import time

class midiInFS:
    SoundFontFile = "/home/pi/soundfonts/Piano1.sf2"
    
    def testFunc(self):
        print("test func called")
        
    def initFluidSynth(self, soundFont):
        #start fluidsynth in the backround
        subprocess.Popen(["fluidsynth",
            "-is",
            "-r32000",
            "-c8",
            "--audio-driver=alsa",
            "--gain=2.5",
            soundFont])

    def stopFluidSynth(self):
        subprocess.Popen(["sudo",
            "pkill",
            "fluidsynth"])

    def setVolume(self, amount):
        subprocess.Popen(["amixer",
            "set",
            "PCM",
            "--",
            amount+"%"])

    def connectMidiToSynth(self, inputChannel, outputChannel):
        try:
            outI = subprocess.check_output(["aconnect", "-i"])
            print(outI)
            out = subprocess.check_output(["aconnect",
                inputChannel+":0",
                outputChannel+":0"])
           # if out.contains("Connection Faild"):
            #    return false
        except:
            return False
        return True

    def disconnectMidiSynth(self):
        subprocess.Popen(["aconnect",
            "-x"]);

    def startAndAttachSynth(self):
        self.stopFluidSynth()
        time.sleep(1)
        print("Start FluidSynth")
        self.initFluidSynth(self.SoundFontFile)
        time.sleep(7)
        print("Attach Midi Device")
        if self.connectMidiToSynth("128","128"):
            print("connection ok")
        else:
            print("connection failed")
            self.disconnectMidiSynth()
            self.stopFluidSynth()
        print("Done")
