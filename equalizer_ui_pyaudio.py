import sys
import wave
import numpy as np
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QProgressBar
from equalizer_bar import EqualizerBar


class AudioPlayer(QThread):
    update_equalizer = pyqtSignal(list)  # Equalizer 데이터를 업데이트하는 Signal

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.chunk_size = 1024  # 오디오 데이터 청크 크기
        self.running = True

    def run(self):
        # WAV 파일 열기
        wf = wave.open(self.file_path, 'rb')
        p = pyaudio.PyAudio()

        # 오디오 스트림 열기
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )

        # 데이터 읽기 및 재생
        while self.running:
            data = wf.readframes(self.chunk_size)
            if not data:
                break

            # 스트림에 데이터 쓰기
            stream.write(data)

            # FFT로 주파수 분석
            audio_data = np.frombuffer(data, dtype=np.int16)
            fft_data = np.abs(np.fft.fft(audio_data))[:len(audio_data) // 2]  # 절반만 사용
            freqs = np.fft.fftfreq(len(audio_data), d=1/wf.getframerate())[:len(audio_data) // 2]
            band_amplitudes = self.calculate_bands(fft_data, freqs)

            # UI 업데이트 신호 전송
            self.update_equalizer.emit(band_amplitudes)

        # 스트림 종료
        stream.stop_stream()
        stream.close()
        wf.close()
        p.terminate()

    def calculate_bands(self, fft_data, freqs):
        """주파수 대역별 평균 진폭 계산"""
        bands = [0, 200, 500, 1000, 5000, 20000]  # 대역 경계값 (Hz)
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

        # Layout 설정
        self.equalizer = EqualizerBar(10, ['#0C0786', '#40039C', '#6A00A7', '#8F0DA3', '#B02A8F', '#CA4678', '#E06461',
                                          '#F1824C', '#FCA635', '#FCCC25', '#EFF821'])
        self.setCentralWidget(self.equalizer)
        
        # Audio Player 설정
        self.audio_thread = AudioPlayer(file_path)
        self.audio_thread.update_equalizer.connect(self.update_bars)

    def start(self):
        self.audio_thread.start()

    def stop(self):
        self.audio_thread.stop()
        self.audio_thread.wait()

    def update_bars(self, amplitudes):
        """Equalizer Bar를 업데이트"""
        #for i, amp in enumerate(amplitudes):
        #    self.bars[i].setValue(int(min(amp / 1000, 100)))  # 적절히 정규화
        self.equalizer.setValues(amplitudes)

# 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)

    file_path = "test.wav"  # 테스트할 WAV 파일 경로
    main_window = EqualizerUI(file_path)
    main_window.show()

    # 재생 시작
    main_window.start()

    try:
        sys.exit(app.exec_())
    finally:
        main_window.stop()