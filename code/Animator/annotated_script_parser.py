class AnnotatedScriptParser:
	def __init__(self, track_path):
		self.track_path = track_path

	def validTrackLine(self, track_line):
		if track_line.count("{") != 1: return ">{"
		if track_line.count("}") != 1: return ">}"
		if track_line.count("[") != 1: return ">["
		if track_line.count("]") != 1: return ">]"
		parts = track_line.split("}")
		if parts[0].count("{") != 1 or parts[0][0] != "{": return "{ incorrect in part 1"
		if parts[1].count("[") != 1 or parts[1][0] != "[": return "[ incorrect in part 2"
		if parts[1].count("]") != 1 or parts[1][-1] != "]": return "] incorrect in part 2"
		if parts[1].count(";") != 1: return "; incorrect in part 2"
		delta_time = parts[1][1:-1].split(";")[0]
		try:
			float(delta_time)
		except ValueError:
			return "float error in part 2"
		return ""

	def parseTrackLineInfo(self, track_line):
		parts = track_line.split("}")
		text = parts[0][1:]
		tags = parts[1][1:-1].split(";")
		delta_time = float(tags[0])
		return {"text": text, "delta_time": delta_time, "mood": tags[1]}

	def parseAnnotatedScript(self):
		track_raw = []
		with open(f"{self.track_path}.txt", "r") as reader:
			track_raw = reader.read()

		track_info = []
		track_lines = track_raw.split("\n")
		if track_lines[-1].strip(" ") == "": 
			track_lines = track_lines[:-1]
		for track_line in track_lines:
			track_line = track_line.strip(" ")
			err = self.validTrackLine(track_line)
			if err != "":
				print(f"Invalid line {track_line} with error {err}, skipping it")
				print("Valid format is {text}[time;mood]")
				continue
			track_line_info = self.parseTrackLineInfo(track_line)
			track_info.append(track_line_info)
		return track_info


	def unnanotateAndSaveScriptForGentle(self, track_info):
		with open(f"{self.track_path}_gentle.txt", "w") as writer:
			for track_info_line in track_info:
				writer.write(track_info_line["text"] + "\n") 