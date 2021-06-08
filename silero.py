#!/usr/bin/env python
# coding: utf-8
from scipy.io.wavfile import write
from glob import glob
import subprocess
import torch
import os # to prevent crashing with the pytorch gradient library on MacOS
os.environ['KMP_DUPLICATE_LIB_OK']='True'

# Initialize speech-to-text module
device = torch.device('cpu')

stt_model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en',
                                       device=device, verbose=False)
(read_batch, split_into_batches, read_audio, prepare_model_input) = utils

# Initialize text-to-speech module
tts_model, symbols, sample_rate, example_text, apply_tts = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                                      model='silero_tts',
                                                                      language='en',
                                                                      speaker='lj_16khz', verbose=False)
tts_model = tts_model.to(device)  # gpu or cpu

def decode_file(filename):
    test_files = glob(filename)
    batches = split_into_batches(test_files, batch_size=10)
    input = prepare_model_input(read_batch(batches[0]), device=device)
    output = stt_model(input)
    decoded = decoder(output[0].cpu())
    return decoded

def get_speech(text):
    audio = apply_tts(texts=[text],
                      model=tts_model,
                      sample_rate=sample_rate,
                      symbols=symbols,
                      device=device)
    ret_audio = audio[0].numpy() * 0.05
    return ret_audio

def write_to_pi(audio, filename = 'reply.wav'):
    write(filename, sample_rate, audio)
    cmd = ['scp', filename, 'pi@raspberrypi.local:']
    subprocess.Popen(cmd, shell=False)

def transmit():
    cmd = 'sudo python3 pifmrds_term.py'
    subprocess.Popen("ssh {user}@{host} {cmd}".format(user='pi', host='raspberrypi.local', cmd=cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

def transmit_speech(text):
    write_to_pi(get_speech(text))
    transmit()

if __name__ == '__main__':
    transmit_speech("hello my friend, how are you?")