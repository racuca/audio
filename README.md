# Raspberry Pi MEMS Mic audio Test
# reference 
https://github.com/makerportal/rpi_i2s

https://www.pythonguis.com/widgets/equalizerbar/

chatgpt


# setup process
#### 1. update OS

sudo apt-get -y update

sudo apt-get -y upgrade

sudo reboot

#### 2. update python

wget https://www.python.org/ftp/python/3.xx.xx/Python-3.xx.xx.tgz

tar zxvf Python-3.xx.xx.tgz

cd Python-3.xx.xx

./configure --enable-optimizations

sudo make altinstall

cd /usr/bin

sudo rm python

sudo ln -s /usr/local/bin/python3.xx python

python --version



#### 3. install PyQt5 for equalizer function - Optional

sudo apt-get install python3-pyqt5

sudo apt-get install qttools5-dev-tools

sudo apt-get install pyside2-tools

sudo apt-get install pyside2.*

sudo apt-get install python3-pyside2.*

###### run for DRI2 error message, but after this, screen may be unstable. 
sudo raspi-config

Advanced Options -> GL Driver -> GL (Full KMS) OpenGL desktop driver with full KMS. After rebooting

#### 4. install packages

sudo pip3 install --upgrade adafruit-python-shell</br>

sudo wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py</br>

sudo python3 i2smic.py</br>

sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev</br>

sudo pip install pyaudio matplotlib scipy</br>

#### 5. connect raspberry pi and mems mic

refer to images

#### 6. check audio devices with input channels

    import pyaudio
    audio = pyaudio.PyAudio() # start pyaudio
    for ii in range(0,audio.get_device_count()):
        # print out device info
        print(audio.get_device_info_by_index(ii))

#### 7. record speech and analyze wave file using fft.
python i2s_mono.py

python fft_pysimplegui.py

python fft_prompt.py
