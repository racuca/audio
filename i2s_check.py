import pyaudio

p = pyaudio.PyAudio()
for ii in range(0, p.get_device_count()):
    print(p.get_device_info_by_index(ii))
    

default_output_device_info = p.get_default_output_device_info()
print(default_output_device_info)

for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print((dev['index'], dev['name'], dev['maxInputChannels'], dev['maxOutputChannels']))