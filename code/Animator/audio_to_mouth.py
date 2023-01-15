import cv2
import os
import numpy as np
import array

from pydub import AudioSegment
from pydub.utils import get_array_type
from PIL import ImageFont, ImageDraw, Image

from pocketsphinx import *

class AudioToMouth:
	def __init__(self, track_path, WIDTH, HEIGHT):
		self.AVERAGING_WINDOW_SECONDS = 0.3
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT
	
		self.audio_raw, self.audio_FPS, self.audio_max = self._extractAudioRaw(track_path)

		self.phoneme_list, self.phoneme_FPS = self._extractPhonemes(track_path)
		self.current_phoneme = 0

		print(self.phoneme_list)
	
	def _extractPhonemes(self, track_path):
		MODELDIR = get_model_path()

		# Create a decoder with certain model
		config = Config(lm=None)
		#config.set_string('-hmm', os.path.join(MODELDIR, 'en-us/en-us'))
		config.set_string('-allphone', os.path.join(MODELDIR, 'en-us/en-us-phone.lm.bin'))
		#config.set_string('-backtrace', 'yes')
		#config.set_float('-lw', 2.0)
		#config.set_float('-beam', 1e-20)
		#config.set_float('-pbeam', 1e-20)

		decoder = Decoder(config)

		decoder.start_utt()
		
		sound = AudioSegment.from_file(f"{track_path}.aac", "aac") 
		for segment in sound:
			decoder.process_raw(segment.raw_data, False, False)
			
		decoder.end_utt()
		
		hypothesis = decoder.hyp()
		return [{"phoneme": seg.word, "start_frame": seg.start_frame, "end_frame": seg.end_frame} for seg in decoder.seg()], 600
	
	def _extractAudioRaw(self, track_path):
		sound = AudioSegment.from_file(f"{track_path}.aac", "aac")
		#sound = sound.set_frame_rate(60)
		bit_depth = sound.sample_width * 8
		array_type = get_array_type(bit_depth)
		audio_raw_array = array.array(array_type, sound.raw_data)
		audio_raw = list(audio_raw_array)
		len_audio_raw = len(audio_raw)
		audio_raw_left = [audio_raw[i] for i in range(0, len_audio_raw, 2)]
		audio_FPS = sound.frame_rate
		audio_max = 0
		for audio_sample in audio_raw:
			audio_max = max(audio_max, abs(audio_sample))
		return audio_raw, audio_FPS, audio_max

	def _getOpennessLevel(self, frame_time):
		start_time = frame_time - self.AVERAGING_WINDOW_SECONDS / 2
		end_time = frame_time + self.AVERAGING_WINDOW_SECONDS / 2
		len_audio_raw = len(self.audio_raw)
		start_frame = max(0, int(start_time * self.audio_FPS))
		end_frame = min(len_audio_raw, int(end_time * self.audio_FPS))
	
		count = 0
		audio_sample = 0
		for audio_frame in range(start_frame, end_frame):
			audio_sample += abs(self.audio_raw[audio_frame]) / self.audio_max
			count += 1
		return audio_sample / count


	def _addCircleMouth(self, openness, image):
		pillow_image = Image.fromarray(image)

		pillow_image_draw = ImageDraw.Draw(pillow_image)
		r = 300*openness
		w = self.WIDTH / 2
		h = self.HEIGHT / 2
		corners = [
			(w - r, h - r),
			(w + r, h + r)
		]
		pillow_image_draw.ellipse(corners, fill=(0,0,0,255))
		# cv2.cvtColor(..., code): code is 0 for RGB2GBR and 1 for RGB2RGB 
		cv2_mouthed_image = cv2.cvtColor(np.array(pillow_image), 1)  
		return cv2_mouthed_image

	def addMouth(self, image, frame_time):
		audio_frame = int(frame_time * self.audio_FPS)
		phoneme_frame = int(frame_time * self.phoneme_FPS)

		if phoneme_frame > self.phoneme_list[self.current_phoneme]['end_frame']: 
			self.current_phoneme += 1
			if self.current_phoneme >= len(self.phoneme_list):
				self.current_phoneme = len(self.phoneme_list)-1


		openness = self._getOpennessLevel(frame_time)
		phoneme = self.phoneme_list[self.current_phoneme]["phoneme"]

		if phoneme in ["SIL", "+SPN+", "NSN+"]:
			phoneme = ""
		#print(audio_frame, phoneme_frame, frame_time, openness, phoneme)
		#mouthed_image = self._addCircleMouth(openness, image)

		return image, phoneme
