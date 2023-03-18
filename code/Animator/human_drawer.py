import cv2
import os
import numpy as np
import array

from pydub import AudioSegment
from pydub.utils import get_array_type
from PIL import ImageFont, ImageDraw, Image

import requests

from configuration_constants import ART_PATHS


class HumanDrawer:
    def __init__(self):
        pass

    def _addImage(self, image, added_image):
        pillow_empty = Image.new("RGBA", image.size)
        (w, h) = added_image.size
        (W, H) = image.size
        position = (int(W / 2 - w / 2), int(H / 2 - h / 2))
        pillow_empty.paste(added_image, position, mask=added_image)
        return Image.alpha_composite(image, pillow_empty)

    def _addPart(self, image, part_path):
        return self._addImage(image, Image.open(part_path)).convert('RGBA')

    def draw(self, hands, mouth, eyes, eyebrows):
        body_path = ART_PATHS["BODY_IMAGE"]
        body = Image.open(body_path)
        image = Image.new('RGBA', body.size, (0, 0, 0, 0))

        image = self._addImage(image, body)
        image = self._addPart(image, ART_PATHS["FACE_IMAGE"])
        image = self._addPart(image, ART_PATHS["HANDS"] + "/" + hands + ".png")
        image = self._addPart(image, ART_PATHS["MOUTHS"] + "/" + mouth + ".png")
        image = self._addPart(image, ART_PATHS["EYEBROWS"] + "/" + eyebrows + ".png")
        image = self._addPart(image, ART_PATHS["EYES"] + "/" + eyes + ".png")
        image = self._addPart(image, ART_PATHS["HAIR_IMAGE"])

        return image
