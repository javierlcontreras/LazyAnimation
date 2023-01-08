import cv2
import tqdm 
import glob
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import os


class VideoGenerator:
	def __init__(self, track_name, track_info, 
					MOOD_IMG_PATH,
					DATA_FILES_PATH,
					FPS = 60, WIDTH = 1920, HEIGHT = 1080): 
		self.track_name = track_name
		self.track_info = track_info
		self.FPS = FPS
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT
		self.MOOD_IMG_PATH = MOOD_IMG_PATH
		self.DATA_FILES_PATH = DATA_FILES_PATH
		self.track_audio_path = f"{self.DATA_FILES_PATH}/{track_name}.aac"
		self.output_video_path = f"{self.DATA_FILES_PATH}/{self.track_name}.mp4"
		self.output_video_audio_path = f"{self.DATA_FILES_PATH}/{self.track_name}_audio.mp4"

	def generateVideo(self):	
		fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
		video = cv2.VideoWriter(self.output_video_path, 
								fourcc, 
								self.FPS, 
								(self.WIDTH, self.HEIGHT))
		
		for track_info_line in tqdm.tqdm(self.track_info):
			text = track_info_line["text"]
			mood = track_info_line["mood"]
			delta_time = track_info_line["delta_time"]
			frames = int(delta_time * self.FPS)

			imgfile = glob.glob(f"{self.MOOD_IMG_PATH}/{mood}/*")[0]
			print(imgfile)
			img = cv2.imread(imgfile)
			img = self.imageResize(img, self.WIDTH, self.HEIGHT)			
			
			for i in range(frames):
				video.write(img)

		video.release()
		self.addMusic()

	def addMusic(self):
		os.system(f"ffmpeg -i {self.output_video_path} -i {self.track_audio_path} \
			-c copy -map 0:v -map 1:a -c:v copy -shortest -y {self.output_video_audio_path}")

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