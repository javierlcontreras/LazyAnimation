import requests
from pydub import AudioSegment
import random

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

		print("------ DEBUG INFO: Sent to gentle...")
		response = requests.post(self.docker_url, params=params, files=files)
		print("------ DEBUG INFO: Recieved from gentle")
		print(response.json()["words"])
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
			if not "start" in word_info: continue
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
			
			while json_index < len(json) and \
				(not "alignedWord" in json[json_index] or \
					json[json_index]["alignedWord"] != last_word): 
				json_index += 1

			if json_index < len(json):
				durations.append(json[json_index]["end"] - last_duration)
				last_duration = json[json_index]["end"]

		full_audio_duration = self._fullAudioDuration()
		durations.append(full_audio_duration - last_duration)

		return durations

	def _newFrame(self, track_line, phoneme, blinker, pose):
		return {
			"phoneme": phoneme,
			"mood": track_line["mood"],
			"pose": pose,
			"blinker": blinker
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

		blinking_space_frames = int(self.VIDEO_SETTINGS["BLINKING_SPACE_TIME"] * FPS)
		blinking_action_frames = int(self.VIDEO_SETTINGS["BLINKING_ACTION_TIME"] * FPS)

		frames_to_blink = blinking_space_frames
		blinking_stage = 1e9
		blinker = 0

		pose_frames = int(self.VIDEO_SETTINGS["POSE_TIME"] * FPS)
		frames_to_pose = pose_frames
		pose = 0
		for frame_it in range(total_frames):
			## POSINF
			frames_to_pose -= 1
			if frames_to_pose == 0:
				pose = (pose+1)%3

			### BLINKING
			frames_to_blink -= 1
			blinking_stage += 1
			if frames_to_blink == 0:
				blinking_stage = 0
				blinker = 1
			if blinking_stage == blinking_action_frames:
				blinker = 2
			if blinking_stage == 2*blinking_action_frames:
				blinker = 0
				frames_to_blink = blinking_space_frames
			### /BLINKING

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
			frame_info.append(self._newFrame(self.track_info[track_it], phoneme_list[phoneme_it]["phoneme"], blinker, pose))
		return frame_info

	def getTimetables(self):
		gentle_json = self._requestHTTPGentle()
		phoneme_list = self._extractPhonemeTimetable(gentle_json)
		track_durations = self._extractTrackLineDuration(gentle_json)

		schedule = self._frameBriefing(phoneme_list, track_durations)
		print("--- DEBUG INFO: full schedule")
		for line in schedule:
			print(line)
		return schedule