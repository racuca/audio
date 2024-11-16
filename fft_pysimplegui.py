# fft matplotlib by racuca
# 2024.10.31
# fft + PySimpleGUI  


import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import PySimpleGUI as sg


def amplitude_time(filename):
    #filename = "data/2024_10_31_14_11_17_pyaudio.wav"
    sample_rate, data = wavfile.read(filename)

    # if stereo, select only one channel
    if len(data.shape) > 1:
        data = data[:, 0]

    N = len(data) # length of sample
    time = np.linspace(0, N / sample_rate, N)

    plt.figure(figsize=(12,6))
    plt.plot(time, data)
    plt.title("Amplitude over Time")
    plt.xlabel("Time(s)")
    plt.ylabel("Amplitude")
    plt.show(block=True)

        
def fft(filename, freqranges):
    sample_rate, data = wavfile.read(filename)
    # if stereo, select only one channel
    if len(data.shape) > 1:
        data = data[:, 0]
    N = len(data) # length of sample
    time = np.linspace(0, N / sample_rate, N)
    
    # FFT
    yf = np.fft.fft(data)
    xf = np.fft.fftfreq(N, 1 / sample_rate)

    rangelist = freqranges.split('|')
    # filtering
    for res in rangelist:
        # frequencies to zero
        low_cutoff = int(res.split(',')[0])
        high_cutoff = int(res.split(',')[1])
        yf[(xf > low_cutoff) & (xf < high_cutoff)] = 0
        yf[(xf < -low_cutoff) & (xf > -high_cutoff)] = 0

    low = int(values['-MIN X-'])
    high = int(values['-MAX X-'])
    freq_range = (xf >= low) & (xf <= high)
    yf_filtered = yf.copy()
    xf_filtered_range = xf[freq_range]
    yf_filtered_range = np.abs(yf_filtered)[freq_range]
    yf_org = np.abs(yf)[freq_range]
        
    # original spectrum
    plt.figure(figsize=(12,6))
    plt.subplot(2,1,1)
    plt.plot(xf_filtered_range, yf_org)
    plt.title("Original Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")

    # filtered spectrum
    plt.subplot(2,1,2)
    plt.plot(xf_filtered_range, yf_filtered_range)
    plt.title("Filtered Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()
    
    # original spectrum
    #plt.figure(figsize=(12, 6))
    #plt.subplot(2,1,1)
    #plt.plot(xf[:N // 2], np.abs(np.fft.fft(data))[:N//2])
    #plt.title("Original Frequency Spectrum")
    #plt.xlabel("Frequency (Hz)")
    #plt.ylabel("Amplitude")
    
    # filtered spectrum
    #plt.subplot(2,1,2)
    #plt.plot(xf[:N // 2], np.abs(yf[:N//2]))
    #plt.title("Filtered Frequency Spectrum")
    #plt.xlabel("Frequency (Hz)")
    #plt.ylabel("Amplitude")
    #plt.tight_layout()
    #plt.show(block=False)
        
    # ifft
    #filtered_data = np.fft.ifft(yf)
    #filtered_data = np.real(filtered_data).astype(data.dtype)
    #wavfile.write("filtered_" + filename, sample_rate, filtered_data)

    # Original Frequency Spectrum
    #plt.figure(figsize = (10, 6))
    #plt.plot(xf[:N // 2], np.abs(yf[:N//2]))
    #plt.title("Frequency Spectrum of WAV File")
    #plt.xlabel("Freq (Hz)")
    #plt.ylabel("Amplitude")
    #plt.show()
    
    
    



left_col = [
    [sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
    [sg.Listbox(values=[], enable_events=True, size=(40,20),key='-FILE LIST-')],
]

# For now will only show the name of the file that was chosen
images_col = [[sg.Text('You choose from the list:')],
              [sg.Text(key='-TOUT-')],
              [sg.Button("Show Amplitude over Time", key='-BTNTIME-')],
              [sg.Text('Input Frequency ranges to remove. ex> 0,1000|2000,3000')],
              [sg.Input('0,1000', key='-RANGE TO REMOVE-')],
              [sg.Text('Input Frequency x Axis Range.')],
              [sg.Input('0', key='-MIN X-', size=(10, 20)), sg.Text('~'), sg.Input('20000', key='-MAX X-',size=(10,20))],
              [sg.Button('Show Frequency Graph', key='-BTNFFT-')]
            ]

# ----- Full layout -----
layout = [[sg.Column(left_col, element_justification='c'), sg.VSeperator(),sg.Column(images_col, element_justification='c')]]

# --------------------------------- Create Window ---------------------------------
window = sg.Window('Wave File Audio Frequency Viewer', layout,resizable=True)

filename = ""

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        exit()
    elif event == sg.WIN_CLOSED or event == 'Exit':
        exit()
    elif event == '-FOLDER-':                         # Folder name was filled in, make a list of files in the folder
        folder = values['-FOLDER-']
        try:
            file_list = os.listdir(folder)         # get list of files in folder
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".wav"))]
        fnames.sort()
        window['-FILE LIST-'].update(fnames)
    elif event == '-FILE LIST-':    # A file was chosen from the listbox
        try:
            filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
            window['-TOUT-'].update(filename)
        except Exception as E:
            print(f'** Error {E} **')
            pass
    elif event == '-BTNTIME-':
        amplitude_time(filename)
    elif event == '-BTNFFT-':
        ranges = values['-RANGE TO REMOVE-']
        fft(filename, ranges)
    elif event == '-RANGE TO REMOVE-':
        ranges = values['-RANGE TO REMOVE-']
window.close()
