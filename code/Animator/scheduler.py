import json
from configuration_constants import VIDEO_SETTINGS, TRACK_PATH_FILES
from annotated_script_parser import AnnotatedScriptParser


class Scheduler:
    def __init__(self, track_path):
        self.track_path = track_path

    def _fullAudioDuration(self, gentle_json):
        return gentle_json[-1]["phonemes"][-1]["end_time"]

    def _injectTrackLineDuration(self, track_info, gentle_json):
        word_index = 0
        last_duration = 0
        for track_line_it in range(len(track_info) - 1):
            track_line = track_info[track_line_it]
            last_word = track_line["text"].strip(" ").split(" ")[-1].strip(" ,.;:?¿¡!").lower()

            while word_index < len(gentle_json) and \
                    ("word" not in gentle_json[word_index] or gentle_json[word_index]["word"].lower() != last_word):
                word_index += 1

            if word_index < len(gentle_json):
                end_word_time = gentle_json[word_index]["phonemes"][-1]["end_time"]
                track_info[track_line_it]["duration"] = end_word_time - last_duration
                last_duration = end_word_time

        full_audio_duration = self._fullAudioDuration(gentle_json)
        track_info[-1]["duration"] = full_audio_duration - last_duration

    def _initFrames(self, audio_duration):
        FPS = VIDEO_SETTINGS["FPS"]
        total_frames = int(FPS * audio_duration)
        frames = [
            {
                "number": frame_num,
                "time": frame_num * audio_duration / total_frames,
                "mouth": "m",
                "hands": "down",
                "eyebrows": "happy",
                "eyes": "open"
            }
            for frame_num in range(total_frames)
        ]
        return frames

    def _injectBlinking(self, frames):
        FPS = VIDEO_SETTINGS["FPS"]
        blinking_space_frames = int(VIDEO_SETTINGS["BLINKING_SPACE_TIME"] * FPS)
        blinking_action_frames = int(VIDEO_SETTINGS["BLINKING_ACTION_TIME"] * FPS)

        frames_to_blink = blinking_space_frames
        blinking_stage = 1e9
        blinker = "open"

        for frame in frames:
            frames_to_blink -= 1
            blinking_stage += 1
            if frames_to_blink == 0:
                blinking_stage = 0
                blinker = "mid"
            if blinking_stage == blinking_action_frames:
                blinker = "closed"
            if blinking_stage == 2 * blinking_action_frames:
                blinker = "open"
                frames_to_blink = blinking_space_frames

            frame["eyes"] = blinker

    def _injectPoseAndMood(self, frames, track_info):
        FPS = VIDEO_SETTINGS["FPS"]

        track_it = 0
        current_duration = track_info[0]["duration"]
        for frame_it, frame in enumerate(frames):
            frame_time = frame_it / FPS
            if frame_time >= current_duration:
                track_it += 1
                current_duration += track_info[track_it]["duration"]

            frame["hands"] = track_info[track_it]["hands"]
            frame["eyebrows"] = track_info[track_it]["eyebrows"]

    def _injectPhonemes(self, frames, gentle_json):
        FPS = VIDEO_SETTINGS["FPS"]

        word_it = 0
        phoneme_it = 0
        for frame_it, frame in enumerate(frames):
            frame_time = frame_it / FPS
            if word_it > len(gentle_json): break

            while frame_time >= gentle_json[word_it]["phonemes"][phoneme_it]["end_time"]:
                phoneme_it += 1
                if phoneme_it >= len(gentle_json[word_it]["phonemes"]):
                    phoneme_it = 0
                    word_it += 1

            frame["mouth"] = gentle_json[word_it]["phonemes"][phoneme_it]["mouth"]

    def _cleanUpInput(self):
        script_parser = AnnotatedScriptParser(self.track_path)
        track_info = script_parser.parseAnnotatedScript()
        gentle_json = json.load(open(f"{self.track_path}/{TRACK_PATH_FILES['PHONEMES_REVIEWED']}"))
        self._injectTrackLineDuration(track_info, gentle_json)
        print(track_info)
        return gentle_json, track_info, self._fullAudioDuration(gentle_json)

    def getSchedule(self):
        gentle_json, track_info, audio_duration = self._cleanUpInput()

        frames = self._initFrames(audio_duration)
        self._injectBlinking(frames)
        self._injectPoseAndMood(frames, track_info)
        self._injectPhonemes(frames, gentle_json)

        return frames
