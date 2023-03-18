TO_GENTLE_MODE = "to_gentle"
TO_VIDEO_MODE = "to_video"
VALID_EXECUTION_MODES = [TO_GENTLE_MODE, TO_VIDEO_MODE]

SPRITE_DIRECTORY = "art/sprites"
ART_PATHS = {
    "FONTS": "art/fonts",
    "MOUTHS": f"{SPRITE_DIRECTORY}/mouths",
    "EYEBROWS": f"{SPRITE_DIRECTORY}/eyebrows",
    "HANDS": f"{SPRITE_DIRECTORY}/hands",
    "EYES": f"{SPRITE_DIRECTORY}/eyes",
    "BODY_IMAGE": f"{SPRITE_DIRECTORY}/body/body.png",
    "FACE_IMAGE": f"{SPRITE_DIRECTORY}/face/face.png",
    "HAIR_IMAGE": f"{SPRITE_DIRECTORY}/hair/hair.png",
}

INPUT_AUDIO_TYPE = "aac"
OUTPUT_VIDEO_TYPE = "mp4"

TRACK_PATH_FILES = {
    "ANNOTATED_TRANSCRIPT": ".txt",
    "AUDIO": f".{INPUT_AUDIO_TYPE}",
    "TRANSCRIPT": "_gentle.txt",
    "PHONEME_LIST": "_phonemes.json",
    "PHONEME_LIST_REVIEWED": "_phonemes_reviewed.json",
    "VIDEO": f".{OUTPUT_VIDEO_TYPE}",
    "VIDEO_WITH_AUDIO": f"_audio.{OUTPUT_VIDEO_TYPE}",
}

VIDEO_SETTINGS = {
    "FPS": 24,
    "WIDTH": 2560,
    "HEIGHT": 2560,
    "BLINKING_SPACE_TIME": 3,
    "BLINKING_ACTION_TIME": 0.1,
    "POSE_TIME": 1.5
}

PHONEME_TO_MOUTH = {
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
    "empty": "m",  # For unknown phonemes, the stick figure will just have a closed mouth ("mmm")
    "oov": "m",
    "sil": "m",
    "not-found-in-audio": "m"
}