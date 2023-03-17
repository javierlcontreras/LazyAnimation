from human_drawer import *
import random
import tqdm
import glob 

from PIL import ImageFont, ImageDraw, Image

class AnimationEngine:
	def __init__(self, ART_PATHS, VIDEO_SETTINGS, LAZYKH_IMAGE_INDEXING):
		self.ART_PATHS = ART_PATHS
		self.VIDEO_SETTINGS = VIDEO_SETTINGS
		self.LAZYKH_IMAGE_INDEXING = LAZYKH_IMAGE_INDEXING

		self.human_drawer = HumanDrawer(ART_PATHS, LAZYKH_IMAGE_INDEXING)

	def _emotionToImagePath(self, mood, pose, blinker):
		#index = (5*self.LAZYKH_IMAGE_INDEXING["EMOTION_INDEX"][mood] + pose)*3 + blinker
		try:
			path = glob.glob(f"{self.ART_PATHS['POSES']}/{mood}*")[0]# + "{:04d}".format(index + 1) + ".png")[0]
		except IndexError as e:
			print(f"Invalid mood {mood}, no images found")
			raise e
		return path
			

	def getFrame(self, frame_info):
		pose_path = self._emotionToImagePath(frame_info["mood"], frame_info["pose"], frame_info["blinker"]) 
		pose_image = Image.open(pose_path)

		frame_with_mouth = self.human_drawer.addMouth(pose_image, frame_info)
		frame_with_eyes = self.human_drawer.addEyes(frame_with_mouth, frame_info)
		WIDTH = self.VIDEO_SETTINGS["WIDTH"]		
		HEIGHT = self.VIDEO_SETTINGS["HEIGHT"]		
		frame_resized = self._imageResize(frame_with_eyes, WIDTH, HEIGHT)
		return frame_resized

	def _writeTextOnImage(self, img, word):
		(W, H) = img.size
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

	def _imageResize(self, img, W, H):
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
		img = img.resize((swidth, sheight), resample=Image.Resampling.NEAREST)
		
		pil_back = Image.new("RGBA", (W,H))
		dx = W//2 - swidth//2
		dy = H//2 - sheight//2
		pil_back.paste(img, (dx, dy), mask=img)
		
		return pil_back
		
