from frame_modifier import *

class AnimationEngine:
	def __init__(self, track_path, ART_PATHS,
					FPS, WIDTH, HEIGHT):
		self.ART_PATHS = ART_PATHS
		self.FPS = FPS
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT

		self.frame_modifier = FrameModifier(track_path, self.ART_PATHS, self.WIDTH, self.HEIGHT)

	def addTrackLineToVideo(self, video, track_info_line, init_time):
		mood = track_info_line["mood"]
		delta_time = track_info_line["delta_time"]
		frames_of_track_line = int(delta_time * self.FPS + 0.5)

		try:
			background_path = glob.glob(f"{self.ART_PATHS['POSES']}/*")[0]
		except IndexError as e:
			print(f"Invalid mood {mood}, no images found")
			raise e
		background = cv2.imread(background_path)
		resized_background = self.frame_modifier.imageResize(background, self.WIDTH, self.HEIGHT)
		
		for frame_it in range(frames_of_track_line):
			frame_time = init_time + frame_it / self.FPS
			frame = self.frame_modifier.getFrame(resized_background, frame_time)
			video.write(frame)

		