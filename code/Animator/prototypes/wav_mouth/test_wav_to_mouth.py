import array
from pydub.utils import get_array_type
from pydub import AudioSegment
from pydub.playback import play

sound = AudioSegment.from_file("example.aac", "aac")
sound = sound[1000:]
sound = sound.set_frame_rate(60)
print(sound.channels)
print(sound.sample_width)
max_amplitude = sound.max

bit_depth = sound.sample_width * 8
array_type = get_array_type(bit_depth)
numeric_array = array.array(array_type, sound.raw_data)

framesPerSecond = sound.frame_rate

audio_raw = list(numeric_array)
len_audio_file = len(audio_raw)
audio_raw_left = [audio_raw[i] for i in range(0, len_audio_file, 2)]
audio_raw_right = [audio_raw[i] for i in range(1, len_audio_file, 2)]

for sample in audio_raw_left:
	sample = abs(sample)
	print(sample/max_amplitude)


import matplotlib.pyplot as plt

plt.plot([i/framesPerSecond for i in range(len(audio_raw_left))], audio_raw_left)
#plt.plot([i/framesPerSecond for i in range(len(audio_raw_right))], audio_raw_right)
plt.show()

play(sound)
