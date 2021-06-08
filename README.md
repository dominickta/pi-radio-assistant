# Smart Pi Radio Assistant

- [Introduction to Smart Pi Radio Assistant](#introduction-to-smart-pi-radio-assistant)
- [Required Hardware](#required-hardware)
- [Setting up Signal Processor](#setting-up-signal-processor)
- [Setting up the Raspberry Pi](#setting-up-the-raspberry-pi)
    - [Install operating system on the Pi](#install-operating-system-on-the-pi)
    - [Set up Internet Access to Pi via WiFi and SSH](#set-up-internet-access-to-pi-via-wifi-and-ssh)
    - [Install rpitx](#install-rpitx)
    - [Get python script to transmit audio](#get-python-script-to-transmit-audio)
    - [Connect a wire to GPIO pin 4](#connect-a-wire-to-gpio-pin-4)
- [Instructions for Setting up Pi as Signal Processor](#instructions-for-setting-up-pi-as-signal-processor)
    - [Modify USB buffer size](#modify-usb-buffer-size)
    - [Install conda](#install-conda)
    - [Install onnx runtime](#install-onnx-runtime)
    - [Install SDR stuff](#install-sdr-stuff)
    - [Install pytorch](#install-pytorch)
    
## Introduction to Smart Pi Radio Assistant
TODO

## Required Hardware
- [ ] Computer (fast enough to process SDR samples in realtime)
- [ ] SDR
- [ ] Walkie Talkie
- [ ] Raspberry Pi 4
- [ ] SD Card + SD Card Reader
- [ ] Ethernet cable or WiFi for LAN w/ Pi
- [ ] Temporary keyboard, mouse, monitor
- [ ] Antenna material (e.g. jumper wire)

## Setting up Signal Processor

TODO

## Setting up the Raspberry Pi

### 1. Install operating system on the Pi
1. Install Raspberry Pi Imager on a computer
2. Plug in SD card into SD card reader
3. Insert SD card to be used to hold operating system and storage for the Raspberry Pi
4. Open Raspberry Pi Imager
5. Choose an Operating System -> Raspberry Pi OS (Other) -> Raspberry Pi OS Lite (32-bit) no desktop environment
6. Choose SD Card
7. Select Write
8. Once writing is done, insert SD card into Raspberry Pi.
9. Plug in monitor, keyboard, and mouse before plugging in power for Raspberry Pi
10. Once it successfully boots, you should be able to login with the following credentials
user: pi
password: raspberry

Good to know facts:
- Raspberry Pi 4 has a unique ARM cpu architecture (specifically armv7l) which means that you might have to build programs from source (like Pytorch which takes 6-12 hours) or find community prebuilt binaries. 
- armv7l is a 32-bit processor (anything ARMv8 and above is 64-bit)
- rpitx requires our Raspberry Pi 4 to be run in headless mode (i.e. without monitor, keyboard, mouse connected; connected via SSH), which is why we use the Lite OS. We only use keyboard, mouse, monitor for ease of set-up. It's possible to set-up without these peripherals but its not worth figuring out.
- Raspberry Pi OS was previously called Raspbian because it is a Debian-based operating system, so you might hear it referred to as Raspbian (like in the rpitx repo)

Issues I've faced in the past:
* I used a TV monitor as a display which meant there was a lot of compatibility issues I needed to figure out. This involved editing config files on the SD card on my computer before plugging into the Pi.
* Trying to provide Internet access to Pi via ethernet cable connected to a Macbook involved turning on "Internet Sharing" over WiFi in the Sharing settings in MacOS
* Trying to install the Raspberry Pi OS desktop version will cause problems with rpitx. rpitx installation sets GPU to 250MHz which I think is underclocking, which is required for rpitx to be stable. This means that running rpitx + monitor causes desktop and/or rpitx to crash. I've had success installing the non-desktop Raspberry Pi OS and then manually installing a lightweight desktop afterwards if you insist on having a desktop interface.

### Set up Internet Access to Pi via WiFi and SSH
Following directions in here
1. `sudo raspi-config`
2. Setup localisation in Localisation Options
3. Enable SSH via Interfacing Options -> SSH
4. Setup SSID & passphrase in System Options -> Wireless LAN
5. Exit
6. Test connection with `ping google.com`

*If you don't have a temporary keyboard/mouse/monitor available to setup Raspberry Pi, there are 'headless' configuration instructions online. It involves editing network config files and messing around with the SD card before plugging it into the Pi.*

After this, you **should only connect to Raspberry Pi via SSH** (over WiFi or Ethernet), aka run the Raspberry Pi in 'headless' configuration. Otherwise there might be issues with rpitx and monitor/GPU crashing (even if your monitor is only displaying a terminal).

Assuming your Pi is the only Pi on your local network, you can connect via
```
ssh pi@raspberrypi.local
```
Otherwise you can connect to your Pi by finding its IP address on your local network.

### Install rpitx

Follow the up-to-date instructions in the README [here](https://github.com/F5OEO/rpitx).

As a convenience, the instructions as of June 5th, 2021 are listed in this section.
```
sudo apt-get update
sudo apt-get install git
git clone https://github.com/F5OEO/rpitx
cd rpitx
./install.sh
sudo reboot
```

Test out the installation by running this command in the rpitx folder:
```
sudo ./pifmrds -audio sampleaudio.wav -freq 434
```
This will transmit the included "sampleaudio.wav" file via the [FM radio protocol](https://en.wikipedia.org/wiki/FM_broadcasting#Other_subcarrier_services) on a frequency of 434MHz. 

This should work without an antenna but range will increase with an antenna to (TBD).

There are a bunch of other fun programs in this repo such as
- transmitting images via the waterfall in a SDR receiver
- replay signals with SDR + Pi
- transmitting data to pagers via pocsag

***Major Issues:***
You must be running your Pi on headless mode while using rpitx (there are some workarounds though)
https://github.com/F5OEO/rpitx/issues/244
https://github.com/F5OEO/rpitx/issues/231

### Get python script to transmit audio

TODO

### Connect a wire to GPIO pin 4

## Instructions for Setting up Pi as Signal Processor
I spent a lot of time trying to get the Raspberry Pi to stream and process samples from an SDR with reasonable performance, but was unable to.

The Raspberry Pi 4 is unable to process radio signals with realtime performance that is needed for this application (hopefully someone can prove me wrong).

The following instructions were created when I believed that it would still work. So if you're trying to get your Pi to stream & process radio waves, these instructions are probably useful.

### Modify USB buffer size
The SDR needs to stream samples via the USB port and buffers are allocated to handle that. We need to manually increase the buffer size and also ensure this change persists throughout reboots. The default on Linux is only 16MB which is not enough for our SDR streaming.

The following instructions are an offshoot of [this guide](https://www.flir.com/support-center/iis/machine-vision/application-note/understanding-usbfs-on-linux/).

1. Open startup command file in a text editor

Open /etc/rc.local. This file contains commands that will be run on boot. We'll add a command to this file that will change the usb buffer size to 1024MB everytime on boot.
```
sudo vim /etc/rc.local
```

2. Edit the file

/etc/rc.local *should* already exist on your Pi. If so, add this line right before `exit 0` (the last line): 
```
echo 1024 > /sys/module/usbcore/parameters/usbfs_memory_mb
```
If /etc/rc.local doesn't already exist, make this the content of your file:
```
#!/bin/sh -e
echo 1024 > /sys/module/usbcore/parameters/usbfs_memory_mb
exit 0
```
3. Save changes and reboot
Save your changes to the file and then reboot the Pi. You can reboot with `sudo reboot`.

4. Check your work

If it worked then this command should spit out `1024`.
```
cat /sys/module/usbcore/parameters/usbfs_memory_mb
```

### Install conda
***Just in case you need conda on the Raspberry Pi, this is useful. Currently anaconda doesn't support armv7l cpus.***

Install conda following these [Stack Overflow instructions](https://stackoverflow.com/a/56852714)

Note that this works because we are getting the armv7l version. You can confirm that you have the correct CPU architecture by running `uname -m`
```
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
sudo md5sum Miniconda3-latest-Linux-armv7l.sh
sudo /bin/bash Miniconda3-latest-Linux-armv7l.sh
```
**Important**: Only follow the first set of instructions (listed below); we already have Python3.7 via Raspberry Pi OS installation
**Important**: follow these directions for the prompts carefully

Accept the license agreement with `yes`

When asked, change the install location: `/home/pi/miniconda3`

Do you wish the installer to prepend the Miniconda3 install location to PATH in your /root/.bashrc ? `yes`

Now add the install path to the PATH variable:

`sudo nano /home/pi/.bashrc`

Go to the end of the file .bashrc and add the following line:

`export PATH="$PATH:/home/pi/miniconda3/bin`
 **NOTE: This is different from the Stack Overflow path. We want to append miniconda3 because we want to avoid using miniconda3's version of python3 (python3.4), and use the default python3.7 that came with Raspberry Pi OS**


Save the file and exit.

To test if the installation was successful, open a new terminal and enter

`conda`

If you see a list with commands you are ready to go.

### Install onnx runtime
***ONNX Runtime is required to run Pytorch models, because currently Pytorch uses Intel Math Kernel Library (mkl) which doesn't work on an ARM CPU.*** 

https://github.com/nknytk/built-onnxruntime-for-raspberrypi-linux/tree/master/wheels/buster

```
wget https://github.com/nknytk/built-onnxruntime-for-raspberrypi-linux/raw/master/wheels/buster/onnxruntime-1.8.0-cp37-cp37m-linux_armv7l.whl

pip3 install onnxruntime-1.8.0-cp37-cp37m-linux_armv7l.whl
```



### Install SDR stuff
Install with this command:
```
sudo apt-get install gr-osmosdr
```
Plug in your SDR into your Pi and test if it worked via this command:
```
rtl_test -t
```
### Install pytorch
***Pytorch with onnx runtime is NOT a bottleneck. For example, the silero models run surprisingly fast.***

Pytorch does not provide builds for ARM cpus, so we either have to build it ourselves or find someone who pre-built it for the ARM cpu.

I attempted building it myself (before knowing someone prebuilt it) and it was compiling for ~6 hours before it eventually didn't work for some reason. I tried this twice, wasted 12 hours, and then found [this slightly outdated guide](https://medium.com/analytics-vidhya/quick-setup-instructions-for-installing-pytorch-and-fastai-on-raspberry-pi-4-5ffbe45e0ae3) that works with ***heavy*** modifications.

1. Check your ARM processor configuration via uname -a. It should contain "armv7l GNU/Linux" at the end.

2. Check we have the correct python3 version via `python3 --version`. It should say Python3.7

3. Download recent prebuilt Pytorch wheels 

Download torch 1.7 and torchaudio 0.7 (more recent version) wheels. The guide I linked above that we are following has a link to an older version of torch. [This repo](https://github.com/isakbosman/pytorch_arm_builds) has more recent versions uploaded.

We need to download the most recent available torch and torchaudio file that ends in "linux_armv7l.whl"

As of June 5th, 2021, these are the correct download links:
```
https://github.com/isakbosman/pytorch_arm_builds/raw/main/torch-1.7.0a0-cp37-cp37m-linux_armv7l.whl
https://github.com/isakbosman/pytorch_arm_builds/raw/main/torchaudio-0.7.0a0%2Bac17b64-cp37-cp37m-linux_armv7l.whl
```

Inside home directory, run
```
wget https://github.com/isakbosman/pytorch_arm_builds/raw/main/torch-1.7.0a0-cp37-cp37m-linux_armv7l.whl

wget https://github.com/isakbosman/pytorch_arm_builds/raw/main/torchaudio-0.7.0a0%2Bac17b64-cp37-cp37m-linux_armv7l.whl
```

4. Install the files
```
sudo apt install libatlas3-base
sudo apt-get install -y libopenblas-base
pip3 install INSERT_TORCH_WHEEL_FILE_DOWNLOADED_IN_STEP_3
pip3 install INSERT_TORCH_AUDIO_WHEEL_FILE_DOWNLOADED_IN_STEP_3
```

5. Check if installed properly
Start a python3 session by typing `python3`
Run these commands (exit session by entering `quit()`):
```
import torch
import torchaudio
import numpy
```

**Other useful Pytorch links**
* https://github.com/pytorch/pytorch/issues/41592
* https://stackoverflow.com/questions/66693151/how-can-i-emulate-run-pytorch-model-that-uses-aten-stft-implementation-on-arm-ba
* https://mathinf.eu/pytorch/arm64/2021-01/