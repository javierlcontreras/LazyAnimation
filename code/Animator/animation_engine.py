from frame_modifier import *

emotions = {}
emotions["explain"] = 0
emotions["happy"] = 1
emotions["sad"] = 2
emotions["angry"] = 3
emotions["confused"] = 4
emotions["rq"] = 5

class AnimationEngine:
	def __init__(self, track_path, docker_url, ART_PATHS,
					FPS, WIDTH, HEIGHT):
		self.ART_PATHS = ART_PATHS
		self.FPS = FPS
		self.WIDTH = WIDTH
		self.HEIGHT = HEIGHT

		self.docker_url = docker_url
		self.frame_modifier = FrameModifier(track_path, docker_url, self.ART_PATHS)

	def addTrackLineToVideo(self, video, track_info_line, init_time):
		mood = track_info_line["mood"]
		delta_time = track_info_line["delta_time"]
		frames_of_track_line = int(delta_time * self.FPS + 0.5)
		
		frames_in_a_blink = int(2 * self.FPS)
		blink_speed = int(0.05 * self.FPS)
		time_to_blink = frames_in_a_blink
		time_since_blink = 100

		blinker = 0
		for frame_it in range(frames_of_track_line):
			time_since_blink += 1
			time_to_blink -= 1
			if time_to_blink == 0:
				blinker = 1
				time_since_blink = 0
			if time_since_blink == blink_speed:
				blinker = 2
			if time_since_blink == 2*blink_speed:
				blinker = 0
				time_to_blink = frames_in_a_blink

			try:
				poseIndexBlinker = emotions[mood]*3 + blinker
				background_path = glob.glob(f"{self.ART_PATHS['POSES']}/pose" + "{:04d}".format(poseIndexBlinker+1) + ".png")[0]
			except IndexError as e:
				print(f"Invalid mood {mood}, no images found")
				raise e
			background = Image.open(background_path)
			mood_pose = self.frame_modifier.imageResize(background, self.WIDTH, self.HEIGHT)
			
			frame_time = init_time + frame_it / self.FPS
			frame = self.frame_modifier.getFrame(mood_pose, frame_time)
			cv2_frame= cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)  
			video.write(cv2_frame)

		