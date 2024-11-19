import numpy as np
import wave
import scipy.fftpack as fft
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QPainter

class EqualizerWindow(QMainWindow):
    def __init__(self, wave_file):
        super().__init__()
        self.setWindowTitle("Real-time Audio Equalizer")
        self.setGeometry(100, 100, 800, 400)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)

        # frequency range setting ( 5 ranges )
        self.bands = [(20, 100), (100, 500), (500, 1000), (1000, 5000), (5000, 20000)]
        self.bars = [QGraphicsRectItem(0, 0, 20, 100) for _ in range(len(self.bands))]
        for i, bar in enumerate(self.bars):
            bar.setBrush(Qt.green)
            bar.setPos(40 * i, 0)
            self.scene.addItem(bar)

        self.view.setFixedSize(800,400) 
            
        self.wave_file = wave_file
        self.wave_data = self.read_wave_file(self.wave_file)
        self.chunk_size = 1024  # one time sample count
        self.rate = 44100  # WAV file sampling rate
        self.current_position = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_equalizer)
        self.timer.start(50)  # 50ms update

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
            return  # file end

        # FFT frequency analysis
        fft_data = np.abs(fft.fft(chunk_data))
        freqs = np.fft.fftfreq(len(chunk_data), 1 / self.rate)
        
        # calculate amplitude for 5 range bands
        band_amplitudes = [0] * len(self.bands)
        for i, (low, high) in enumerate(self.bands):
            band_amplitudes[i] = np.sum(fft_data[(freqs >= low) & (freqs < high)])

        # bar update for each amplitude
        max_amplitude = max(band_amplitudes)
        for i, amplitude in enumerate(band_amplitudes):
            bar_height = int(100 * amplitude / max_amplitude) if max_amplitude > 0 else 0
            self.bars[i].setRect(40 * i, 100 - bar_height, 20, bar_height)

        # current_position update
        self.current_position = (self.current_position + self.chunk_size) % len(self.wave_data)

    def closeEvent(self, event):
        event.accept()

if __name__ == "__main__":
    wave_file = 'your_audio_file.wav'  
    app = QApplication([])
    window = EqualizerWindow(wave_file)
    window.show()
    app.exec_()
