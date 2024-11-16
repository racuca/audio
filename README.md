# Raspberry Pi MEMS Mic audio Test
# reference 
https://github.com/makerportal/rpi_i2s

https://www.pythonguis.com/widgets/equalizerbar/

chatgpt


# setup process

sudo apt-get -y update

sudo apt-get -y upgrade

sudo reboot

sudo pip3 install --upgrade adafruit-python-shell</br>

sudo wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py</br>

sudo python3 i2smic.py</br>

sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev</br>

sudo pip install pyaudio matplotlib scipy</br>

# check audio devices with input channels

    import pyaudio</br>
    audio = pyaudio.PyAudio() # start pyaudio</br>
    for ii in range(0,audio.get_device_count()):</br>
        # print out device info</br>
        print(audio.get_device_info_by_index(ii)) </br>


