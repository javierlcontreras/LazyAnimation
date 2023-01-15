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
	def __init__(self, track_path, docker_url, ART_PATHS):
		self.AVERAGING_WINDOW_SECONDS = 0.3
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

	def _addMouthImage(self, image, phoneme):
		pillow_mouth = Image.open(f"{self.ART_PATHS['MOUTHS']}/{phoneme}.png").convert('RGBA')
		pillow_empty = Image.new("RGBA",image.size)
		(W, H) = image.size
		(w, h) = pillow_mouth.size
		position = (W//2 - w//2, H//2 - h//2)
		pillow_empty.paste(pillow_mouth, position,mask=pillow_mouth)
		image = Image.alpha_composite(image, pillow_empty)

		return image

	def addMouth(self, image, frame_time):
		#audio_frame = int(frame_time * self.audio_FPS)
		
		if frame_time > self.phoneme_list[self.current_phoneme]['end_time']: 
			self.current_phoneme += 1
			if self.current_phoneme >= len(self.phoneme_list):
				self.current_phoneme = len(self.phoneme_list)-1

		phoneme = self.phoneme_list[self.current_phoneme]["phoneme"]
		return self._addMouthImage(image, phoneme)
