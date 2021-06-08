#!/usr/bin/env python
# coding: utf-8
import numpy as np
import scipy.signal
from math import floor
from rtlsdr import RtlSdr 

# SDR
def derive(fsps, Tmax):
    dt = 1.0/fsps # Time step size between samples
    nyquist = fsps / 2.0 # Nyquist frequency
    N = round(fsps*Tmax) # Total number of samples to collect
    return dt, nyquist, N

def downsample(audio, fsps, faudiosps):
    dsf = round(fsps/faudiosps) # Downsampling factor
    audio = audio[0:floor(len(audio)/dsf)*dsf]
    downsampled_audio = np.mean(audio.reshape((-1, dsf)), axis=1).astype('float32')
    return downsampled_audio

def get_bpm(fcutoff, nyquist, N):
    fcuttoff_nyq = fcutoff / nyquist 
    midwidth = round(fcuttoff_nyq*N)
    zerowidth = int((N-midwidth)/2)
    bpm = np.concatenate((np.zeros(zerowidth),np.ones(midwidth),np.zeros(zerowidth)))
    return bpm

def process_samples(samples, fsps, fc, Tmax, fcutoff):
    ### Initialize
    dt, nyquist, N = derive(fsps, Tmax)
    bpm = get_bpm(fcutoff, nyquist, N)
    f_offset = int(250e3) #NEW
    shift = np.exp(1.0j * 2.0 * np.pi * f_offset / fsps * np.arange(N))
    ### Process
    shifted_samples = samples * shift
    spectrum = np.fft.fftshift(np.fft.fft(shifted_samples))
    filteredspectrum = spectrum * bpm
    filteredsignal = np.fft.ifft(np.fft.fftshift(filteredspectrum))
    # Get angles
    theta_og = np.arctan2(filteredsignal.imag,filteredsignal.real)
    # Squelch
    abssignal = np.abs(filteredsignal)
    mean = np.mean(abssignal)
    theta = np.where(abssignal < (mean/3), 0, theta_og)
    # Get instantaneous frequency
    derivtheta = np.convolve([1,-1],theta,'same')
    # Clean wrapping artifacts via median filter
    audio = scipy.ndimage.median_filter(derivtheta, size=10)
    return audio

# Initialize constants
faudiosps = 40960
fsps = 2*256*256*16 # Sampling frequency
fc = 433.5e6 # Center frequency
Tmax = 5 # Sampling time duration
fcutoff = 25e3 # Cutoff for walkie talkie
f_offset = int(250e3)

sdr = RtlSdr()
sdr.sample_rate = fsps 
sdr.center_freq = fc + f_offset
sdr.gain = 42.0