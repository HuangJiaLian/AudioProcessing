import pyaudio
import wave

p = pyaudio.PyAudio()

FORMAT = pyaudio.paInt16
FS = 44100
CHANNELS = 1
CHUNK = 1024
RECORD_SECOND = 5

stream = p.open(format=FORMAT, channels=CHANNELS,\
          rate=FS, input=True, frames_per_buffer=CHUNK)

print('* recording')

frames = []
num_times = int(RECORD_SECOND * FS / CHUNK)

for i in range(num_times):
    data = stream.read(CHUNK)
    frames.append(data)

print('Done')

stream.start_stream()
stream.close()
p.terminate()

print(frames)

samplewidth = p.get_sample_size(FORMAT)


wf = wave.open('output.wav', 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(samplewidth)
wf.setframerate(FS)
wf.writeframes(b''.join(frames))
wf.close()