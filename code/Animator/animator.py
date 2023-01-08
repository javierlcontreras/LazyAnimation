import argparse
import os
from video_generator import *

DATA_FILES_PATH = "data_files"
MOOD_IMG_PATH = "mood_images"

def validTrackLine(track_line):
	if track_line.count("{") != 1: return False
	if track_line.count("}") != 1: return False
	if track_line.count("[") != 1: return False
	if track_line.count("]") != 1: return False
	parts = track_line.split("}")
	if parts[0].count("{") != 1 or parts[0][0] != "{": return False
	if parts[1].count("[") != 1 or parts[1][0] != "[": return False
	if parts[1].count("]") != 1 or parts[1][-1] != "]": return False
	if parts[1].count(";") != 1: return False
	delta_time = parts[1][1:-1].split(";")[0]
	try:
		float(delta_time)
	except ValueError:
		return False
	return True

def parseTrackLineInfo(track_line):
	parts = track_line.split("}")
	text = parts[0][1:]
	tags = parts[1][1:-1].split(";")
	delta_time = float(tags[0])
	return {"text": text, "delta_time": delta_time, "mood": tags[1]}

def parseAnnotatedScript(track_name):
	track_raw = []
	with open(f"{DATA_FILES_PATH}/{track_name}.txt", "r") as reader:
		track_raw = reader.read()

	track_info = []
	track_lines = track_raw.split("\n")
	if track_lines[-1].strip(" ") == "": 
		track_lines = track_lines[:-1]
	for track_line in track_lines:
		track_line = track_line.strip(" ")
		if not validTrackLine(track_line):
			print(f"Invalid line {track_line}, skipping it")
			continue
		track_line_info = parseTrackLineInfo(track_line)
		track_info.append(track_line_info)
	return track_info


def parseTrackNameFromArguments():
	parser = argparse.ArgumentParser(description='Annotated text to Animation')
	parser.add_argument('--track_name', 
						dest='track_name', 
						type=str, 
						help='Name of the track',
						required=True)
	args = parser.parse_args()
	track_name = args.track_name

	if not os.path.exists(f"{DATA_FILES_PATH}/{track_name}.txt"):
		print(f"Annotated text file \"{DATA_FILES_PATH}/{track_name}.txt\" does not exist")
		return None
	if not os.path.exists(f"{DATA_FILES_PATH}/{track_name}.aac"):
		print(f"Audio file \"{DATA_FILES_PATH}/{track_name}.aac\" does not exist")
		return None

	return track_name 


def main():
	track_name = parseTrackNameFromArguments()
	if track_name == None:
		return

	print(f"Starting animator on track: {track_name}")
	track_info = parseAnnotatedScript(track_name)
	
	video_generator = VideoGenerator(track_name, track_info, MOOD_IMG_PATH, DATA_FILES_PATH)
	video_generator.generateVideo() 

if __name__ == "__main__":
	main()