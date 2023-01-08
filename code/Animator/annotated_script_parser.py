class AnnotatedScriptParser:
	def __init__(self, track_path):
		self.track_path = track_path

	def validTrackLine(self, track_line):
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
			if not self.validTrackLine(track_line):
				print(f"Invalid line {track_line}, skipping it")
				continue
			track_line_info = self.parseTrackLineInfo(track_line)
			track_info.append(track_line_info)
		return track_info
