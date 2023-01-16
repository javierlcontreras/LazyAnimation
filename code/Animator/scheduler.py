import requests
from pydub import AudioSegment

class Scheduler:
	def __init__(self, audio_track_path, docker_url, track_info, LAZYKH_IMAGE_INDEXING):
		self.audio_track_path = audio_track_path
		self.docker_url = docker_url
		self.track_info = track_info
		self.LAZYKH_IMAGE_INDEXING = LAZYKH_IMAGE_INDEXING

	def _requestHTTPGentle(self):
		params = {
		    'async': 'false',
		}

		files = {
		    'audio': open('video_files/example.aac', 'rb'),
		    'transcript': open('video_files/example_gentle.txt', 'rb'),
		}

		response = requests.post(self.docker_url, params=params, files=files)
		
		return response.json()["words"]

	def _addPhoneme(self, phoneme_list, phoneme, start_time, end_time):
		phoneme_list.append({
			"phoneme": phoneme,
			"start_time":start_time,
			"end_time":end_time
		})

	def _extractPhonemeTimetable(self, json):
		phoneme_list = []
		start_time = 0
		for word_info in json:
			if word_info["start"] != start_time:
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

		return phoneme_list

	def _fullAudioDuration(self):
		sound = AudioSegment.from_file(f"{self.audio_track_path}", "aac")
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

	def getTimetables(self):
		gentle_json = self._requestHTTPGentle()

		schedule = {
			'PHONEMES': self._extractPhonemeTimetable(gentle_json),
			"TRACK_LINE_DURATIONS": self._extractTrackLineDuration(gentle_json)
		}

		return schedule