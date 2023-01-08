from annotated_script_parser import *
from frame_modifier import *
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
		self.frame_modifier = FrameModifier(self.MOOD_IMG_PATH, self.WIDTH, self.HEIGHT)

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
			mood = track_info_line["mood"]
			delta_time = track_info_line["delta_time"]
			frames_of_track_line = int(delta_time * self.FPS + 0.5)

			for frame_it in range(frames_of_track_line):
				frame_time = init_time + frame_it / self.FPS
				frame = self.frame_modifier.getFrame(mood, init_time, delta_time, frame_time)
				video.write(frame)

			init_time += delta_time

		video.release()
		self.addMusic()

	def addMusic(self):
		os.system(f"ffmpeg -i {self.output_video_path} -i {self.track_audio_path} \
			-c copy -map 0:v -map 1:a -c:v copy -shortest -y {self.output_video_audio_path}")