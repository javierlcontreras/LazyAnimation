import cv2
import numpy as np
import array
from pydub import AudioSegment
from pydub.utils import get_array_type
from PIL import ImageFont, ImageDraw, Image

class AudioToMouth:
	def __init__(self, track_path, WIDTH, HEIGHT):
		self.AVERAGING_WINDOW_SECONDS = 0.1
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT
		self.audio_raw, self.audio_FPS, self.audio_max = self.extractAudioRaw(track_path)
		#print(self.audio_FPS)
	
	def extractAudioRaw(self, track_path):
		sound = AudioSegment.from_file(f"{track_path}.aac", "aac")
		#sound = sound.set_frame_rate(60)
		bit_depth = sound.sample_width * 8
		array_type = get_array_type(bit_depth)
		audio_raw_array = array.array(array_type, sound.raw_data)
		audio_raw = list(audio_raw_array)
		len_audio_raw = len(audio_raw)
		audio_raw_left = [audio_raw[i] for i in range(0, len_audio_raw, 2)]
		audio_FPS = sound.frame_rate
		audio_max = 0
		for audio_sample in audio_raw:
			audio_max = max(audio_max, abs(audio_sample))
		return audio_raw, audio_FPS, audio_max

	def getOpennessLevel(self, frame_time):
		start_time = frame_time - self.AVERAGING_WINDOW_SECONDS / 2
		end_time = frame_time + self.AVERAGING_WINDOW_SECONDS / 2
		len_audio_raw = len(self.audio_raw)
		start_frame = max(0, int(start_time * self.audio_FPS))
		end_frame = min(len_audio_raw, int(end_time * self.audio_FPS))
	
		count = 0
		audio_sample = 0
		for audio_frame in range(start_frame, end_frame):
			audio_sample += abs(self.audio_raw[audio_frame]) / self.audio_max
			count += 1
		return audio_sample / count


	def addMouth(self, image, frame_time):

		openness = self.getOpennessLevel(frame_time)
		mouthed_image = self.addCircleMouth(openness, image)

		return mouthed_image

	def addCircleMouth(self, openness, image):
		pillow_image = Image.fromarray(image)

		pillow_image_draw = ImageDraw.Draw(pillow_image)
		r = 300*openness
		w = self.WIDTH / 2
		h = self.HEIGHT / 2
		corners = [
			(w - r, h - r),
			(w + r, h + r)
		]
		pillow_image_draw.ellipse(corners, fill=(0,0,0,255))
		cv2_mouthed_image = cv2.cvtColor(np.array(pillow_image), cv2.COLOR_RGB2BGR)  
		return cv2_mouthed_image
