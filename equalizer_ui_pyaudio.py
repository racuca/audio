import sys
import wave
import numpy as np
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QAction, 
                            QFileDialog, QLabel, QDialog, QPushButton, QTabWidget, 
                            QCheckBox, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                            QRadioButton, QButtonGroup, QListWidget, QFrame, QHeaderView)
from equalizer_bar import EqualizerBar

# 예제 색상 프리셋 (12단계)
color_presets = {
    0: ['#FF0000', '#FF4500', '#FFA500', '#FFFF00', '#ADFF2F', '#00FF00', '#32CD32', '#40E0D0', '#1E90FF', '#0000FF', '#8A2BE2', '#9400D3'],
    1: ['#9400D3', '#8A2BE2', '#0000FF', '#1E90FF', '#40E0D0', '#32CD32', '#00FF00', '#ADFF2F', '#FFFF00', '#FFA500', '#FF4500', '#FF0000'],
    2: ['#0C0786', '#260392', '#40039C', '#5904A4', '#6A00A7', '#8F0DA3', '#B02A8F', '#CA4678', '#E06461', '#F1824C', '#FCA635', '#EFF821'],
    3: ['#1B263B', '#23314C', '#2D3E60', '#3C4A69', '#4E5F85', '#586994', '#7796B5', '#99B8D4', '#B0D4E3', '#D2E7F2', '#EAF2F8', '#F5F9FD'],
    4: ['#3B302F', '#4A423F', '#5A504D', '#785C4F', '#9B7B59', '#C89E6A', '#E4B97B', '#EBDCA8', '#F5EAD3', '#D2C197', '#B89C6E', '#8A6E4B'],
    5: ['#2E2927', '#4A403E', '#6B5A57', '#866D60', '#A27F68', '#BD956F', '#D4AC80', '#E8C898', '#F5E3B4', '#D8BA88', '#B99C6B', '#8D704D'],
    6: ['#00FF7F'] * 12,  # 단색 Preset
    7: ['#FFD700'] * 12,
    8: ['#DC143C'] * 12,
    9: ['#DC143C'] * 12,
    10: ['#FFFFFF'] * 12
}

frequency_band = [(20, 300), (300, 500), (500, 800), (800, 1200), (1200, 2000),
                      (2000, 3000), (3000, 5000), (5000, 10000),(10000, 20000), (20000, 50000)]

