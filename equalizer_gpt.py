import numpy as np
import pyaudio
import wave
import scipy.fftpack as fft
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QPainter

class EqualizerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-time Audio Equalizer")
        self.setGeometry(100, 100, 800, 400)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)

        # 주파수 구간 설정 (5개의 대역)
        self.bands = [(20, 100), (100, 500), (500, 1000), (1000, 5000), (5000, 20000)]
        self.bars = [QGraphicsRectItem(0, 0, 20, 100) for _ in range(len(self.bands))]
        for i, bar in enumerate(self.bars):
            bar.setBrush(Qt.green)
            bar.setPos(40 * i, 0)
            self.scene.addItem(bar)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_equalizer)
        self.timer.start(50)  # 50ms마다 업데이트

        self.pyaudio_stream = None
        self.chunk_size = 1024
        self.rate = 44100
        self.open_stream()

    def open_stream(self):
        self.pyaudio_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                                     channels=1,
                                                     rate=self.rate,
                                                     input=True,
                                                     frames_per_buffer=self.chunk_size)

    def update_equalizer(self):
        # 오디오 데이터 읽기
        audio_data = np.frombuffer(self.pyaudio_stream.read(self.chunk_size), dtype=np.int16)
        
        # FFT로 주파수 분석
        fft_data = np.abs(fft.fft(audio_data))
        freqs = np.fft.fftfreq(len(audio_data), 1 / self.rate)
        
        # 5개 대역에 대해 진폭 계산
        band_amplitudes = [0] * len(self.bands)
        for i, (low, high) in enumerate(self.bands):
            band_amplitudes[i] = np.sum(fft_data[(freqs >= low) & (freqs < high)])

        # 각 대역의 진폭에 맞게 바 높이 업데이트
        max_amplitude = max(band_amplitudes)
        for i, amplitude in enumerate(band_amplitudes):
            bar_height = int(100 * amplitude / max_amplitude) if max_amplitude > 0 else 0
            self.bars[i].setRect(40 * i, 100 - bar_height, 20, bar_height)

    def closeEvent(self, event):
        if self.pyaudio_stream:
            self.pyaudio_stream.stop_stream()
            self.pyaudio_stream.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    window = EqualizerWindow()
    window.show()
    app.exec_()