# Works on a Raspberry Pi that has rpitx installed
# Transmits audio file named "reply.wav" on frequency of 433.5MHz via FM

# https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
# This program combines the top two answers from the stack overflow post
# Run this program with "sudo python3 program_name.py"
import os
import signal
import subprocess
import time
from scipy.io import wavfile

Fs, x = wavfile.read("reply.wav")
duration = len(x)/Fs
# The os.setsid() is passed in the argument preexec_fn so
# it's run after the fork() and before  exec() to run the shell.
cmd = "/home/pi/rpitx/pifmrds -audio /home/pi/reply.wav -freq 433.5"
pro = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE,
                       shell=True, preexec_fn=os.setsid)

print("sleeping")
time.sleep(duration * 3)
print("killing")
os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups
