# Raspberry Pi MEMS Mic audio Test
# reference 
https://github.com/makerportal/rpi_i2s
https://www.pythonguis.com/widgets/equalizerbar/
chatgpt

# setup process
rasp

sudo apt-get -y update
sudo apt-get -y upgrade
sudo reboot
sudo pip3 install --upgrade adafruit-python-shell
sudo wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py
sudo python3 i2smic.py

sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
sudo pip install pyaudio matplotlib scipy

# check audio devices with input channels

import pyaudio
audio = pyaudio.PyAudio() # start pyaudio
for ii in range(0,audio.get_device_count()):
    # print out device info
    print(audio.get_device_info_by_index(ii)) 


