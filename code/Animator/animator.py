import argparse
import os
from video_generator import *
import requests

ART_PATHS = {
	"POSES": "art/poses",
	"FONTS": "art/fonts",
	"MOUTHS": "art/mouths",
	"EYES": "art/eyes"
}

VIDEO_SETTINGS = {
	"FPS": 24,
	"WIDTH": 1920,
	"HEIGHT": 1080,
	"BLINKING_SPACE_TIME": 3,
	"BLINKING_ACTION_TIME": 0.1
}

LAZYKH_IMAGE_INDEXING = {
	'EMOTION_INDEX': {
		'explain': 0,
		'happy': 1,
		'sad': 2,
		'angry': 3,
		'confused': 4,
		'rq': 5,
	},
	'EMOTION_POSITIVITY': {
		'explain': False,
		'happy': True,
		'sad': False,
		'angry': False,
		'confused': False,
		'rq': True,
	},
	'PHONEME_TO_MOUTH': {
		"aa": "a",
		"ae": "a",
		"ah": "a",
		"ao": "a",
		"aw": "au",
		"ay": "ay",
		"b": "m",
		"ch": "t",
		"d": "t",
		"dh": "t",
		"eh": "a",
		"er": "u",
		"ey": "ay",
		"f": "f",
		"g": "t",
		"hh": "y",
		"ih": "a",
		"iy": "ay",
		"jh": "t",
		"k": "t",
		"l": "y",
		"m": "m",
		"n": "t",
		"ng": "t",
		"ow": "au",
		"oy": "ua",
		"p": "m",
		"r": "u",
		"s": "t",
		"sh": "t",
		"t": "t",
		"th": "t",
		"uh": "u",
		"uw": "u",
		"v": "f",
		"w": "u",
		"y": "y",
		"z": "t",
		"zh": "t",
		"empty": "m" # For unknown phonemes, the stick figure will just have a closed mouth ("mmm")
	},
	'MOUTH_TO_INDEX': {
		'y': 0, 
		'a': 5, # 4 
		't': 6, 
		'f': 7, 
		'm': 8, 
		'u': 10, # 9
	}
}

def parseTrackPathFromArguments():
	parser = argparse.ArgumentParser(description='Annotated text to Animation')
	parser.add_argument('--track_path', 
						dest='track_path', 
						type=str, 
						help='Path of the track without file extensions',
						required=True)
	parser.add_argument('--docker_port',
						type=int, 
						help='Real machine port of Gentle docker service',
						required=True)

	args = parser.parse_args()
	track_path = args.track_path
	docker_port = args.docker_port
	docker_url = f"http://0.0.0.0:{docker_port}/transcriptions"


	if not os.path.exists(f"{track_path }.txt"):
		raise "track_path.txt doesn't exist"

	if not os.path.exists(f"{track_path}.aac"):
		raise "track_path.acc doesn't exist"

	try:
		head = requests.get(docker_url)
	except ConnectionRefusedError as e:
		raise "docker_port is not responding to HTTP requests"
	
	return track_path, docker_url

def main():
	track_path, docker_url = parseTrackPathFromArguments()
	
	print(f"Starting animator on track: {track_path}")

	video_generator = VideoGenerator(track_path, docker_url, ART_PATHS, VIDEO_SETTINGS, LAZYKH_IMAGE_INDEXING)
	video_generator.generateVideo() 

if __name__ == "__main__":
	main()