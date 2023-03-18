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

        frame_folder = f"{self.track_path}/{TRACK_PATH_FILES['FRAMES']}"
        if not os.path.exists(frame_folder):
            os.mkdir(frame_folder)

        for frame_it, frame_info in enumerate(tqdm.tqdm(schedule)):
            frame_file = f"{frame_folder}/frame-{frame_it:06d}.png"
            print(frame_file)
            if os.path.exists(frame_file):
                continue
            frame = animation_engine.getFrame(frame_info)
            (W, H) = frame.size
            if frame_it == 0:
                frame.show()
            if W != WIDTH or H != HEIGHT:
                raise "Receiving frame of inadequate size for video"
            frame.save(frame_file, "png")

        self.createVideo()

    def createVideo(self):
        os.system(f"ffmpeg -framerate {VIDEO_SETTINGS['FPS']} \
                    -pattern_type glob -i '{self.track_path}/{TRACK_PATH_FILES['FRAMES']}/*.png' \
                    -i {self.track_path}/{TRACK_PATH_FILES['AUDIO']} \
                    -c:v png -pix_fmt +rgba {self.track_path}/{TRACK_PATH_FILES['VIDEO']} -y")
