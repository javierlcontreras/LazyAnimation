class VideoGenerator:
	def __init__(self, track_name, track_info, track_audio = None):
		self.track_name = track_name
		self.track_info = track_info
		self.track_audio = track_audio

	def generateVideo(self):
		print(self.track_info)