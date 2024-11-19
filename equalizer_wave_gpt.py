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

        # 주파수 구간 설정 (5개의 대역)
        self.bands = [(20, 100), (100, 500), (500, 1000), (1000, 5000), (5000, 20000)]
        self.bars = [QGraphicsRectItem(0, 0, 20, 100) for _ in range(len(self.bands))]
        for i, bar in enumerate(self.bars):
            bar.setBrush(Qt.green)
            bar.setPos(40 * i, 0)
            self.scene.addItem(bar)

        self.view.setFixedSize(800,400)  # 화면 왼쪽상단에 작게 나오는 문제 수정
            
        self.wave_file = wave_file
        self.wave_data = self.read_wave_file(self.wave_file)
        self.chunk_size = 1024  # 한 번에 읽을 샘플의 수
        self.rate = 44100  # WAV 파일의 샘플링 레이트
        self.current_position = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_equalizer)
        self.timer.start(50)  # 50ms마다 업데이트

    def read_wave_file(self, wave_file):
        """WAV 파일에서 데이터를 읽어들임"""
        with wave.open(wave_file, 'rb') as wf:
            # 샘플링 레이트, 채널 수, 샘플 길이 등을 가져옵니다
            self.rate = wf.getframerate()
            num_frames = wf.getnframes()
            # WAV 파일의 데이터를 읽어 NumPy 배열로 변환
            wave_data = np.frombuffer(wf.readframes(num_frames), dtype=np.int16)
            return wave_data

    def update_equalizer(self):
        """실시간 equalizer 업데이트"""
        # 현재 위치에서 chunk_size만큼 데이터를 가져옴
        end_position = self.current_position + self.chunk_size
        chunk_data = self.wave_data[self.current_position:end_position]

        if len(chunk_data) == 0:
            return  # 파일 끝에 도달했을 때

        # FFT로 주파수 분석
        fft_data = np.abs(fft.fft(chunk_data))
        freqs = np.fft.fftfreq(len(chunk_data), 1 / self.rate)
        
        # 5개 대역에 대해 진폭 계산
        band_amplitudes = [0] * len(self.bands)
        for i, (low, high) in enumerate(self.bands):
            band_amplitudes[i] = np.sum(fft_data[(freqs >= low) & (freqs < high)])

        # 각 대역의 진폭에 맞게 바 높이 업데이트
        max_amplitude = max(band_amplitudes)
        for i, amplitude in enumerate(band_amplitudes):
            bar_height = int(100 * amplitude / max_amplitude) if max_amplitude > 0 else 0
            self.bars[i].setRect(40 * i, 100 - bar_height, 20, bar_height)

        # current_position 업데이트
        self.current_position = (self.current_position + self.chunk_size) % len(self.wave_data)

    def closeEvent(self, event):
        event.accept()

if __name__ == "__main__":
    wave_file = 'your_audio_file.wav'  # 여기에 사용하고자 하는 WAV 파일 경로를 넣어주세요
    app = QApplication([])
    window = EqualizerWindow(wave_file)
    window.show()
    app.exec_()
