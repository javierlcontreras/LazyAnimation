import cv2
import os
import numpy as np
import array

from pydub import AudioSegment
from pydub.utils import get_array_type
from PIL import ImageFont, ImageDraw, Image

import requests

class AudioToMouth:
	def __init__(self, ART_PATHS, LAZYKH_IMAGE_INDEXING):
		self.ART_PATHS = ART_PATHS
		self.LAZYKH_IMAGE_INDEXING = LAZYKH_IMAGE_INDEXING	

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

	def addMouth(self, image, frame_info):
		phoneme = frame_info["phoneme"]
		mood = frame_info["mood"]
		return self._addMouthImage(image, mood, phoneme)
