import argparse
import os
from video_generator import *
from phoneme_predictor import *
import requests
from configuration_constants import TO_GENTLE_MODE, TO_VIDEO_MODE, VALID_EXECUTION_MODES

def parseTrackPathFromArguments():
    parser = argparse.ArgumentParser(description='Annotated text to Animation')
    parser.add_argument('--track_path',
                        dest='track_path',
                        type=str,
                        help='Path of the track without file extensions',
                        required=True)
    parser.add_argument('--execution_mode',
                        dest="execution_mode",
                        type=str,
                        help='Part of the pipeline you want to execute',
                        required=True)
    parser.add_argument('--docker_port',
                        type=int,
                        help='Real machine port of Gentle docker service')

    args = parser.parse_args()
    execution_mode = args.execution_mode
    track_path = args.track_path
    

    if execution_mode not in VALID_EXECUTION_MODES:
        raise "Invalid Execution mode"
    if not os.path.exists(f"{track_path}/{TRACK_PATH_FILES['ANNOTATED_TRANSCRIPT']}"):
        raise "Annotated transcript doesn't exist"
    if not os.path.exists(f"{track_path}/{TRACK_PATH_FILES['AUDIO']}"):
        raise "Audio doesn't exist"
    
    if execution_mode == TO_GENTLE_MODE:
        docker_port = args.docker_port
        docker_url = f"http://0.0.0.0:{docker_port}/transcriptions"
        try:
            head = requests.get(docker_url)
        except ConnectionRefusedError as e:
            raise "docker_port is not responding to HTTP requests"
        except requests.exceptions.InvalidURL as e:
            raise "Invalid docker port"
        
        return {"execution_mode": execution_mode, "track_path": track_path, "docker_url": docker_url}
    elif execution_mode == TO_VIDEO_MODE:
        return {"execution_mode": execution_mode, "track_path": track_path}


def main():
    arguments = parseTrackPathFromArguments()
    execution_mode = arguments['execution_mode']
    track_path = arguments['track_path']
    print(f"Starting animator on mode: {execution_mode} on track: {track_path}")
    
    if execution_mode == TO_GENTLE_MODE:
        docker_url = arguments["docker_url"]
        phoneme_predictor = PhonemePredictor(track_path, docker_url)
        phoneme_predictor.predictAndSavePhonemes()
    elif execution_mode == TO_VIDEO_MODE:
        video_generator = VideoGenerator(track_path)
        video_generator.generateAndSaveVideo()


if __name__ == "__main__":
    main()
