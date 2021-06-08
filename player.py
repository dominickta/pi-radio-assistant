#!/usr/bin/env python
# coding: utf-8
from silero import *
from myspotify import *
from mysdr import *
import asyncio
from scipy.io.wavfile import write

def parse(message):
    tokens = message.split(' ')
    query = " ".join(str(x) for x in tokens[1:])
    cmd = tokens[0]
    if cmd == 'play':
        play_song(get_device_id(), query)
    elif cmd == 'weather' or cmd == 'whether':
        hardcoded_response = "The current weather in " + query + " is cloudy. Expect rain this afternoon."
        transmit_speech(hardcoded_response)
    elif cmd == 'echo' or cmd == 'ego' or cmd == 'andgo' or cmd == 'andcho':
        transmit_speech(query)
    else:
        return False
    return True

async def streaming():
    print("Streaming!")
    async for samples in sdr.stream(fsps*Tmax):
        raw_audio = process_samples(samples, fsps, fc, Tmax, fcutoff)
        audio_play = downsample(raw_audio, fsps, faudiosps)
        write('incoming_msg.wav', faudiosps, audio_play)
        msg = decode_file('incoming_msg.wav')
        if msg == '':
            continue
        elif parse(msg):
            print("Command received:", msg)
        else:
            print("Couldn't parse command:", msg)

asyncio.run(streaming())