class AudioPlayer(QThread):
    update_equalizer = pyqtSignal(list)  # Equalizer Signal

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.chunk_size = 1024  # audio data chunk size
        # frequency range setting ( 5 ranges )
        self.bands = frequency_band
        self.bars = [0 for _ in range(len(self.bands))]
        self.rate = 0
        self.num_frames = 0
        self.max_amplitude = 0
        self.running = True

    def run(self):
        # open WAV file
        wf = wave.open(self.file_path, 'rb')
        p = pyaudio.PyAudio()

        # sampling rate, channels, sample length
        self.rate = wf.getframerate()
        self.num_frames = wf.getnframes()
        #print("frame num : ", self.num_frames)

        # open audio stream
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )

        # play audio data
        read_cnt = 0
        while self.running:
            data = wf.readframes(self.chunk_size)
            if not data:
                break
            read_cnt += 1
            #print(read_cnt * 1024)
            
            # output to speaker
            stream.write(data)

            # FFT analysis
            audio_data = np.frombuffer(data, dtype=np.int16)
            fft_data = np.abs(np.fft.fft(audio_data))[:len(audio_data) // 2]  # 절반만 사용
            freqs = np.fft.fftfreq(len(audio_data), d=1/wf.getframerate())[:len(audio_data) // 2]
            self.calculate_bands(fft_data, freqs)

            # Send UI update signal
            self.update_equalizer.emit(self.bars)

        # stream end
        stream.stop_stream()
        stream.close()
        wf.close()
        p.terminate()

    def calculate_bands(self, fft_data, freqs):
        band_amplitudes = [0] * len(self.bands)
        for i, (low, high) in enumerate(self.bands):
            band_amplitudes[i] = np.sum(fft_data[(freqs >= low) & (freqs < high)])

        # bar update for each amplitude        
        instance_max = max(band_amplitudes)
        if instance_max < 10000:  # assume noise below 10000 
            self.max_amplitude = 0
        else:
            self.max_amplitude = max(instance_max, self.max_amplitude)
        for i, amplitude in enumerate(band_amplitudes):
            bar_height = int(100 * amplitude / self.max_amplitude) if self.max_amplitude > 0 else 0
            self.bars[i] = bar_height

    def stop(self):
        self.running = False


class EqualizerPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃 (수평)
        layout = QHBoxLayout()

        # 왼쪽: Color 리스트 (QListWidget)
        self.color_list = QListWidget()
        self.color_list.addItems([f"Preset {i + 1}" for i in range(len(color_presets))])  # 5개의 프리셋 추가
        self.color_list.currentRowChanged.connect(self.update_preview)  # 선택 변경 시 핸들러 연결
        layout.addWidget(self.color_list, 1)

        # 오른쪽: Equalizer 색상 바 미리보기
        self.preview_frame = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_frame)
        self.preview_frame.setStyleSheet("background-color: black;")

        # 12단계 Equalizer Bar 추가
        self.bars = []
        for i in range(12):
            bar = QFrame()
            bar.setFixedHeight(20)
            bar.setStyleSheet("background-color: black;")
            self.bars.append(bar)
            self.preview_layout.addWidget(bar)

        layout.addWidget(self.preview_frame, 1)
        self.setLayout(layout)
        self.selected_equalizer_index = 0

    def update_preview(self, row):
        """
        Bar color update
        """

        # 선택한 프리셋 색상으로 Bar 업데이트
        if row in color_presets:
            colors = color_presets[row]
            for i, bar in enumerate(self.bars):
                bar.setStyleSheet(f"background-color: {colors[i]};")
        
        self.selected_color_index = row


class SettingsDialog(QDialog):
    def __init__(self, parent, devices, colorpresetnum):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 600, 400)
        
        self.selected_device_index = None  # 선택한 디바이스 인덱스
        self.devices = devices
        self.selected_equalizer_index = colorpresetnum

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings dialog."))

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.create_audio_tab()
        self.create_preview_tab()
        self.create_frequencyband_tab()

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def showEvent(self, event):
        """Override showEvent to center the dialog."""
        self.center()
        super().showEvent(event)
    
    def center(self):
        """Center the dialog in the parent window."""
        if self.parent():
            parent_geometry = self.parent().geometry()
            dialog_geometry = self.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - dialog_geometry.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_geometry.height()) // 2
            self.move(x, y)

    def create_audio_tab(self):
        """Audio Settings Tab"""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Select", "Device Name", "Input Channels"])
        table.setRowCount(len(self.devices))

        self.radio_group = QButtonGroup(self)
        self.radio_group.setExclusive(True)

        for row, (index, name, channels) in enumerate(self.devices):
            radio_button = QRadioButton()
            radio_widget = QWidget()
            radio_layout = QHBoxLayout(radio_widget)
            radio_layout.addWidget(radio_button)
            radio_layout.setAlignment(Qt.AlignCenter)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            radio_widget.setLayout(radio_layout)
            table.setCellWidget(row, 0, radio_widget)
            self.radio_group.addButton(radio_button, index)

            # Device Name
            table.setItem(row, 1, QTableWidgetItem(name))

            # Input Channels
            table.setItem(row, 2, QTableWidgetItem(str(channels)))

        # 테이블 옵션
        table.resizeColumnsToContents()
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # 셀 편집 비활성화

        tab_layout.addWidget(table)
        self.tabs.addTab(tab, "Audio Settings")
    
    # Equalizer Preview tab
    def create_preview_tab(self):
        self.equalizer_tab = EqualizerPreview()
        self.equalizer_tab.update_preview(self.selected_equalizer_index)
        self.tabs.addTab(self.equalizer_tab, "Equalizer Preview")

    # Frequency band Tab
    def create_frequencyband_tab(self):
        self.freqband_tab = QWidget()        
        layout = QVBoxLayout()

        # Frequency bands: (Low, High)
        self.frequency_bands = frequency_band
        # Table for frequency bands
        self.freqband_table = QTableWidget(len(self.frequency_bands), 2)
        self.freqband_table.setHorizontalHeaderLabels(["Low Frequency (Hz)", "High Frequency (Hz)"])
        self.freqband_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.populate_table(self.freqband_table)
        layout.addWidget(self.freqband_table)

        self.freqband_tab.setLayout(layout)
        self.tabs.addTab(self.freqband_tab, "Frequency Bands")
    
    #Populate the table with the current frequency bands.
    def populate_table(self, table):
        for row, (low, high) in enumerate(self.frequency_bands):
            low_item = QTableWidgetItem(str(low))
            high_item = QTableWidgetItem(str(high))
            table.setItem(row, 0, low_item)
            table.setItem(row, 1, high_item)


    def accept(self):
        # audio device tab
        selected_button = self.radio_group.checkedButton()
        if selected_button:
            self.selected_device_index = self.radio_group.id(selected_button)
        
        # equalizer tab
        self.selected_equalizer_index = self.equalizer_tab.selected_color_index

        # frequency band tab
        try:
            updated_bands = []
            for row in range(self.freqband_table.rowCount()):
                low = int(self.freqband_table.item(row, 0).text())
                high = int(self.freqband_table.item(row, 1).text())
                if low >= high:
                    raise ValueError(f"Low frequency ({low}) must be less than High frequency ({high}).")
                updated_bands.append((low, high))
            
            self.frequency_bands = updated_bands
            print("Updated Frequency Bands:", self.frequency_bands)
        except ValueError as e:
            print(f"Error: {e}")

        super().accept()


