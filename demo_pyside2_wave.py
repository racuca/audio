# Source that implement equalizer of wave file using wave module
# reference code : https://www.pythonguis.com/widgets/equalizerbar/
# 2024.11.19

from PySide2 import QtCore, QtWidgets
from equalizer_bar import EqualizerBar
from PySide2.QtWidgets import QFileDialog
import random
import wave
import numpy as np
import scipy.fftpack as fft


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.equalizer = EqualizerBar(10, ['#0C0786', '#40039C', '#6A00A7', '#8F0DA3', '#B02A8F', '#CA4678', '#E06461',
                                          '#F1824C', '#FCA635', '#FCCC25', '#EFF821'])
        self.setCentralWidget(self.equalizer)


        self.fileName = QFileDialog.getOpenFileName(self,'Wave File','','*.wav')
        #print(self.fileName)
        self.wave_data = self.read_wave_file(self.fileName[0])
        self.chunk_size = 1024
        self.rate = 44100
        self.current_position = 0
        # frequency range setting ( 5 ranges )
        self.bands = [(20, 100), (100, 500), (500, 750), (750, 1000), (1000, 2000),
                      (2000, 3000), (3000, 5000), (5000, 10000),(10000, 20000), (20000, 50000)]
        self.bars = [0 for _ in range(len(self.bands))]
        
        self._timer = QtCore.QTimer()
        self._timer.setInterval(100)
        #self._timer.timeout.connect(self.update_values)
        self._timer.timeout.connect(self.update_equalizer)
        self._timer.start()
        
        
    def read_wave_file(self, wave_file):
        with wave.open(wave_file, 'rb') as wf:
            # sampling rate, channels, sample length
            self.rate = wf.getframerate()
            num_frames = wf.getnframes()
            # convert WAV file to numpy array
            wave_data = np.frombuffer(wf.readframes(num_frames), dtype=np.int16)
            return wave_data

    def update_equalizer(self):
        # get data as chunk_size at current position
        end_position = self.current_position + self.chunk_size
        chunk_data = self.wave_data[self.current_position:end_position]

        if len(chunk_data) == 0:
            print("file ended")
            return  # file end

        # FFT frequency analysis
        fft_data = np.abs(fft.fft(chunk_data))
        freqs = np.fft.fftfreq(len(chunk_data), 1 / self.rate)
        
        # calculate amplitude for 5 range bands
        band_amplitudes = [0] * len(self.bands)
        for i, (low, high) in enumerate(self.bands):
            band_amplitudes[i] = np.sum(fft_data[(freqs >= low) & (freqs < high)])

        #print(band_amplitudes)
        
        # bar update for each amplitude
        max_amplitude = max(band_amplitudes)
        for i, amplitude in enumerate(band_amplitudes):
            bar_height = int(100 * amplitude / max_amplitude) if max_amplitude > 0 else 0
            #self.bars[i].setRect(40 * i, 100 - bar_height, 20, bar_height)
            self.bars[i] = bar_height
        self.equalizer.setValues(self.bars)
        #print(self.bars)

        # current_position update
        self.current_position = (self.current_position + self.chunk_size) % len(self.wave_data)
        
       
    
    # random update
    def update_values(self):
        randomval = [min(100, v+random.randint(0, 50) if random.randint(0, 5) > 2 else v) for v in self.equalizer.values()]
        #print(randomval)
        self.equalizer.setValues(randomval)


app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()
