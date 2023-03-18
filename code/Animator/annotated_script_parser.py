from configuration_constants import ART_PATHS
from PIL import Image


def _parseTrackLineInfo(track_line):
    parts = track_line.split("]")
    tags = parts[0][1:].strip(" ")
    text = parts[1].strip(" ")
    
    hands, eyebrows = "down", "happy"
    if "," in tags:
        hands, eyebrows = tags.split(",")
        hands = hands.strip(" ")
        eyebrows = eyebrows.strip(" ")
    else:
        hands = tags

    try:
        Image.open(ART_PATHS["HANDS"] + "/" + hands + ".png")
        Image.open(ART_PATHS["EYEBROWS"] + "/" + eyebrows + ".png")
    except FileNotFoundError:
        raise "using non-existing tags!"
    return {"text": text, "hands": hands, "eyebrows": eyebrows}


def _validTrackLine(track_line):
    print(track_line)
    if track_line.count("[") != 1: return ">["
    if track_line.count("]") != 1: return ">]"
    parts = track_line.split("]")
    if parts[0].count("[") != 1 or parts[0][0] != "[": return "[ incorrect in part 1"
    if parts[0].count(",") >= 2: return "too many tags, max is 2"
    return ""


class AnnotatedScriptParser:
    def __init__(self, track_path):
        self.track_path = track_path

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
            if track_line == "": continue
            err = _validTrackLine(track_line)
            if err != "":
                print(f"-----DEBUG INFO: Invalid line {track_line} with error {err}, skipping it")
                print("Valid format is {text}[mood]")
                continue
            track_line_info = _parseTrackLineInfo(track_line)
            track_info.append(track_line_info)
        return track_info

    def unnanotateAndSaveScriptForGentle(self, track_info):
        with open(f"{self.track_path}_gentle.txt", "w") as writer:
            for track_info_line in track_info:
                writer.write(track_info_line["text"] + "\n")
