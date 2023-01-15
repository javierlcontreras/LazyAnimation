import argparse
import os
from video_generator import *
import requests

ART_PATHS = {
	"POSES": "art/poses",
	"FONTS": "art/fonts",
	"MOUTHS": "art/mouths"
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

	video_generator = VideoGenerator(track_path, docker_url, ART_PATHS)
	video_generator.generateVideo() 

if __name__ == "__main__":
	main()