# fft matplotlib by racuca
# 2024.10.31
# fft + command prompt interaction


import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile


filename = "data/2024_10_31_14_11_17_pyaudio.wav"
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
        
# FFT
yf = np.fft.fft(data)
xf = np.fft.fftfreq(N, 1 / sample_rate)

# filtering
res = input("do you want to filtering(remove freqs)?[y/n]") 
if res.lower() == "y":
    while True:
        res = input("input range(ex> 0,100) => ")
        # frequencies to zero
        low_cutoff = int(res.split(',')[0])
        high_cutoff = int(res.split(',')[1])
        yf[(xf > low_cutoff) & (xf < high_cutoff)] = 0
        yf[(xf < -low_cutoff) & (xf > -high_cutoff)] = 0
        res = input("more range? [y/n]")
        if res == "n":
            break
        
    res = input("Do you want to plot range manually? [y/n]")
    if res == "y":
        res = input("range to plot(default-> 1000,20000) => ")
        if res == "":
            low = 1000
            high = 20000
        else:
            low = int(res.split(',')[0])
            high = int(res.split(',')[1])
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

    else:
        
        
        # original spectrum
        plt.figure(figsize=(12, 6))
        plt.subplot(2,1,1)
        plt.plot(xf[:N // 2], np.abs(np.fft.fft(data))[:N//2])
        plt.title("Original Frequency Spectrum")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        
        # filtered spectrum
        plt.subplot(2,1,2)
        plt.plot(xf[:N // 2], np.abs(yf[:N//2]))
        plt.title("Filtered Frequency Spectrum")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        plt.tight_layout()
        plt.show()
        
        res = input("save filtered data?[y/n] ")
        if res == "y":
            # ifft
            filtered_data = np.fft.ifft(yf)
            filtered_data = np.real(filtered_data).astype(data.dtype)
            wavfile.write("filtered_" + filename, sample_rate, filtered_data)
else:
    plt.figure(figsize = (10, 6))
    plt.plot(xf[:N // 2], np.abs(yf[:N//2]))
    plt.title("Frequency Spectrum of WAV File")
    plt.xlabel("Freq (Hz)")
    plt.ylabel("Amplitude")
    plt.show()
    
