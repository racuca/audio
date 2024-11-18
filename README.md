# Raspberry Pi MEMS Mic audio Test
# reference 
https://github.com/makerportal/rpi_i2s

https://www.pythonguis.com/widgets/equalizerbar/

chatgpt


# setup process
## update OS

sudo apt-get -y update

sudo apt-get -y upgrade

sudo reboot

## update python

wget https://www.python.org/ftp/python/3.12.4/Python-3.xx.xx.tgz

tar zxvf Python-3.xx.xx.tgz

cd Python-3.xx.xx

./configure --enable-optimizations

sudo make altinstall


## install packages

sudo pip3 install --upgrade adafruit-python-shell</br>

sudo wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py</br>

sudo python3 i2smic.py</br>

sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev</br>

sudo pip install pyaudio matplotlib scipy</br>

# check audio devices with input channels

    import pyaudio
    audio = pyaudio.PyAudio() # start pyaudio
    for ii in range(0,audio.get_device_count()):
        # print out device info
        print(audio.get_device_info_by_index(ii))


