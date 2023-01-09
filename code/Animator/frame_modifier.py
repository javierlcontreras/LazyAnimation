import cv2
from PIL import ImageFont, ImageDraw, Image
import glob
import numpy as np
from audio_to_mouth import *

class FrameModifier:
	def __init__(self, track_path, MOOD_IMG_PATH, WIDTH, HEIGHT):
		self.MOOD_IMG_PATH = MOOD_IMG_PATH
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT
		
		self.audio_to_mouth = AudioToMouth(track_path, WIDTH, HEIGHT)


	def getFrame(self, background, frame_time):
		frame_with_mouth = self.audio_to_mouth.addMouth(background, frame_time)			
		return frame_with_mouth

	def imageResize(self, img, W, H):
		(h, w, c) = np.shape(img)

		back = np.zeros((H, W, 3), dtype = "uint8")

		if w/W > h/H:
			swidth = W
			sheight = h*W/w
		else:
			sheight = H
			swidth = w*H/h
		
		sheight = int(sheight)
		swidth = int(swidth)
		img = cv2.resize(img, (swidth, sheight), interpolation = cv2.INTER_AREA)
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  
		
		pil_back = Image.fromarray(back)
		pil_img = Image.fromarray(img)
		dx = W/2 - swidth/2
		dy = H/2 - sheight/2
		dx = int(dx)
		dy = int(dy)
		pil_back.paste(pil_img, (dx, dy))

		img = cv2.cvtColor(np.array(pil_back), cv2.COLOR_RGB2BGR)  
		return img