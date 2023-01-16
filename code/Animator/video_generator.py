from annotated_script_parser import *
from animation_engine import *
from scheduler import *

import cv2
import tqdm 
import glob
import os


class VideoGenerator:
	def __init__(self, track_path, docker_url, ART_PATHS, VIDEO_SETTINGS, LAZYKH_IMAGE_INDEXING): 
		self.VIDEO_SETTINGS = VIDEO_SETTINGS
		self.track_path = track_path
		self.docker_url = docker_url
		self.ART_PATHS = ART_PATHS
		self.VIDEO_SETTINGS = VIDEO_SETTINGS
		self.LAZYKH_IMAGE_INDEXING = LAZYKH_IMAGE_INDEXING
		
		self.audio_track_path = f"{track_path}.aac"
		self.output_video_path = f"{track_path}.mp4"
		self.output_video_audio_path = f"{track_path}_audio.mp4"

	def _parseAnnotatedScript(self):
		annotated_script_parser = AnnotatedScriptParser(self.track_path)
		track_info = annotated_script_parser.parseAnnotatedScript()
		annotated_script_parser.unnanotateAndSaveScriptForGentle(track_info)
		return track_info

	def _computeSchedule(self, track_info):
		scheduler = Scheduler(self.audio_track_path, self.docker_url, track_info, self.LAZYKH_IMAGE_INDEXING)
		schedule = scheduler.getTimetables()
		return schedule

	def generateVideo(self):
		track_info = self._parseAnnotatedScript()
		schedule = self._computeSchedule(track_info)

		animation_engine = AnimationEngine(self.track_path, self.docker_url, schedule, self.ART_PATHS, self.VIDEO_SETTINGS, self.LAZYKH_IMAGE_INDEXING)

		FPS = self.VIDEO_SETTINGS['FPS']
		WIDTH = self.VIDEO_SETTINGS['WIDTH']
		HEIGHT = self.VIDEO_SETTINGS['HEIGHT']

		fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
		video = cv2.VideoWriter(self.output_video_path, 
								fourcc, 
								FPS, 
								(WIDTH, HEIGHT))
		init_time = 0
		for track_info_index, track_info_line in tqdm.tqdm(enumerate(track_info)):
			delta_time = schedule["TRACK_LINE_DURATIONS"][track_info_index]

			animation_engine.addTrackLineToVideo(video, track_info_line, init_time, delta_time)
			init_time += delta_time

		video.release()
		self.addMusic()

	def addMusic(self):
		os.system(f"ffmpeg -i {self.output_video_path} -i {self.audio_track_path} \
			-c copy -map 0:v -map 1:a -c:v copy -shortest -y {self.output_video_audio_path}")