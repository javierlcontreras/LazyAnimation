from annotated_script_parser import *
from animation_engine import *
from scheduler import *

import cv2
import tqdm
import glob
import os

from configuration_constants import TRACK_PATH_FILES, VIDEO_SETTINGS, ART_PATHS

class VideoGenerator:
    def __init__(self, track_path):
        self.track_path = track_path

        self.audio_track_path = f"{track_path}{TRACK_PATH_FILES['AUDIO']}"
        self.output_video_path = f"{track_path}{TRACK_PATH_FILES['VIDEO']}"
        self.output_video_audio_path = f"{track_path}{TRACK_PATH_FILES['VIDEO_WITH_AUDIO']}"

    def _computeSchedule(self):
        scheduler = Scheduler(self.track_path)
        schedule = scheduler.getSchedule()
        return schedule

    def generateAndSaveVideo(self):
        schedule = self._computeSchedule()

        animation_engine = AnimationEngine()

        FPS = VIDEO_SETTINGS['FPS']
        WIDTH = VIDEO_SETTINGS['WIDTH']
        HEIGHT = VIDEO_SETTINGS['HEIGHT']

        print(FPS, WIDTH, HEIGHT)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(self.output_video_path,
                                fourcc,
                                FPS,
                                (WIDTH, HEIGHT))
        for frame_it, frame_info in enumerate(tqdm.tqdm(schedule)):
            frame = animation_engine.getFrame(frame_info)
            (W, H) = frame.size
            if frame_it == 0:
                frame.show()
            if W != WIDTH or H != HEIGHT:
                raise "Receiving frame of inadequate size for video"
            cv2_frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            video.write(cv2_frame)

        video.release()
        self.addMusic()

    def addMusic(self):
        os.system(f"ffmpeg -i {self.output_video_path} -i {self.audio_track_path} \
			-c copy -map 0:v -map 1:a -c:v copy -shortest -y {self.output_video_audio_path}")
