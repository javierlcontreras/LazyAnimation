from frame_modifier import *

class AnimationEngine:
	def __init__(self, track_path, MOOD_IMG_PATH, 
					FPS, WIDTH, HEIGHT):
		self.MOOD_IMG_PATH = MOOD_IMG_PATH
		self.FPS = FPS
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT
		self.frame_modifier = FrameModifier(track_path, self.MOOD_IMG_PATH, self.WIDTH, self.HEIGHT)

	def addTrackLineToVideo(self, video, track_info_line, init_time):
		mood = track_info_line["mood"]
		delta_time = track_info_line["delta_time"]
		frames_of_track_line = int(delta_time * self.FPS + 0.5)

		background_path = glob.glob(f"{self.MOOD_IMG_PATH}/{mood}/*")[0]
		background = cv2.imread(background_path)
		resized_background = self.frame_modifier.imageResize(background, self.WIDTH, self.HEIGHT)
		
		for frame_it in range(frames_of_track_line):
			frame_time = init_time + frame_it / self.FPS
			frame = self.frame_modifier.getFrame(resized_background, frame_time)
			video.write(frame)

		