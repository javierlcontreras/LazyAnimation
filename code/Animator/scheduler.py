import requests
from pydub import AudioSegment

EPS = 1e-5
class Scheduler:
	def __init__(self, track_path, docker_url, track_info, VIDEO_SETTINGS, LAZYKH_IMAGE_INDEXING):
		self.track_path = track_path
		self.docker_url = docker_url

		self.track_info = track_info

		self.VIDEO_SETTINGS = VIDEO_SETTINGS
		self.LAZYKH_IMAGE_INDEXING = LAZYKH_IMAGE_INDEXING

	def _requestHTTPGentle(self):
		params = {
		    'async': 'false',
		}

		files = {
		    'audio': open(f'{self.track_path}.aac', 'rb'),
		    'transcript': open(f'{self.track_path}_gentle.txt', 'rb'),
		}

		response = requests.post(self.docker_url, params=params, files=files)
		
		return response.json()["words"]

	def _addPhoneme(self, phoneme_list, phoneme, start_time, end_time):
		if start_time >= end_time:
			raise "Adding a phoneme with negative duration"
		phoneme_list.append({
			"phoneme": phoneme,
			"start_time":start_time,
			"end_time":end_time
		})

	def _extractPhonemeTimetable(self, json):
		phoneme_list = []
		start_time = 0
		for word_info in json:
			if word_info["start"] > start_time + EPS:
				self._addPhoneme(phoneme_list, "m", start_time, word_info["start"])
			start_time = word_info["start"]
			for phoneme in word_info["phones"]:
				true_phoneme = self.LAZYKH_IMAGE_INDEXING["PHONEME_TO_MOUTH"][phoneme["phone"].split("_")[0]]
				if true_phoneme == "sil": true_phoneme = "m"
				duration = phoneme["duration"]
				if len(true_phoneme) == 2:
					self._addPhoneme(phoneme_list, true_phoneme[0], start_time, start_time + 0.5*duration)
					self._addPhoneme(phoneme_list, true_phoneme[1], start_time + 0.5*duration, start_time + duration)
				else:
					self._addPhoneme(phoneme_list, true_phoneme, start_time, start_time + duration)
				start_time += duration
		
		self._addPhoneme(phoneme_list, "m", start_time, self._fullAudioDuration())

		return phoneme_list

	def _fullAudioDuration(self):
		sound = AudioSegment.from_file(f"{self.track_path}.aac", "aac")
		duration = sound.duration_seconds
		return duration

	def _extractTrackLineDuration(self, json):
		durations = []
		json_index = 0
		last_duration = 0
		for track_line in self.track_info[:-1]:
			last_word = track_line["text"].strip(" ").split(" ")[-1].strip(" ,.;:?¿¡!").lower()
			
			while json[json_index]["alignedWord"] != last_word: 
				json_index += 1

			durations.append(json[json_index]["end"] - last_duration)

			last_duration = json[json_index]["end"]

		full_audio_duration = self._fullAudioDuration()
		durations.append(full_audio_duration - last_duration)

		return durations

	def _newFrame(self, track_line, phoneme):
		return {
			"phoneme": phoneme,
			"mood": track_line["mood"],
			"pose": 0,
			"blinker": 0
		}

	def _frameBriefing(self, phoneme_list, track_durations):
		print(phoneme_list)
		print(track_durations)

		FPS = self.VIDEO_SETTINGS["FPS"]
		total_frames = int(FPS * self._fullAudioDuration())
		frame_info = []
		phoneme_it = 0
		track_it = 0
		current_duration = track_durations[0]
		for frame_it in range(total_frames):
			frame_time = frame_it / FPS
			if frame_time >= phoneme_list[phoneme_it]["end_time"]: 
				phoneme_it += 1
			if frame_time >= current_duration: 
				track_it += 1 
				current_duration += track_durations[track_it]

			if phoneme_it >= len(phoneme_list):
				print("phoneme_it", phoneme_it)
				import pdb; pdb.set_trace()
			
			if track_it >= len(track_durations):
				print("track_it ", track_it)
			frame_info.append(self._newFrame(self.track_info[track_it], phoneme_list[phoneme_it]["phoneme"]))
		return frame_info

	def getTimetables(self):
		gentle_json = self._requestHTTPGentle()
		phoneme_list = self._extractPhonemeTimetable(gentle_json)
		track_durations = self._extractTrackLineDuration(gentle_json)

		schedule = self._frameBriefing(phoneme_list, track_durations)
		return schedule