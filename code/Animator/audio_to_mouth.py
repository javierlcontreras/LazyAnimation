import cv2
import os
import numpy as np
import array

from pydub import AudioSegment
from pydub.utils import get_array_type
from PIL import ImageFont, ImageDraw, Image

import requests

class AudioToMouth:
	def __init__(self, track_path, docker_url, schedule, ART_PATHS, LAZYKH_IMAGE_INDEXING):
		self.ART_PATHS = ART_PATHS
		
		self.docker_url = docker_url
		self.LAZYKH_IMAGE_INDEXING = LAZYKH_IMAGE_INDEXING

		self.phoneme_list = schedule["PHONEMES"]
		self.current_phoneme = 0
	

	def _phonemeToMouthImagePath(self, phoneme, mood):
		index = self.LAZYKH_IMAGE_INDEXING["MOUTH_TO_INDEX"][phoneme]
		if self.LAZYKH_IMAGE_INDEXING['EMOTION_POSITIVITY'][mood]:
			index += 11
		return Image.open(f"{self.ART_PATHS['MOUTHS']}/mouth" + "{:04d}".format(index + 1) + ".png")

	def _addMouthImage(self, image, mood, phoneme):
		pillow_mouth = self._phonemeToMouthImagePath(phoneme, mood).convert('RGBA')
		pillow_empty = Image.new("RGBA",image.size)
		(w, h) = pillow_mouth.size
		pillow_mouth = pillow_mouth.resize((w//3, h//3))
		(W, H) = image.size
		position = (int(W/2 - (2*47+1)*w/128), int(H/2 - 26*h/32))
		pillow_empty.paste(pillow_mouth, position,mask=pillow_mouth)
		image = Image.alpha_composite(image, pillow_empty)

		return image

	def addMouth(self, image, frame_time, mood):
		#audio_frame = int(frame_time * self.audio_FPS)
		
		if frame_time > self.phoneme_list[self.current_phoneme]['end_time']: 
			self.current_phoneme += 1
			if self.current_phoneme >= len(self.phoneme_list):
				self.current_phoneme = len(self.phoneme_list)-1

		phoneme = self.phoneme_list[self.current_phoneme]["phoneme"]
		return self._addMouthImage(image, mood, phoneme)
