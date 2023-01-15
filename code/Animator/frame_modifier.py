import cv2
from PIL import ImageFont, ImageDraw, Image
import glob
import numpy as np
from audio_to_mouth import *

class FrameModifier:
	def __init__(self, track_path, docker_url, ART_PATHS, WIDTH, HEIGHT):
		self.ART_PATHS = ART_PATHS
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT

		self.docker_url = docker_url
		self.audio_to_mouth = AudioToMouth(track_path, docker_url, ART_PATHS, WIDTH, HEIGHT)

	def getFrame(self, background, frame_time):
		frame_with_mouth = self.audio_to_mouth.addMouth(background, frame_time)			
		return frame_with_mouth

	def _writeTextOnImage(self, img, word, W, H):
		fontsize = 200

		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  
		pil_im = Image.fromarray(img)
		draw = ImageDraw.Draw(pil_im)  
		color = (0,0,0)
		
		while True:
			font = ImageFont.truetype(f"{self.ART_PATHS['FONTS']}/SODORBld.ttf", fontsize)	

			x1, y1, x2, y2 = draw.textbbox((0,0), word, font=font)
			w = x2 - x1
			h = y2 - y1
			if w > 0.7*W or h > 0.7*H: fontsize -= 1
			else:
				break

		draw.text(((W-w)/2,(H-h)/2), word.replace("-", " "), font=font, fill="white", stroke_width=fontsize//10, stroke_fill="black")

		img = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)  

		return img

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