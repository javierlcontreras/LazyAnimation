from annotated_script_parser import *
from animation_engine import *
import cv2
import tqdm 
import glob
import os


class VideoGenerator:
	def __init__(self, track_path, MOOD_IMG_PATH,
					FPS = 60, WIDTH = 1920, HEIGHT = 1080): 
		self.FPS = FPS
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT
		self.MOOD_IMG_PATH = MOOD_IMG_PATH

		self.track_path = track_path
		annotated_script_parser = AnnotatedScriptParser(self.track_path)
		self.track_info = annotated_script_parser.parseAnnotatedScript()
		
		self.animation_engine = AnimationEngine(track_path, MOOD_IMG_PATH, FPS, WIDTH, HEIGHT)

		self.track_audio_path = f"{track_path}.aac"
		self.output_video_path = f"{track_path}.mp4"
		self.output_video_audio_path = f"{track_path}_audio.mp4"

	def generateVideo(self):	
		fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
		video = cv2.VideoWriter(self.output_video_path, 
								fourcc, 
								self.FPS, 
								(self.WIDTH, self.HEIGHT))
		
		init_time = 0
		for track_info_line in tqdm.tqdm(self.track_info):

			self.animation_engine.addTrackLineToVideo(video, track_info_line, init_time)

			init_time += track_info_line["delta_time"]

		video.release()
		self.addMusic()

	def addMusic(self):
		os.system(f"ffmpeg -i {self.output_video_path} -i {self.track_audio_path} \
			-c copy -map 0:v -map 1:a -c:v copy -shortest -y {self.output_video_audio_path}")