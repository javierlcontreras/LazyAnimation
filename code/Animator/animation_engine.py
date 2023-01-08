from frame_modifier import *

class AnimationEngine:
	def __init__(self, MOOD_IMG_PATH, 
					FPS, WIDTH, HEIGHT):
		self.MOOD_IMG_PATH = MOOD_IMG_PATH
		self.FPS = FPS
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT
		self.frame_modifier = FrameModifier(self.MOOD_IMG_PATH, self.WIDTH, self.HEIGHT)

	def addTrackLineToVideo(self, video, track_info_line, init_time):
		mood = track_info_line["mood"]
		delta_time = track_info_line["delta_time"]
		frames_of_track_line = int(delta_time * self.FPS + 0.5)

		for frame_it in range(frames_of_track_line):
			frame_time = init_time + frame_it / self.FPS
			frame = self.frame_modifier.getFrame(mood, init_time, delta_time, frame_time)
			video.write(frame)
