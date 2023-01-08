import argparse
import os
from video_generator import *

MOOD_IMG_PATH = "mood_images"

def parseTrackPathFromArguments():
	parser = argparse.ArgumentParser(description='Annotated text to Animation')
	parser.add_argument('--track_path', 
						dest='track_path', 
						type=str, 
						help='Path of the track without file extensions',
						required=True)
	args = parser.parse_args()
	track_path = args.track_path

	if not os.path.exists(f"{track_path }.txt"):
		print(f"Annotated text file \"{track_path}.txt\" does not exist")
		return None
	if not os.path.exists(f"{track_path}.aac"):
		print(f"Audio file \"{track_path}.aac\" does not exist")
		return None

	return track_path

def main():
	track_path = parseTrackPathFromArguments()
	if track_path == None:
		return

	print(f"Starting animator on track: {track_path}")

	video_generator = VideoGenerator(track_path, MOOD_IMG_PATH)
	video_generator.generateVideo() 

if __name__ == "__main__":
	main()