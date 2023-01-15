import cv2
from PIL import ImageFont, ImageDraw, Image
import glob
import numpy as np
from audio_to_mouth import *

class FrameModifier:
	def __init__(self, track_path, docker_url, ART_PATHS):
		self.ART_PATHS = ART_PATHS

		self.docker_url = docker_url
		self.audio_to_mouth = AudioToMouth(track_path, docker_url, ART_PATHS)

	def getFrame(self, current_frame, frame_time):
		frame_with_mouth = self.audio_to_mouth.addMouth(current_frame, frame_time)			
		return frame_with_mouth

	def _writeTextOnImage(self, img, word, W, H):
		fontsize = 200

		draw = ImageDraw.Draw(img)  
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

		return img

	def imageResize(self, img, W, H):
		h, w = img.size

		back = np.zeros((H, W, 3), dtype = "uint8")

		if w/W > h/H:
			swidth = W
			sheight = h*W/w
		else:
			sheight = H
			swidth = w*H/h
		
		sheight = int(sheight)
		swidth = int(swidth)
		img = img.resize((swidth, sheight))
		
		pil_back = Image.new("RGBA", (W,H))
		dx = W//2 - swidth//2
		dy = H//2 - sheight//2
		pil_back.paste(img, (dx, dy), mask=img)
		
		return pil_back