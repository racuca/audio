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

sudo apt-get install python3-pyside2.qt3dcore python3-pyside2.qt3dinput python3-pyside2.qt3dlogic python3-pyside2.qt3drender python3-pyside2.qtcharts python3-pyside2.qtconcurrent python3-pyside2.qtcore python3-pyside2.qtgui python3-pyside2.qthelp python3-pyside2.qtlocation python3-pyside2.qtmultimedia python3-pyside2.qtmultimediawidgets python3-pyside2.qtnetwork python3-pyside2.qtopengl python3-pyside2.qtpositioning python3-pyside2.qtprintsupport python3-pyside2.qtqml python3-pyside2.qtquick python3-pyside2.qtquickwidgets python3-pyside2.qtscript python3-pyside2.qtscripttools python3-pyside2.qtsensors python3-pyside2.qtsql python3-pyside2.qtsvg python3-pyside2.qttest python3-pyside2.qttexttospeech python3-pyside2.qtuitools python3-pyside2.qtwebchannel python3-pyside2.qtwebsockets python3-pyside2.qtwidgets python3-pyside2.qtx11extras python3-pyside2.qtxml python3-pyside2.qtxmlpatterns

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
