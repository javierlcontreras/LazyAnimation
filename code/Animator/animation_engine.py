from frame_modifier import *
import random
import tqdm

class AnimationEngine:
	def __init__(self, track_path, docker_url, schedule, ART_PATHS, VIDEO_SETTINGS, LAZYKH_IMAGE_INDEXING):
		self.ART_PATHS = ART_PATHS
		self.VIDEO_SETTINGS = VIDEO_SETTINGS
		self.LAZYKH_IMAGE_INDEXING = LAZYKH_IMAGE_INDEXING

		self.docker_url = docker_url
		self.frame_modifier = FrameModifier(track_path, docker_url, schedule, ART_PATHS, LAZYKH_IMAGE_INDEXING)

	def _emotionToImagePath(self, mood, pose, blinker):
		index = (5*self.LAZYKH_IMAGE_INDEXING["EMOTION_INDEX"][mood] + pose)*3 + blinker
		try:
			path = glob.glob(f"{self.ART_PATHS['POSES']}/pose" + "{:04d}".format(index + 1) + ".png")[0]
		except IndexError as e:
			print(f"Invalid mood {mood}, no images found")
			raise e
		return path
			

	def addTrackLineToVideo(self, video, track_info_line, init_time, delta_time):
		FPS = self.VIDEO_SETTINGS['FPS']
		WIDTH = self.VIDEO_SETTINGS['WIDTH']
		HEIGHT = self.VIDEO_SETTINGS['HEIGHT']
		BLINKING_ACTION_TIME = self.VIDEO_SETTINGS['BLINKING_ACTION_TIME']
		BLINKING_SPACE_TIME = self.VIDEO_SETTINGS['BLINKING_SPACE_TIME']
		
		mood = track_info_line["mood"]
		frames_of_track_line = int(delta_time * FPS + 0.5)
		
		inter_blink_frames = int(BLINKING_SPACE_TIME * FPS)
		blinking_frames = int(BLINKING_ACTION_TIME/2 * FPS)

		time_to_blink = inter_blink_frames
		time_since_blink = 1e9
		blinker = 0
		
		pose = random.randint(0,5)
		for frame_it in tqdm.tqdm(range(frames_of_track_line)):
			time_since_blink += 1
			time_to_blink -= 1
		
			if time_to_blink == 0:
				blinker = 1
				time_since_blink = 0
			if time_since_blink == blinking_frames:
				blinker = 2
			if time_since_blink == 2*blinking_frames:
				blinker = 0
				time_to_blink = inter_blink_frames

			pose_path = self._emotionToImagePath(mood, pose, blinker) 
			pose_image = Image.open(pose_path)
			frame_image = self.frame_modifier.imageResize(pose_image, WIDTH, HEIGHT)
			
			frame_time = init_time + frame_it / FPS
			frame = self.frame_modifier.getFrame(pose_image, frame_time, mood)
			if random.randint(0, 200) == 0: 
				frame.show()
			
			cv2_frame= cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)  
			video.write(cv2_frame)

		