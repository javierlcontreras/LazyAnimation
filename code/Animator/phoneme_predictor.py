import requests
from pydub import AudioSegment
from configuration_constants import PHONEME_TO_MOUTH, TRACK_PATH_FILES, INPUT_AUDIO_TYPE
import json
from annotated_script_parser import AnnotatedScriptParser

EPS = 1e-5


class PhonemePredictor:
    def __init__(self, track_path, docker_url):
        self.track_path = track_path
        self.docker_url = docker_url

        self.word_list = []

    def _requestHTTPGentle(self):
        params = {
            'async': 'false',
        }

        files = {
            'audio': open(f'{self.track_path}{TRACK_PATH_FILES["AUDIO"]}', 'rb'),
            'transcript': open(f'{self.track_path}{TRACK_PATH_FILES["TRANSCRIPT"]}', 'rb'),
        }

        print("------ DEBUG INFO: Sent to gentle...")
        response = requests.post(self.docker_url, params=params, files=files)
        print("------ DEBUG INFO: Recieved from gentle")
        print(response.json()["words"])
        return response.json()["words"]

    def _addWord(self, word):
        self.word_list.append({
            "word": word,
            "phonemes": []
        })

    def _addPhoneme(self, phoneme, start_time, end_time):
        if start_time >= end_time:
            raise "Adding a phoneme with negative duration"
        true_phoneme = PHONEME_TO_MOUTH[phoneme.split("_")[0]]
        if true_phoneme == "sil": true_phoneme = "m"
        if len(true_phoneme) == 2:
            self.word_list[-1]["phonemes"].append({
                "phoneme": phoneme,
                "mouth": true_phoneme[0],
                "start_time": start_time,
                "end_time": 0.5 * (start_time + end_time)
            })
            self.word_list[-1]["phonemes"].append({
                "phoneme": phoneme,
                "mouth": true_phoneme[1],
                "start_time": 0.5 * (start_time + end_time),
                "end_time": end_time
            })
        else:
            self.word_list[-1]["phonemes"].append({
                "phoneme": phoneme,
                "mouth": true_phoneme,
                "start_time": start_time,
                "end_time": end_time
            })

    def _extractPhonemeTimetable(self, json):
        word_list = []
        start_time = 0
        for word_info in json:
            word = word_info["word"]
            if word_info["case"] == "not-found-in-audio":
                self._addWord(word)
                self._addPhoneme("not-found-in-audio", start_time, start_time + EPS)
            elif word_info["case"] == "success":
                if word_info["start"] > start_time + EPS:
                    self._addWord("<<spacing>>")
                    self._addPhoneme("sil", start_time, word_info["start"])
                self._addWord(word)
                start_time = word_info["start"]
                for phoneme in word_info["phones"]:
                    phone = phoneme["phone"]
                    duration = phoneme["duration"]
                    self._addPhoneme(phone, start_time, start_time + duration)
                    start_time += duration

        self._addWord("<<spacing>>")
        self._addPhoneme("sil", start_time, self._fullAudioDuration())

    def _fullAudioDuration(self):
        sound = AudioSegment.from_file(f"{self.track_path}{TRACK_PATH_FILES['AUDIO']}", INPUT_AUDIO_TYPE)
        duration = sound.duration_seconds
        return duration

    def _parseAnnotatedScript(self):
        annotated_script_parser = AnnotatedScriptParser(self.track_path)
        track_info = annotated_script_parser.parseAnnotatedScript()
        annotated_script_parser.unnanotateAndSaveScriptForGentle(track_info)
        return track_info

    def predictAndSavePhonemes(self):
        self._parseAnnotatedScript()

        gentle_json = self._requestHTTPGentle()
        self._extractPhonemeTimetable(gentle_json)

        out_file = open(f"{self.track_path}{TRACK_PATH_FILES['PHONEME_LIST']}", "w")
        json.dump(self.word_list, out_file, indent=1)
