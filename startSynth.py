import subprocess
import os

callingDir = os.path.dirname(os.path.realpath(__file__))
print (callingDir)
cmd = "python3 midiOut.py"
while True:
    try:
        subprocess.check_call(["python3", callingDir + "/midiOut.py"])
    except subprocess.CalledProcessError as error:
        print (error)
