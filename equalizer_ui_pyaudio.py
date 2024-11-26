import sys
import wave
import numpy as np
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QAction, 
                            QFileDialog, QLabel, QDialog, QPushButton, QTabWidget, 
                            QCheckBox, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                            QRadioButton, QButtonGroup, QListWidget, QFrame, QHeaderView, QStatusBar, QProgressBar)
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
    audiostatus = pyqtSignal(bool)  # Audio End Signal

    def __init__(self, file_path, audiotype=0, device_index=0):
        super().__init__()
        self.file_path = file_path
        # frequency range setting
        self.bands = frequency_band
        self.bars = [0 for _ in range(len(self.bands))]
        self.max_amplitude = 0
        self.running = True
        self.audiotype = audiotype
        self.input_index = device_index
        self.p = pyaudio.PyAudio()

        # open WAV file
        # sampling rate, channels, sample length
        if self.audiotype == 0:
            self.wf = wave.open(self.file_path, 'rb')
            self.num_frames = self.wf.getnframes()
            self.channels = self.wf.getnchannels()
            self.rate = self.wf.getframerate()
            self.total_duration = self.num_frames / float(self.rate)
        elif self.audiotype == 1:
            self.wf = None
            self.channels = 1
            self.rate = 44100
        self.chunk_size = 1024  # audio data chunk size

    def run(self):

        # open audio stream
        if self.audiotype == 0:
            stream = self.p.open(
                format= self.p.get_format_from_width(self.wf.getsampwidth()),
                channels=self.channels,
                rate=self.rate,
                output=True,
                output_device_index=self.input_index,
            )
        elif self.audiotype == 1:
            stream = self.p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.input_index,
                frames_per_buffer=1024
            )

        # play audio data
        while self.running:
            if self.audiotype == 0:
                data = self.wf.readframes(self.chunk_size)
                if not data:
                    break
                
                # output to speaker
                stream.write(data)
            else:
                data = stream.read(1024)
                if not data:
                    break

            # FFT analysis
            audio_data = np.frombuffer(data, dtype=np.int16)
            fft_data = np.abs(np.fft.fft(audio_data))[:len(audio_data) // 2]  # 절반만 사용
            freqs = np.fft.fftfreq(len(audio_data), d=1/self.rate)[:len(audio_data) // 2]
            self.calculate_bands(fft_data, freqs)

            if self.audiotype == 0:
                current_frame = self.wf.tell()
            else:
                current_frame = 0

            # Send UI update signal
            self.update_equalizer.emit([current_frame, self.bars])

        # stream end
        stream.stop_stream()
        stream.close()
        print("stream close")
        if self.audiotype == 0:
            self.wf.close()
        self.p.terminate()
        print("pyaudio terminate")
        self.audiostatus.emit(True)

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
    def __init__(self, parent, settinginfos):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 600, 400)
        
        self.devices = settinginfos[0]
        self.selected_device_index = settinginfos[1]
        self.selected_equalizer_index = settinginfos[2]

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
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Select", "Device Name", "Input Channels", "Output Channels"])
        table.setRowCount(len(self.devices))

        self.radio_group = QButtonGroup(self)
        self.radio_group.setExclusive(True)

        for row, (index, name, inputchannels, outputchannels) in enumerate(self.devices):
            radio_button = QRadioButton()
            radio_widget = QWidget()
            radio_layout = QHBoxLayout(radio_widget)
            radio_layout.addWidget(radio_button)
            radio_layout.setAlignment(Qt.AlignCenter)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            radio_widget.setLayout(radio_layout)
            table.setCellWidget(row, 0, radio_widget)
            self.radio_group.addButton(radio_button, index)

            # column data
            table.setItem(row, 1, QTableWidgetItem(name))
            table.setItem(row, 2, QTableWidgetItem(str(inputchannels)))
            table.setItem(row, 3, QTableWidgetItem(str(outputchannels)))

            if row == self.selected_device_index:
                radio_button.setChecked(True)

        

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
            #print("Updated Frequency Bands:", self.frequency_bands)
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

        self.audioplayer = None
        self.isrunning = False
        self.init_ui()

    def init_ui(self):
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

        # Status bar with progress bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumHeight(10)  # Set height to 10 pixels
        self.progress_bar.setTextVisible(False)  # Hide text for a sleek look
        self.progress_bar.setRange(0, 100)  # Default range; updated dynamically
        self.progress_bar.setVisible(False)  # Initially hidden
        # Add progress bar to status bar's left
        self.status_bar.addPermanentWidget(self.progress_bar, 1) # Stretch factor ensures it spans to the left

        # Style using QSS
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #ddd;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #5c85d6;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4973b3;
            }
        """)
        self.checkdevices()

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
        self.audioplayer = AudioPlayer(file_path, audiotype=0, device_index=self.selected_device_index)
        self.audioplayer.update_equalizer.connect(self.update_bars)
        self.audioplayer.audiostatus.connect(self.checkaudiostatus)
        self.start()
        
    # input audio signal from mic
    def onInputAudioMenu(self):
        # check device has input channels
        if self.devices[self.selected_device_index][2] == 0:
            self.status_bar.showMessage("No Input Device. Select a input device in setting.")
            return

        self.commandtype = 1
        if self.isrunning:
            self.stop()

        self.audioplayer = AudioPlayer(file_path=None, audiotype=1, device_index=self.selected_device_index)
        self.audioplayer.update_equalizer.connect(self.update_bars)
        self.audioplayer.audiostatus.connect(self.checkaudiostatus)
        self.start()


                
    def onStopMenu(self):
        self.stop()

    def onSettingMenu(self):
        global frequency_band

        self.checkdevices()

        dialog = SettingsDialog(self, [self.devices, self.selected_device_index, self.selected_equalizer_index])
        if dialog.exec_() == QDialog.Accepted:
            selected_index = dialog.selected_device_index
            if selected_index is not None:
                device_name = [d[1] for d in self.devices if d[0] == selected_index][0]
                self.status_bar.showMessage(f"Selected device: {device_name} (Index: {selected_index})")
            else:
                self.status_bar.showMessage("No device selected.")
            self.selected_device_index = selected_index
            self.selected_equalizer_index = dialog.selected_equalizer_index
            self.equalizer.setColorPreset(color_presets[self.selected_equalizer_index])

            frequency_band = dialog.frequency_bands
        
    def checkdevices(self):
        self.devices = []
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            self.devices.append((dev['index'], dev['name'], dev['maxInputChannels'], dev['maxOutputChannels']))

        default_output_device_info = p.get_default_output_device_info()
        self.selected_device_index = default_output_device_info['index']

        p.terminate()


    def start(self):
        self.audioplayer.start()
        self.isrunning = True
        
        if self.audioplayer.audiotype == 0:
            # Show progress bar and clear status message
            self.progress_bar.setVisible(True)
            self.status_bar.clearMessage()
            # Update slider range
            self.progress_bar.setRange(0, int(self.audioplayer.total_duration * 1000))  # Milliseconds


    def stop(self):
        if self.audioplayer is None:
            return
        self.audioplayer.stop()
        self.audioplayer.wait()
        self.isrunning = False

    def update_bars(self, audioinfos):
        current_frame = audioinfos[0]
        amplitudes = audioinfos[1]
        current_time = current_frame / float(self.audioplayer.rate)
        self.progress_bar.setValue(int(current_time * 1000))  # Milliseconds
        self.equalizer.setValues(amplitudes)

    def checkaudiostatus(self, status):
        if status:
            # Hide progress bar and show a status message
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Stopped", 2000)

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