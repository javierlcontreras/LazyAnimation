import cv2
import os
import numpy as np
import array

from pydub import AudioSegment
from pydub.utils import get_array_type
from PIL import ImageFont, ImageDraw, Image

from pocketsphinx import *
import requests


phoneme2mouth = {
	"aa": "a",
	"ae": "a",
	"ah": "a",
	"ao": "a",
	"aw": "au",
	"ay": "ay",
	"b": "m",
	"ch": "t",
	"d": "t",
	"dh": "t",
	"eh": "a",
	"er": "u",
	"ey": "ay",
	"f": "f",
	"g": "t",
	"hh": "y",
	"ih": "a",
	"iy": "ay",
	"jh": "t",
	"k": "t",
	"l": "y",
	"m": "m",
	"n": "t",
	"ng": "t",
	"ow": "au",
	"oy": "ua",
	"p": "m",
	"r": "u",
	"s": "t",
	"sh": "t",
	"t": "t",
	"th": "t",
	"uh": "u",
	"uw": "u",
	"v": "f",
	"w": "u",
	"y": "y",
	"z": "t",
	"zh": "t",
	"empty": "m" # For unknown phonemes, the stick figure will just have a closed mouth ("mmm")
}

class AudioToMouth:
	def __init__(self, track_path, docker_url, ART_PATHS, WIDTH, HEIGHT):
		self.AVERAGING_WINDOW_SECONDS = 0.3
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT
		self.ART_PATHS = ART_PATHS
		
		self.docker_url = docker_url

		# self.audio_raw, self.audio_FPS, self.audio_max = self._extractAudioRaw(track_path)

		self.phoneme_list = self._extractPhonemes(track_path)
		self.current_phoneme = 0

	def _requestHTTPGentle(self):
		params = {
		    'async': 'false',
		}

		files = {
		    'audio': open('video_files/example.aac', 'rb'),
		    'transcript': open('video_files/example_gentle.txt', 'rb'),
		}

		response = requests.post(self.docker_url, params=params, files=files)
		
		return response.json()["words"]
	
	def _addPhoneme(self, phoneme_list, phoneme, start_time, end_time):
		phoneme_list.append({
			"phoneme": phoneme,
			"start_time":start_time,
			"end_time":end_time
		})

	def _extractPhonemes(self, track_path):
		json = self._requestHTTPGentle()
		phoneme_list = []
		start_time = 0
		for word_info in json:
			if word_info["start"] != start_time:
				self._addPhoneme(phoneme_list, "m", start_time, word_info["start"])
			start_time = word_info["start"]
			for phoneme in word_info["phones"]:
				true_phoneme = phoneme2mouth[phoneme["phone"].split("_")[0]]
				if true_phoneme == "sil": true_phoneme = "m"
				duration = phoneme["duration"]
				if len(true_phoneme) == 2:
					self._addPhoneme(phoneme_list, true_phoneme[0], start_time, start_time + 0.5*duration)
					self._addPhoneme(phoneme_list, true_phoneme[1], start_time + 0.5*duration, start_time + duration)
				else:
					self._addPhoneme(phoneme_list, true_phoneme, start_time, start_time + duration)
				start_time += duration

		print(phoneme_list)
		return phoneme_list
	'''
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
	'''

	def _addMouthImage(self, image, phoneme):
		pillow_mouth = Image.open(f"{self.ART_PATHS['MOUTHS']}/{phoneme}.png")
		pillow_image = Image.fromarray(image)

		pillow_image.paste(pillow_mouth, (self.WIDTH//2, self.HEIGHT//2))

		cv2_mouthed_image = cv2.cvtColor(np.array(pillow_image), 1)  
		return cv2_mouthed_image

	def addMouth(self, image, frame_time):
		#audio_frame = int(frame_time * self.audio_FPS)
		
		if frame_time > self.phoneme_list[self.current_phoneme]['end_time']: 
			self.current_phoneme += 1
			if self.current_phoneme >= len(self.phoneme_list):
				self.current_phoneme = len(self.phoneme_list)-1

		phoneme = self.phoneme_list[self.current_phoneme]["phoneme"]
		return self._addMouthImage(image, phoneme)
