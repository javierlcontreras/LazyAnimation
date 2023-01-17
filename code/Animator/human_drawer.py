import cv2
import os
import numpy as np
import array

from pydub import AudioSegment
from pydub.utils import get_array_type
from PIL import ImageFont, ImageDraw, Image

import requests

class HumanDrawer:
	def __init__(self, ART_PATHS, LAZYKH_IMAGE_INDEXING):
		self.ART_PATHS = ART_PATHS
		self.LAZYKH_IMAGE_INDEXING = LAZYKH_IMAGE_INDEXING	

	def _blinkerToEyePath(self, blinker):
		return Image.open(f"{self.ART_PATHS['EYES']}/eyes{blinker+1}.png")
	
	def _phonemeToMouthImagePath(self, phoneme, mood):
		#index = self.LAZYKH_IMAGE_INDEXING["MOUTH_TO_INDEX"][phoneme]
		#if self.LAZYKH_IMAGE_INDEXING['EMOTION_POSITIVITY'][mood]:
		#	index += 11
		return Image.open(f"{self.ART_PATHS['MOUTHS']}/{phoneme}.png")#"mouth" + "{:04d}".format(index + 1) + ".png")

	def _addImage(self, image, added_image):
		pillow_empty = Image.new("RGBA",image.size)
		(w, h) = added_image.size
		(W, H) = image.size
		position = (int(W/2 - w/2), int(H/2 - h/2))
		pillow_empty.paste(added_image, position,mask=added_image)
		image = Image.alpha_composite(image, pillow_empty)

		return image

	def addMouth(self, image, frame_info):
		phoneme = frame_info["phoneme"]
		mood = frame_info["mood"]
		pillow_mouth = self._phonemeToMouthImagePath(phoneme, mood).convert('RGBA')

		return self._addImage(image, pillow_mouth)
	
	def addEyes(self, image, frame_info):
		blinker = frame_info["blinker"]
		pillow_eyes = self._blinkerToEyePath(blinker).convert('RGBA')
		return self._addImage(image, pillow_eyes)

