import sys
import wave
import numpy as np
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QProgressBar

# Setting values
AudioOutput = False
FILE_PATH = "test.wav"



class AudioPlayer(QThread):
    update_equalizer = pyqtSignal(list)  # Equalizer Signal

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.chunk_size = 1024
        self.running = True
        self.framerate = 0
        self.input_device_index = 1 # [FIXME] Manual setting value 

    def run(self):
        p = pyaudio.PyAudio()

        if AudioOutput:
            # WAV file
            wf = wave.open(self.file_path, 'rb')
            self.framerate = wf.getframerate()

            # audio stream
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=self.framerate,
                output=True
            )
        else:
            self.framerate = 44100
            stream = p.open(format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            input_device_index=self.input_device_index,
            frames_per_buffer=1024)

        # read and play data
        while self.running:
            if AudioOutput:
                data = wf.readframes(self.chunk_size)
                # write stream for speaker
                stream.write(data)
            else:
                data = stream.read(1024)
            if not data:
                break

            # FFT frequency analysis
            audio_data = np.frombuffer(data, dtype=np.int16)
            fft_data = np.abs(np.fft.fft(audio_data))[:len(audio_data) // 2]  # 절반만 사용
            freqs = np.fft.fftfreq(len(audio_data), d=1/self.framerate)[:len(audio_data) // 2]
            band_amplitudes = self.calculate_bands(fft_data, freqs)

            # UI update signal 
            self.update_equalizer.emit(band_amplitudes)

        # stream end
        stream.stop_stream()
        stream.close()
        if AudioOutput:
            wf.close()
        p.terminate()

    def calculate_bands(self, fft_data, freqs):
        bands = [0, 200, 500, 1000, 5000, 20000]  # band border (Hz)
        amplitudes = []
        for i in range(len(bands) - 1):
            mask = (freqs >= bands[i]) & (freqs < bands[i + 1])
            amplitudes.append(np.mean(fft_data[mask]) if np.any(mask) else 0)
        return amplitudes

    def stop(self):
        self.running = False


class EqualizerUI(QMainWindow):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Real-Time Equalizer")
        self.setGeometry(100, 100, 400, 300)

        # Layout setting
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Equalizer Bar
        self.bars = []
        for _ in range(5):  # 대역 수에 맞게 설정
            bar = QProgressBar()
            bar.setRange(0, 100)  # 0~100 
            layout.addWidget(bar)
            self.bars.append(bar)

        # create Audio Player 
        self.audio_thread = AudioPlayer(file_path)
        self.audio_thread.update_equalizer.connect(self.update_bars)

    def start(self):
        self.audio_thread.start()

    def stop(self):
        self.audio_thread.stop()
        self.audio_thread.wait()

    def update_bars(self, amplitudes):
        """Equalizer Bar를 업데이트"""
        for i, amp in enumerate(amplitudes):
            self.bars[i].setValue(int(min(amp / 1000, 100)))  # normalize 


# 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)

    file_path = FILE_PATH  # test wave file
    main_window = EqualizerUI(file_path)
    main_window.show()

    # 재생 시작
    main_window.start()

    try:
        sys.exit(app.exec_())
    finally:
        main_window.stop()