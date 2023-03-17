from os import environ, path

from pocketsphinx import *
import wave
from pydub import AudioSegment
from pydub.utils import get_array_type
import array

MODELDIR = get_model_path()

print(MODELDIR)
DATADIR = "."

# Create a decoder with certain model
config = Config(lm=None)
config.set_string('-hmm', path.join(MODELDIR, 'en-us/en-us'))
config.set_string('-allphone', path.join(MODELDIR, 'en-us/en-us-phone.lm.bin'))
config.set_string('-backtrace', 'yes')
config.set_float('-lw', 2.0)
config.set_float('-beam', 1e-20)
config.set_float('-pbeam', 1e-20)

# Decode streaming data.
decoder = Decoder(config)

decoder.start_utt()
#stream = open(path.join(DATADIR, 'example.raw'), 'rb')

sound = AudioSegment.from_file("example.aac", "aac") 
a = 0
for segment in sound:
	a += 1
	decoder.process_raw(segment.raw_data, False, False)
print(a)
print()

decoder.end_utt()

hypothesis = decoder.hyp()
print ('Phonemes: ', [(seg.word, seg.start_frame, seg.end_frame) for seg in decoder.seg()])
'''
'''