class EqualizerUI(QMainWindow):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Real-Time Equalizer")

        self.colorpresetnum = 0
        # Layout setting
        self.equalizer = EqualizerBar(10, color_presets[self.colorpresetnum])
        self.devices = []
        self.selected_device_index = 0 # for input audio
        self.selected_equalizer_index = 0

        self.setCentralWidget(self.equalizer)
        
        button_action = QAction("&Play Wave File", self)
        button_action.setStatusTip("Load a wave File and play it.")
        button_action.triggered.connect(self.onWaveFileMenu)
        button_action.setCheckable(False)
        button_action2 = QAction("&Input Audio", self)
        button_action2.setStatusTip("Audio Signal Equalizer")
        button_action2.triggered.connect(self.onInputAudioMenu)
        button_action2.setCheckable(False)
        button_action3 = QAction("&Stop", self)
        button_action3.setStatusTip("Stop command")
        button_action3.triggered.connect(self.onStopMenu)
        button_action3.setCheckable(False)

        button_action4 = QAction("&Setting", self)
        button_action4.setStatusTip("Setting")
        button_action4.triggered.connect(self.onSettingMenu)

        menu = self.menuBar()
        file_menu = menu.addMenu("&Audio")
        file_menu.addAction(button_action)
        file_menu.addAction(button_action2)
        file_menu.addSeparator()
        file_menu.addAction(button_action3)
        options = menu.addMenu("&Options")
        options.addAction(button_action4)

        self.audio_thread = None
        self.isrunning = False

    # play wave file
    def onWaveFileMenu(self):
        self.commandtype = 0
        self.fileName = QFileDialog.getOpenFileName(self,'Wave File','','*.wav')
        if self.fileName is None or self.fileName[0] == '':
            return
        file_path = self.fileName[0]

        if self.isrunning:
            self.stop()
            
        # Audio Player 
        self.audio_thread = AudioPlayer(file_path)
        self.audio_thread.update_equalizer.connect(self.update_bars)
        self.start()
        
    # input audio signal from mic
    def onInputAudioMenu(self):
        self.commandtype = 1
                
    def onStopMenu(self):
        self.stop()

    def onSettingMenu(self):
        global frequency_band

        self.devices = []
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            self.devices.append((i, dev['name'], dev['maxInputChannels']))

        dialog = SettingsDialog(self, self.devices, self.selected_equalizer_index)
        if dialog.exec_() == QDialog.Accepted:
            selected_index = dialog.selected_device_index
            if selected_index is not None:
                device_name = [d[1] for d in self.devices if d[0] == selected_index][0]
                self.statusBar().showMessage(f"Selected device: {device_name} (Index: {selected_index})")
            else:
                self.statusBar().showMessage("No device selected.")
            self.selected_device_index = selected_index
            self.selected_equalizer_index = dialog.selected_equalizer_index
            self.equalizer.setColorPreset(color_presets[self.selected_equalizer_index])

            frequency_band = dialog.frequency_bands

    def start(self):
        self.audio_thread.start()
        self.isrunning = True

    def stop(self):
        if self.audio_thread is None:
            return
        self.audio_thread.stop()
        self.audio_thread.wait()
        self.isrunning = False

    def update_bars(self, amplitudes):
        self.equalizer.setValues(amplitudes)

# main
if __name__ == "__main__":
    app = QApplication(sys.argv)

    file_path = "data/lvb-sym-5-1.wav"
    main_window = EqualizerUI(file_path)
    main_window.show()

    try:
        sys.exit(app.exec_())
    finally:
        main_window.stop()